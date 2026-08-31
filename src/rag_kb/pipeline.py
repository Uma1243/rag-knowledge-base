"""The end-to-end RAG query: retrieve -> augment -> generate (RAG handbook, Part 8).

`answer()` returns both the generated answer and the sources it was grounded in, so callers
can show citations — a core trust feature of a good RAG system.
"""

from .retriever import Retriever
from .generator import generate
from .config import TOP_K


class RagPipeline:
    def __init__(self, index_dir=None, prefer_embedder="auto"):
        kwargs = {"prefer_embedder": prefer_embedder}
        if index_dir is not None:
            kwargs["index_dir"] = index_dir
        self.retriever = Retriever(**kwargs)

    def answer(self, question, k=TOP_K, use_mock_llm=False):
        chunks = self.retriever.retrieve(question, k=k)          # RETRIEVE
        text = generate(question, chunks, use_mock=use_mock_llm)  # AUGMENT + GENERATE
        sources = []
        seen = set()
        for c in chunks:
            if c["source"] not in seen:
                seen.add(c["source"])
                sources.append({"source": c["source"], "score": round(c["score"], 3)})
        return {"answer": text, "sources": sources, "chunks": chunks}
