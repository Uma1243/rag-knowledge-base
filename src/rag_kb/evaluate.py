"""Evaluation (RAG handbook, Part 9): measure whether retrieval fetches the right documents.

This is regression testing for retrieval — the data-quality mindset applied to RAG. For every
question in the eval set, we check whether an expected source document appears among the
top-k retrieved chunks (retrieval hit-rate). This runs with NO API key, because retrieval is
the half that determines whether RAG can possibly answer correctly.

Optionally (with --check-answers and an API key) it also runs generation and checks whether the
answer contains expected keywords — a lightweight answer-quality signal.
"""

import json

from .config import EVAL_FILE, TOP_K
from .retriever import Retriever
from .generator import generate


def evaluate(index_dir=None, k=TOP_K, check_answers=False, prefer_embedder="auto", log=print):
    data = json.loads(EVAL_FILE.read_text(encoding="utf-8"))
    questions = data["questions"]

    retriever = Retriever(**({"index_dir": index_dir} if index_dir else {}),
                          prefer_embedder=prefer_embedder)

    retrieval_hits = 0
    answer_hits = 0
    log(f"Evaluating {len(questions)} questions (top_k={k})\n")

    for q in questions:
        chunks = retriever.retrieve(q["question"], k=k)
        got_sources = {c["source"] for c in chunks}
        expected = set(q["expected_sources"])
        hit = bool(got_sources & expected)          # did we retrieve any expected source?
        retrieval_hits += hit
        mark = "ok " if hit else "MISS"
        log(f"  [{mark}] retrieval | {q['question'][:60]}")
        if not hit:
            log(f"         expected one of {sorted(expected)}, got {sorted(got_sources)}")

        if check_answers:
            ans = generate(q["question"], chunks, use_mock=False).lower()
            needed = [w.lower() for w in q.get("answer_contains", [])]
            ok = all(w in ans for w in needed) if needed else True
            answer_hits += ok
            log(f"         answer {'ok' if ok else 'WEAK'} (wanted: {q.get('answer_contains')})")

    n = len(questions)
    log(f"\nRetrieval hit-rate: {retrieval_hits}/{n} = {retrieval_hits/n:.0%}")
    if check_answers:
        log(f"Answer keyword-match: {answer_hits}/{n} = {answer_hits/n:.0%}")
    return {"n": n, "retrieval_hits": retrieval_hits,
            "answer_hits": answer_hits if check_answers else None}
