# rag-knowledge-base

> A small but **real** Retrieval-Augmented Generation (RAG) system over a document knowledge base — with a pure-Python vector store, local embeddings, source citations, and an evaluation harness. No external database required.

![python](https://img.shields.io/badge/python-3.9%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)
![tests](https://img.shields.io/badge/tests-pytest-brightgreen)
![vector store](https://img.shields.io/badge/vector%20store-pure%20NumPy-orange)

Ask natural-language questions about a set of documents and get answers **grounded in those
documents**, with the sources cited. The knowledge base here is the internal engineering
documentation of a fictional company, *Meridian Data Co.* — using a fictional company is
deliberate: the LLM couldn't have memorized any of it, so a correct answer **proves retrieval
is doing the work**, not the model guessing from training.

```
$ python -m rag_kb ask "How long is bronze layer data kept before it's deleted?"

ANSWER:
Bronze layer raw data is retained for 13 months in total — 30 days in Cloud Storage
Standard, 90 days in Nearline, then Coldline until the 13-month mark, after which it is
permanently deleted by an automated lifecycle rule. (source: 03_data_retention_policy.md)

SOURCES:
  - 03_data_retention_policy.md  (relevance 0.71)
  - 02_platform_architecture.md  (relevance 0.44)
```

---

## Why this project is worth a look

- **It's a complete RAG pipeline**, not a snippet: loading → chunking → embedding → a vector
  store → retrieval → grounded generation → citations → evaluation.
- **The vector store is pure NumPy** — no pgvector, FAISS, or Pinecone to set up. You can read
  the ~15 lines that *are* "vector search" and see there's no magic (`vector_store.py`).
- **Embeddings run locally** via a small `sentence-transformers` model — free, offline, no API
  key for the retrieval half.
- **Answers are grounded and cited**, with two guardrails that stop hallucination: *answer only
  from the retrieved context*, and *say "I don't know" if it isn't there*.
- **It's measured, not vibes** — an evaluation harness scores retrieval hit-rate against a set
  of question/expected-source pairs, so you can tell whether a change (chunk size, top-k) helped.
- **It runs with no API key** for indexing, retrieval, and retrieval-evaluation. Only the final
  answer-generation step calls an LLM.

---

## Architecture

```
                    INDEXING  (Phase A — run once, offline, no API key)
  knowledge_base/*.md  ──►  chunk  ──►  embed (local model)  ──►  NumPy vector store  ──►  index/
                                                                                             │
                    QUERYING  (Phase B — per question)                                       │
  "your question"  ──►  embed  ──►  search (cosine top-k)  ◄──────────────────────────────────┘
                                        │
                                        ▼
                     retrieved chunks ──►  build grounded prompt  ──►  Claude  ──►  cited answer
```

Every stage maps to a module (and to the RAG handbook this was built from):

| Module | Stage | RAG concept |
|---|---|---|
| `loader.py` | load documents | — |
| `chunker.py` | split into overlapping chunks | Part 6 (chunking) |
| `embeddings.py` | text → meaning-vector | Part 3 (embeddings) |
| `vector_store.py` | store vectors, cosine top-k search | Parts 4–5 (vector search) |
| `indexer.py` | Phase A orchestration | Part 5 (indexing) |
| `retriever.py` | embed question, fetch top-k | Parts 4–5 (retrieval) |
| `generator.py` | grounded prompt + LLM call | Part 7 (augment + generate) |
| `pipeline.py` | retrieve → augment → generate | Part 8 (end-to-end) |
| `evaluate.py` | retrieval hit-rate on an eval set | Part 9 (evaluation) |

---

## Quickstart

```bash
git clone https://github.com/<you>/rag-knowledge-base.git
cd rag-knowledge-base
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev,embeddings]"                      # 'embeddings' installs the local model deps
```

**1. Build the index** (Phase A — no API key; downloads a ~80 MB embedding model on first run):
```bash
python -m rag_kb index
```

**2. Add your Anthropic key** (only needed to generate answers):
```bash
cp .env.example .env        # then edit .env and paste your key
export ANTHROPIC_API_KEY=sk-ant-...
```

**3. Ask questions:**
```bash
python -m rag_kb ask "What are the response time targets for a SEV1 incident?"
python -m rag_kb ask "How is PII handled at ingestion?" --show-chunks
```

**4. Evaluate retrieval quality** (no API key needed):
```bash
python -m rag_kb eval                 # retrieval hit-rate on the eval set
python -m rag_kb eval --check-answers  # also grades answers (needs API key)
```

### No API key? No model download? Still runs.
Every command accepts `--embedder hashing` (a deterministic, non-semantic fallback needing no
model) and `ask` accepts `--mock-llm` (fakes the answer from the top chunk). This is what CI uses:
```bash
python -m rag_kb index --embedder hashing
python -m rag_kb ask "..." --embedder hashing --mock-llm --show-chunks
python -m rag_kb eval --embedder hashing
```

---

## Try these questions

The knowledge base has real, specific facts to retrieve. Good demo questions:

- "Within how many days must a customer data erasure request be completed?"
- "What does it mean for a pipeline to be idempotent at Meridian?"
- "Where are secrets stored and how are they referenced by pipelines?"
- "What is the medallion architecture and what are its layers?"
- "How does a new engineer get production data access?"

And a question the docs **don't** answer, to see the guardrail work:
- "What is Meridian's revenue?" → *"I don't have that information in the knowledge base."*

---

## Run the tests

```bash
pytest -q
```
All tests are offline (hashing embedder, no API key, no model download) and run in CI on every push.

---

## Project layout

```
rag-knowledge-base/
├── knowledge_base/          # 7 source documents (the corpus)
├── src/rag_kb/
│   ├── config.py            # all tunables: chunk size, top_k, model names
│   ├── loader.py chunker.py embeddings.py vector_store.py
│   ├── indexer.py retriever.py generator.py pipeline.py evaluate.py
│   └── cli.py __main__.py   # `index` / `ask` / `eval`
├── eval/eval_set.json       # questions + expected source docs
├── tests/test_rag.py        # offline unit tests
├── .github/workflows/ci.yml
└── pyproject.toml requirements.txt LICENSE .gitignore .env.example
```

---

## Design notes & honest limitations

- **Pure-NumPy vector store.** Brute-force cosine search is instant at this corpus size and keeps
  the mechanics visible. At millions of vectors you'd swap in FAISS or pgvector — the
  `add / search / save / load` interface would stay the same. That swap is the natural next step.
- **The hashing embedder is not semantic.** It exists only so tests/CI run with zero heavy deps or
  network. It matches on token overlap, so it can rank a keyword-heavy but less-relevant chunk
  first. Real retrieval quality comes from the `sentence-transformers` embedder (the default when
  installed) — install it for the intended experience.
- **Evaluation is retrieval-first.** Retrieval hit-rate (did we fetch a correct source in the
  top-k?) is measured with no API key, because retrieval is what determines whether RAG *can*
  answer. Answer-keyword grading (`--check-answers`) is a lightweight extra signal, not a full
  RAGAS-style eval.
- **SDK compatibility.** The generator passes `temperature=0` for deterministic answers and
  transparently retries without it on Anthropic SDK v1.0+ (which removed that argument).

## Roadmap

- [ ] Swap the NumPy store for **pgvector** (same interface, real database)
- [ ] Add **hybrid search** (semantic + keyword) for exact terms like IDs and error codes
- [ ] Add a **reranker** second pass for higher precision
- [ ] Richer evaluation (faithfulness / RAGAS-style answer grading)
- [ ] A minimal web UI

## License

MIT — see [LICENSE](LICENSE).
