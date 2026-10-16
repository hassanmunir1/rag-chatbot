"""Conversational RAG pipeline built with LangChain (LCEL)."""
from typing import List, Tuple

from langchain_core.documents import Document
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from . import config
from .vector_store import get_vectorstore

# ---------- Prompt engineering ----------
CONDENSE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Given the chat history and the user's latest question, rewrite the "
            "latest question as a fully standalone question. Resolve pronouns "
            "and references using the history. Do NOT answer it. If it is "
            "already standalone, return it unchanged.",
        ),
        MessagesPlaceholder("chat_history"),
        ("human", "{question}"),
    ]
)

QA_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant that answers questions using ONLY the "
            "context below, which comes from the user's documents.\n"
            "Rules:\n"
            "1. If the answer is not in the context, say: \"I could not find "
            "this in the provided documents.\" Do not guess.\n"
            "2. Be concise and accurate; use bullet points for lists.\n"
            "3. Mention the source file (and page/sheet if available) you used.\n\n"
            "Context:\n{context}",
        ),
        MessagesPlaceholder("chat_history"),
        ("human", "{question}"),
    ]
)


def get_llm():
    """Return a chat model for the provider chosen in .env."""
    provider = config.LLM_PROVIDER
    if provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=config.LLM_MODEL,
            base_url=config.OLLAMA_BASE_URL,
            temperature=0,
        )
    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(model=config.LLM_MODEL, temperature=0)
    if provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=config.LLM_MODEL, temperature=0)
    raise ValueError(f"Unknown LLM_PROVIDER: {provider}")


def format_docs(docs: List[Document]) -> str:
    parts = []
    for d in docs:
        m = d.metadata
        loc = m.get("source", "unknown")
        if "page" in m:
            loc += f", page {m['page'] + 1}"
        if "sheet" in m:
            loc += f", sheet '{m['sheet']}'"
        parts.append(f"[Source: {loc}]\n{d.page_content}")
    return "\n\n---\n\n".join(parts)


class RAGChatbot:
    """Holds chat history and runs: condense -> retrieve -> generate."""

    def __init__(self) -> None:
        llm = get_llm()
        self._condense = CONDENSE_PROMPT | llm | StrOutputParser()
        self._answer = QA_PROMPT | llm | StrOutputParser()
        self.history: List[BaseMessage] = []

    def _retriever(self):
        # built per call so newly ingested documents are visible immediately
        return get_vectorstore().as_retriever(
            search_type="mmr",
            search_kwargs={"k": config.TOP_K, "fetch_k": config.TOP_K * 4},
        )

    def ask(self, question: str) -> Tuple[str, List[Document]]:
        recent = self.history[-2 * config.MAX_HISTORY_TURNS :]

        standalone = (
            self._condense.invoke({"chat_history": recent, "question": question})
            if recent
            else question
        )
        docs = self._retriever().invoke(standalone)

        if not docs:
            reply = "No documents are indexed yet. Please upload some files first."
        else:
            reply = self._answer.invoke(
                {
                    "context": format_docs(docs),
                    "chat_history": recent,
                    "question": question,
                }
            )

        self.history.extend([HumanMessage(question), AIMessage(reply)])
        return reply, docs

    def clear_history(self) -> None:
        self.history = []
