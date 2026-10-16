"""Streamlit web UI:  streamlit run app.py"""
import streamlit as st

from src import config
from src.ingestion import ingest_files
from src.rag_chain import RAGChatbot
from src.vector_store import reset_vectorstore

st.set_page_config(page_title="RAG Chatbot", page_icon="📚")
st.title("📚 Chat with your documents")

if "bot" not in st.session_state:
    st.session_state.bot = RAGChatbot()
    st.session_state.messages = []

with st.sidebar:
    st.header("Documents")
    files = st.file_uploader(
        "Upload PDF, DOCX, TXT or Excel",
        type=[e.strip(".") for e in config.SUPPORTED_EXTENSIONS],
        accept_multiple_files=True,
    )
    if st.button("Index documents") and files:
        config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        paths = []
        for f in files:
            p = config.UPLOAD_DIR / f.name
            p.write_bytes(f.getbuffer())
            paths.append(p)
        with st.spinner("Embedding and indexing..."):
            result = ingest_files(paths)
        st.success(f"Indexed {result['chunks_indexed']} chunks")
        for name, err in result["failed"].items():
            st.error(f"{name}: {err}")

    if st.button("Clear chat"):
        st.session_state.bot.clear_history()
        st.session_state.messages = []
    if st.button("Delete all indexed data"):
        reset_vectorstore()
        st.session_state.bot = RAGChatbot()
        st.warning("Vector database cleared.")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if question := st.chat_input("Ask a question about your documents"):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer, docs = st.session_state.bot.ask(question)
        st.markdown(answer)
        with st.expander("Sources"):
            for d in docs:
                meta = ", ".join(f"{k}={v}" for k, v in d.metadata.items())
                st.caption(meta)
                st.text(d.page_content[:300] + "...")
    st.session_state.messages.append({"role": "assistant", "content": answer})
