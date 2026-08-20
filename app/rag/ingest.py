import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import CHROMA_DIR, POLICY_DIR
from app.rag.embedding import configure_embedding_cache


configure_embedding_cache()


def load_policy_files() -> list[tuple[str, str]]:
    """Returns list of (filename, text) - one entry per policy doc."""
    return [
        (f.name, f.read_text(encoding="utf-8"))
        for f in sorted(POLICY_DIR.glob("*.md"))
    ]


def split_policy(text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )
    return splitter.split_text(text)


def ingest() -> None:
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(name="support_policies")

    all_docs, all_metas, all_ids = [], [], []

    for filename, text in load_policy_files():
        chunks = split_policy(text)
        for i, chunk in enumerate(chunks):
            all_docs.append(chunk)
            all_metas.append({"source": filename})
            all_ids.append(f"{filename}-{i}")

    collection.upsert(ids=all_ids, documents=all_docs, metadatas=all_metas)
