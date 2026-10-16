# Suggested commit sequence (use these as meaningful commit messages)
1. chore: initialise project structure, .gitignore and requirements
2. feat(config): add central configuration and .env support
3. feat(ingestion): add PDF, DOCX and TXT loaders
4. feat(ingestion): add Excel loader with row-wise serialisation
5. feat(vector-store): integrate HuggingFace embeddings and ChromaDB persistence
6. feat(ingestion): add chunking and idempotent indexing with hashed IDs
7. feat(rag): add MMR retriever and grounded QA prompt
8. feat(rag): add history-aware question condensing and LLM provider factory
9. feat(ui): add Streamlit chat interface with source display
10. feat(cli): add command-line ingest and chat
11. docs: add README with installation and usage
12. docs: add technical documentation with architecture, flow and state diagrams
13. docs: add experimental results and screenshots
