"""The vector store (RAG handbook, Parts 4-5): hold chunks + their vectors, and find the
nearest ones to a query vector.

This is a pure-NumPy implementation — no external database. It is the same idea a vector
database (pgvector, FAISS, Pinecone) implements, kept deliberately visible so you can see
exactly what "vector search" is: a cosine-similarity sort. Because all vectors are
L2-normalized by the embedder, cosine similarity is just a dot product, so a whole search is
one matrix-vector multiply.

For this knowledge-base-sized corpus a brute-force NumPy search is instant. At millions of
vectors you'd swap this class for FAISS or pgvector — but the interface (add / search / save /
load) would stay the same.
"""

import json
from pathlib import Path

import numpy as np


class VectorStore:
    def __init__(self):
        self.vectors = None          # np.ndarray (n_chunks, dim)
        self.chunks = []             # list of chunk dicts (parallel to rows of self.vectors)

    def add(self, chunks, vectors):
        """Add chunk dicts and their (already-normalized) vectors."""
        vectors = np.asarray(vectors, dtype=np.float32)
        self.vectors = vectors if self.vectors is None else np.vstack([self.vectors, vectors])
        self.chunks.extend(chunks)

    def search(self, query_vector, k=4):
        """Return the top-k chunks nearest to query_vector, each with a similarity score.

        Because vectors are L2-normalized, similarity = dot product = cosine similarity.
        This single line is the whole 'vector database' — an ORDER BY on closeness.
        """
        if self.vectors is None or len(self.chunks) == 0:
            return []
        q = np.asarray(query_vector, dtype=np.float32).reshape(-1)
        scores = self.vectors @ q                      # cosine similarity to every chunk
        top_idx = np.argsort(scores)[::-1][:k]         # indices of the k highest scores
        results = []
        for i in top_idx:
            chunk = dict(self.chunks[int(i)])
            chunk["score"] = float(scores[int(i)])
            results.append(chunk)
        return results

    def __len__(self):
        return len(self.chunks)

    # --- persistence: save/load the index so you don't re-embed every run ---
    def save(self, index_dir: Path):
        index_dir.mkdir(parents=True, exist_ok=True)
        np.save(index_dir / "vectors.npy", self.vectors)
        with open(index_dir / "chunks.jsonl", "w", encoding="utf-8") as f:
            for chunk in self.chunks:
                f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    @classmethod
    def load(cls, index_dir: Path):
        store = cls()
        vectors_path = index_dir / "vectors.npy"
        chunks_path = index_dir / "chunks.jsonl"
        if not vectors_path.exists() or not chunks_path.exists():
            raise FileNotFoundError(
                f"No index found in {index_dir}. Run `python -m rag_kb index` first."
            )
        store.vectors = np.load(vectors_path)
        with open(chunks_path, encoding="utf-8") as f:
            store.chunks = [json.loads(line) for line in f]
        return store
