"""Indexing — Phase A of RAG (run once, offline, and again whenever documents change).

Pipeline: load documents -> chunk them -> embed each chunk -> store in the vector store ->
persist to disk. This is an ordinary ETL job whose output is a searchable vector index.
"""

from .config import KB_DIR, INDEX_DIR
from .loader import load_documents
from .chunker import chunk_documents
from .embeddings import get_embedder
from .vector_store import VectorStore


def build_index(kb_dir=KB_DIR, index_dir=INDEX_DIR, prefer_embedder="auto", log=print):
    log(f"Loading documents from {kb_dir} ...")
    docs = load_documents(kb_dir)
    log(f"  {len(docs)} documents loaded.")

    log("Chunking ...")
    chunks = chunk_documents(docs)
    log(f"  {len(chunks)} chunks created.")

    embedder = get_embedder(prefer_embedder)
    log(f"Embedding {len(chunks)} chunks with {embedder.name} ...")
    vectors = embedder.embed([c["content"] for c in chunks])

    store = VectorStore()
    store.add(chunks, vectors)
    store.save(index_dir)
    log(f"Index saved to {index_dir} ({len(store)} chunks, dim={vectors.shape[1]}).")
    return store
