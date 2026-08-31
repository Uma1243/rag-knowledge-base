"""Command-line interface: `index`, `ask`, and `eval`.

  python -m rag_kb index                          # build the vector index (no API key)
  python -m rag_kb ask "how long is bronze kept?" # retrieve + generate an answer
  python -m rag_kb ask "..." --show-chunks        # also print the retrieved chunks
  python -m rag_kb ask "..." --mock-llm           # no API key: retrieval + mock answer
  python -m rag_kb eval                            # retrieval hit-rate (no API key)
  python -m rag_kb eval --check-answers            # also grade answers (needs API key)
"""

import argparse
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(prog="rag_kb", description="A small RAG system over a document knowledge base.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_index = sub.add_parser("index", help="build the vector index from knowledge_base/")
    p_index.add_argument("--embedder", choices=["auto", "st", "hashing"], default="auto")

    p_ask = sub.add_parser("ask", help="ask a question")
    p_ask.add_argument("question", help="your question in quotes")
    p_ask.add_argument("--k", type=int, default=None, help="how many chunks to retrieve")
    p_ask.add_argument("--show-chunks", action="store_true", help="print retrieved chunks")
    p_ask.add_argument("--mock-llm", action="store_true", help="skip the API; mock the answer")
    p_ask.add_argument("--embedder", choices=["auto", "st", "hashing"], default="auto")

    p_eval = sub.add_parser("eval", help="measure retrieval quality on the eval set")
    p_eval.add_argument("--k", type=int, default=None)
    p_eval.add_argument("--check-answers", action="store_true", help="also grade answers (needs API key)")
    p_eval.add_argument("--embedder", choices=["auto", "st", "hashing"], default="auto")

    args = parser.parse_args(argv)

    if args.command == "index":
        from .indexer import build_index
        build_index(prefer_embedder=args.embedder)

    elif args.command == "ask":
        from .pipeline import RagPipeline
        from .config import TOP_K
        try:
            pipe = RagPipeline(prefer_embedder=args.embedder)
        except FileNotFoundError as e:
            print(e); sys.exit(1)
        k = args.k or TOP_K
        result = pipe.answer(args.question, k=k, use_mock_llm=args.mock_llm)

        print("\n" + "=" * 70)
        print("ANSWER:\n")
        print(result["answer"])
        print("\nSOURCES:")
        for s in result["sources"]:
            print(f"  - {s['source']}  (relevance {s['score']})")
        if args.show_chunks:
            print("\nRETRIEVED CHUNKS:")
            for i, c in enumerate(result["chunks"], 1):
                preview = c["content"].strip().replace("\n", " ")[:160]
                print(f"  [{i}] {c['source']} (score {c['score']:.3f})  {preview}...")
        print("=" * 70)

    elif args.command == "eval":
        from .evaluate import evaluate
        from .config import TOP_K
        evaluate(k=args.k or TOP_K, check_answers=args.check_answers, prefer_embedder=args.embedder)


if __name__ == "__main__":
    main()
