"""Central configuration for the RAG system.

Keeping every tunable in one place makes the system easy to reason about and to experiment
with — change a value here, re-index, and measure the effect with the eval command.
"""

from pathlib import Path

# --- Paths ------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]        # repo root
KB_DIR = ROOT / "knowledge_base"                   # source .md documents
INDEX_DIR = ROOT / "index"                         # generated vector index (gitignored)
EVAL_FILE = ROOT / "eval" / "eval_set.json"        # evaluation questions

# --- Chunking (see the RAG handbook, Part 6) --------------------------------
# Chunks are split on paragraph boundaries, then packed up to CHUNK_SIZE characters,
# with CHUNK_OVERLAP characters carried over so an idea on a boundary isn't lost.
CHUNK_SIZE = 900          # ~150-180 words; a coherent paragraph or two
CHUNK_OVERLAP = 150       # ~15% overlap between consecutive chunks

# --- Embeddings (Part 3) ----------------------------------------------------
# Default: a small local sentence-transformers model — free, offline, no API key,
# runs on CPU. Falls back to a deterministic hashing embedder if the library isn't
# installed (used by tests/CI so they need no model download or network).
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"   # 384-dimensional vectors
EMBED_DIM_FALLBACK = 384                                  # hashing embedder dimension

# --- Retrieval (Parts 4-5) --------------------------------------------------
TOP_K = 4                 # how many chunks to retrieve per question

# --- Generation (Part 7) ----------------------------------------------------
# The LLM only runs in the `ask` command; indexing and retrieval need no API key.
LLM_MODEL = "claude-haiku-4-5-20251001"   # verify current model names in the Anthropic docs
LLM_MAX_TOKENS = 500
