"""Configuration for ChromaDB's local embedding model."""

from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

from app.config import CHROMA_MODEL_CACHE_DIR


def configure_embedding_cache() -> None:
    """Store the downloaded embedding model inside the writable project tree."""
    ONNXMiniLM_L6_V2.DOWNLOAD_PATH = CHROMA_MODEL_CACHE_DIR / ONNXMiniLM_L6_V2.MODEL_NAME
