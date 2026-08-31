"""Convenience helpers used by the Streamlit app.

Keeps app logic thin: check whether an index exists, build it on demand, and detect
whether an Anthropic API key is available so the UI can enable/disable real answers.
"""

import os

from .config import INDEX_DIR, KB_DIR
from .indexer import build_index


def index_exists(index_dir=INDEX_DIR) -> bool:
    return (index_dir / "vectors.npy").exists() and (index_dir / "chunks.jsonl").exists()


def ensure_index(prefer_embedder="auto", log=print):
    """Build the index if it doesn't already exist. Returns True if a build happened."""
    if index_exists():
        return False
    log("No index found — building it now (first run only)...")
    build_index(prefer_embedder=prefer_embedder, log=log)
    return True


def has_api_key() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def list_documents():
    """Return the source document filenames that make up the knowledge base."""
    return sorted(p.name for p in KB_DIR.glob("*.md")) + sorted(p.name for p in KB_DIR.glob("*.txt"))
