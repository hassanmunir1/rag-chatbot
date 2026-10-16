"""Document ingestion: load -> split -> embed -> index into ChromaDB."""
import hashlib
from pathlib import Path
from typing import Iterable, List

import pandas as pd
from langchain_community.document_loaders import (
    Docx2txtLoader,
    PyPDFLoader,
    TextLoader,
)
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from . import config
from .vector_store import get_vectorstore


def _load_excel(path: Path) -> List[Document]:
    """Every sheet becomes one Document; each row is rendered as 'col: value'."""
    docs: List[Document] = []
    sheets = pd.read_excel(path, sheet_name=None)  # dict[sheet_name, DataFrame]
    for sheet_name, df in sheets.items():
        df = df.dropna(how="all").fillna("")
        lines = []
        for i, row in df.iterrows():
            cells = [f"{col}: {val}" for col, val in row.items() if str(val) != ""]
            lines.append(f"Row {i + 2} | " + " | ".join(cells))
        if lines:
            docs.append(
                Document(
                    page_content="\n".join(lines),
                    metadata={"source": path.name, "sheet": str(sheet_name)},
                )
            )
    return docs


def load_file(path: str | Path) -> List[Document]:
    """Load one file into LangChain Documents based on its extension."""
    path = Path(path)
    ext = path.suffix.lower()
    if ext not in config.SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")

    if ext == ".pdf":
        docs = PyPDFLoader(str(path)).load()
    elif ext == ".docx":
        docs = Docx2txtLoader(str(path)).load()
    elif ext == ".txt":
        docs = TextLoader(str(path), encoding="utf-8", autodetect_encoding=True).load()
    else:  # .xlsx / .xls
        docs = _load_excel(path)

    for d in docs:
        d.metadata["source"] = path.name
    return docs


def split_documents(docs: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(docs)


def _chunk_id(chunk: Document) -> str:
    raw = chunk.metadata.get("source", "") + chunk.page_content
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def ingest_files(paths: Iterable[str | Path]) -> dict:
    """Ingest files into ChromaDB. Re-ingesting the same file is idempotent."""
    all_chunks: List[Document] = []
    failed = {}
    for p in paths:
        try:
            all_chunks.extend(split_documents(load_file(p)))
        except Exception as exc:  # keep going if one file is broken
            failed[str(p)] = str(exc)

    if all_chunks:
        ids = [_chunk_id(c) for c in all_chunks]
        unique = {i: c for i, c in zip(ids, all_chunks)}  # de-dup inside batch
        get_vectorstore().add_documents(
            documents=list(unique.values()), ids=list(unique.keys())
        )
    return {"chunks_indexed": len(all_chunks), "failed": failed}
