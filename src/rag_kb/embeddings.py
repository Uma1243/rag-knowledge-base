"""Embedding step (indexing Phase A, step 3 & querying step 1): turn text into meaning-vectors.

Two embedders (RAG handbook, Part 3):

* SentenceTransformerEmbedder — the real one. A small local model (all-MiniLM-L6-v2) that
  produces genuine semantic vectors, runs on CPU, needs no API key. The model (~80 MB) is
  downloaded once on first use.

* HashingEmbedder — a deterministic, dependency-free fallback used by tests/CI (and if
  sentence-transformers isn't installed). It does NOT capture meaning — it just hashes tokens
  into a vector — so retrieval quality with it is poor. Its only job is to let the plumbing
  run and be tested offline with no model download.

`get_embedder()` picks the real one if available, else warns and falls back.
"""

import sys
import hashlib

import numpy as np

from .config import EMBED_MODEL, EMBED_DIM_FALLBACK


class SentenceTransformerEmbedder:
    """Real semantic embeddings via a local sentence-transformers model."""

    def __init__(self, model_name=EMBED_MODEL):
        from sentence_transformers import SentenceTransformer  # imported lazily
        self.model = SentenceTransformer(model_name)
        self.name = model_name
        self.dim = self.model.get_sentence_embedding_dimension()

    def embed(self, texts):
        """texts: list[str] -> np.ndarray of shape (len(texts), dim), L2-normalized."""
        vecs = self.model.encode(
            texts, normalize_embeddings=True, show_progress_bar=False
        )
        return np.asarray(vecs, dtype=np.float32)


class HashingEmbedder:
    """Deterministic fallback. NOT semantic — for offline tests/CI only."""

    def __init__(self, dim=EMBED_DIM_FALLBACK):
        self.dim = dim
        self.name = f"hashing-{dim}"

    def embed(self, texts):
        out = np.zeros((len(texts), self.dim), dtype=np.float32)
        for row, text in enumerate(texts):
            for token in text.lower().split():
                h = int(hashlib.md5(token.encode()).hexdigest(), 16)
                out[row, h % self.dim] += 1.0
            norm = np.linalg.norm(out[row])
            if norm > 0:
                out[row] /= norm            # L2-normalize so dot product == cosine
        return out


def get_embedder(prefer="auto"):
    """Return an embedder. prefer: 'auto' | 'st' | 'hashing'."""
    if prefer == "hashing":
        return HashingEmbedder()
    try:
        return SentenceTransformerEmbedder()
    except Exception as e:                   # library missing or model load failed
        if prefer == "st":
            raise
        print(
            f"[embeddings] sentence-transformers unavailable ({e}); "
            f"falling back to the non-semantic hashing embedder. "
            f"Install it (pip install sentence-transformers) for real retrieval.",
            file=sys.stderr,
        )
        return HashingEmbedder()
