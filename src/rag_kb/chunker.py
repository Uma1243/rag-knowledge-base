"""Chunking step (indexing Phase A, step 2): split documents into retrieval-sized pieces.

Strategy (RAG handbook, Part 6): split on paragraph boundaries first (so we cut on natural
seams, not mid-sentence), then greedily pack paragraphs into chunks up to CHUNK_SIZE
characters, carrying CHUNK_OVERLAP characters from the end of one chunk into the next so an
idea spanning a boundary isn't lost.
"""

import re

from .config import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_documents(docs, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Turn a list of documents into a flat list of chunk dicts with metadata."""
    chunks = []
    for doc in docs:
        for i, piece in enumerate(_chunk_text(doc["text"], chunk_size, overlap)):
            chunks.append({
                "id": f"{doc['source']}::chunk_{i}",
                "source": doc["source"],
                "title": doc["title"],
                "content": piece,
            })
    return chunks


def _chunk_text(text, chunk_size, overlap):
    """Yield overlapping chunks of text, respecting paragraph boundaries where possible."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

    chunks, current = [], ""
    for para in paragraphs:
        # If a single paragraph is huge, hard-split it so no chunk exceeds the size.
        if len(para) > chunk_size:
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(_hard_split(para, chunk_size))
            continue

        if len(current) + len(para) + 2 <= chunk_size:
            current = f"{current}\n\n{para}" if current else para
        else:
            chunks.append(current)
            current = para
    if current:
        chunks.append(current)

    return _apply_overlap(chunks, overlap)


def _hard_split(text, chunk_size):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


def _apply_overlap(chunks, overlap):
    """Prepend the last `overlap` characters of each chunk to the next one."""
    if overlap <= 0 or len(chunks) <= 1:
        return chunks
    out = [chunks[0]]
    for prev, nxt in zip(chunks, chunks[1:]):
        carry = prev[-overlap:]
        out.append(f"{carry} {nxt}")
    return out
