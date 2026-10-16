"""Command-line interface.

  python cli.py ingest data/uploads/*        # index files
  python cli.py chat                         # start chatting
"""
import sys
from pathlib import Path

from src.ingestion import ingest_files
from src.rag_chain import RAGChatbot


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in {"ingest", "chat"}:
        print(__doc__)
        return

    if sys.argv[1] == "ingest":
        files = [Path(p) for p in sys.argv[2:]]
        result = ingest_files(files)
        print(f"Indexed {result['chunks_indexed']} chunks.")
        for f, err in result["failed"].items():
            print(f"FAILED {f}: {err}")
        return

    bot = RAGChatbot()
    print("RAG chatbot ready. Type 'exit' to quit, 'reset' to clear memory.")
    while True:
        q = input("\nYou: ").strip()
        if q.lower() in {"exit", "quit"}:
            break
        if q.lower() == "reset":
            bot.clear_history()
            print("History cleared.")
            continue
        if not q:
            continue
        answer, docs = bot.ask(q)
        print(f"\nBot: {answer}")
        srcs = {(d.metadata.get("source"), d.metadata.get("page")) for d in docs}
        print("Sources:", ", ".join(f"{s}" + (f" p.{p+1}" if p is not None else "") for s, p in srcs))


if __name__ == "__main__":
    main()
