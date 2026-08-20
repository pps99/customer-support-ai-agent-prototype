import chromadb

from app.config import CHROMA_DIR
from app.rag.embedding import configure_embedding_cache


configure_embedding_cache()
client = chromadb.PersistentClient(path=str(CHROMA_DIR))

collection = client.get_or_create_collection(
    name="support_policies"
)


def search_policy(query: str, limit: int = 3):
    result = collection.query(
        query_texts=[query],
        n_results=limit,
        include=["documents", "metadatas", "distances"],
    )

    documents = result["documents"][0]
    metadatas = result["metadatas"][0]
    distances = result["distances"][0]

    results = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):
        results.append({
            "text": document,
            "source": metadata.get("source"),
            "distance": distance,
        })

    return results
