# 📚 RAG Chatbot — LangChain + ChromaDB

A conversational question-answering chatbot that answers **only from your own documents**
using Retrieval-Augmented Generation (RAG).

**Supported formats:** PDF, DOCX, TXT, Excel (.xlsx/.xls)

## Features
- Document ingestion for 4 formats (Excel handled sheet-by-sheet, row-by-row)
- Chunking (`RecursiveCharacterTextSplitter`) + local embeddings (`all-MiniLM-L6-v2`)
- Persistent vector index in **ChromaDB** (idempotent re-ingestion)
- MMR retrieval pipeline
- Prompt engineering: question-condensing prompt + grounded answer prompt
- Multi-turn conversational memory
- Source citations (file / page / sheet)
- Swappable LLM: **Ollama (free, local)**, **Google Gemini**, or **OpenAI**
- Streamlit web UI and a CLI

## Architecture (short)
```
Files -> Loader -> Splitter -> Embeddings -> ChromaDB
Question + history -> Condense -> Retriever (MMR) -> Prompt -> LLM -> Answer + Sources
```
Full diagrams: [`docs/technical_documentation.md`](docs/technical_documentation.md)

## Project structure
```
rag-chatbot/
├── app.py                 # Streamlit UI
├── cli.py                 # Command-line interface
├── requirements.txt
├── .env.example
├── src/
│   ├── config.py          # settings
│   ├── ingestion.py       # load + split + index
│   ├── vector_store.py    # embeddings + ChromaDB
│   └── rag_chain.py       # prompts, LLM factory, RAGChatbot
├── data/uploads/          # uploaded files
└── docs/technical_documentation.md
```

## Installation
Requires **Python 3.10+**.

```bash
git clone <your-repo-url>
cd rag-chatbot
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # Windows: copy .env.example .env
```

### Choose an LLM (edit `.env`)
**Option A — Ollama (free, offline):**
1. Install from https://ollama.com
2. `ollama pull llama3.1`
3. Keep `LLM_PROVIDER=ollama`, `LLM_MODEL=llama3.1`

**Option B — Gemini (free tier):** set `LLM_PROVIDER=gemini`, `LLM_MODEL=<a current Gemini model name>`, `GOOGLE_API_KEY=...`

**Option C — OpenAI:** set `LLM_PROVIDER=openai`, `LLM_MODEL=<model name>`, `OPENAI_API_KEY=...`

> The first run downloads the embedding model (~90 MB) once.

## Run
**Web UI**
```bash
streamlit run app.py
```
Upload files in the sidebar → **Index documents** → ask questions.

**CLI**
```bash
python cli.py ingest data/uploads/report.pdf data/uploads/sheet.xlsx
python cli.py chat
```

## Configuration
| Setting | File | Default |
|---|---|---|
| Chunk size / overlap | `src/config.py` | 1000 / 150 |
| Chunks retrieved (`TOP_K`) | `src/config.py` | 4 |
| History turns | `src/config.py` | 5 |
| Embedding model | `.env` | all-MiniLM-L6-v2 |

## Troubleshooting
- **Connection refused (Ollama):** run `ollama serve` and make sure the model is pulled.
- **"No documents are indexed":** click *Index documents* first.
- **Scanned PDF returns nothing:** it has no text layer; OCR is needed (see Future Improvements).

## License
MIT
