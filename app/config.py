"""Shared filesystem paths and application settings."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
ORDERS_FILE = DATA_DIR / "orders.json"
RUNTIME_DIR = DATA_DIR / "runtime"
ESCALATIONS_FILE = RUNTIME_DIR / "escalations.json"
POLICY_DIR = DATA_DIR / "policies"
CHROMA_DIR = DATA_DIR / "chroma"
CHROMA_MODEL_CACHE_DIR = DATA_DIR / ".cache" / "chroma" / "onnx_models"
MIN_INTENT_CONFIDENCE = 0.65
