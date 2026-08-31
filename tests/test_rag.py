"""Offline unit tests — no API key, no model download (uses the hashing embedder).

Run:  pytest
"""

import numpy as np
import pytest

from rag_kb.chunker import chunk_documents, _chunk_text
from rag_kb.embeddings import HashingEmbedder
from rag_kb.vector_store import VectorStore
from rag_kb.generator import build_prompt


def test_chunking_respects_size_and_overlaps():
    text = "\n\n".join(f"Paragraph number {i} with some words." for i in range(20))
    chunks = _chunk_text(text, chunk_size=120, overlap=20)
    assert len(chunks) > 1
    # No chunk should be absurdly larger than size + overlap slack.
    assert all(len(c) <= 120 + 40 for c in chunks)


def test_chunk_documents_attaches_metadata():
    docs = [{"source": "a.md", "title": "A", "text": "Hello world.\n\nSecond paragraph here."}]
    chunks = chunk_documents(docs, chunk_size=1000, overlap=0)
    assert chunks[0]["source"] == "a.md"
    assert chunks[0]["title"] == "A"
    assert "id" in chunks[0] and chunks[0]["id"].startswith("a.md::chunk_")


def test_hashing_embedder_is_deterministic_and_normalized():
    emb = HashingEmbedder(dim=64)
    v1 = emb.embed(["the quick brown fox"])
    v2 = emb.embed(["the quick brown fox"])
    assert np.allclose(v1, v2)                     # deterministic
    assert v1.shape == (1, 64)
    assert abs(np.linalg.norm(v1[0]) - 1.0) < 1e-5  # L2-normalized


def test_vector_store_search_ranks_by_similarity():
    emb = HashingEmbedder(dim=128)
    chunks = [
        {"id": "1", "source": "s", "title": "t", "content": "annual leave holiday vacation days"},
        {"id": "2", "source": "s", "title": "t", "content": "kubernetes docker container orchestration"},
    ]
    vecs = emb.embed([c["content"] for c in chunks])
    store = VectorStore()
    store.add(chunks, vecs)

    q = emb.embed(["how many holiday vacation days"])[0]
    results = store.search(q, k=2)
    assert results[0]["id"] == "1"                 # the leave chunk should rank first
    assert results[0]["score"] >= results[1]["score"]


def test_vector_store_save_load_roundtrip(tmp_path):
    emb = HashingEmbedder(dim=32)
    chunks = [{"id": "1", "source": "s", "title": "t", "content": "hello"}]
    store = VectorStore()
    store.add(chunks, emb.embed(["hello"]))
    store.save(tmp_path)

    loaded = VectorStore.load(tmp_path)
    assert len(loaded) == 1
    assert loaded.chunks[0]["content"] == "hello"
    assert loaded.vectors.shape == (1, 32)


def test_build_prompt_includes_context_and_question():
    chunks = [{"source": "policy.md", "content": "18 days of leave."}]
    prompt = build_prompt("how many days?", chunks)
    assert "policy.md" in prompt
    assert "18 days of leave." in prompt
    assert "how many days?" in prompt


def test_missing_index_raises_helpful_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        VectorStore.load(tmp_path / "does_not_exist")
