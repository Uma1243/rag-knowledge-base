"""Retrieval — the first half of RAG's query phase (RAG handbook, Parts 4-5).

Embed the user's question with the SAME embedder used at indexing time, then ask the vector
store for the k nearest chunks. Returns the chunks (with similarity scores) that will become
the model's context.
"""

from .config import INDEX_DIR, TOP_K
from .embeddings import get_embedder
from .vector_store import VectorStore


class Retriever:
    def __init__(self, index_dir=INDEX_DIR, prefer_embedder="auto"):
        self.store = VectorStore.load(index_dir)
        self.embedder = get_embedder(prefer_embedder)

    def retrieve(self, question, k=TOP_K):
        query_vec = self.embedder.embed([question])[0]     # embed the QUESTION
        return self.store.search(query_vec, k=k)           # top-k nearest chunks
