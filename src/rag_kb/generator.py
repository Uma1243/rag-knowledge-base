"""Generation — the second half of RAG's query phase (RAG handbook, Part 7).

Build a grounded prompt from the retrieved chunks and call the LLM. The prompt carries the two
guardrails that make RAG trustworthy: answer ONLY from the context, and say "I don't know" if
the context doesn't contain the answer.

A `--mock` generator is included so the whole pipeline can run and be tested without an API key
(it stitches an answer from the top chunk). Real generation uses the Anthropic API.
"""

from .config import LLM_MODEL, LLM_MAX_TOKENS

SYSTEM_PROMPT = (
    "You are Meridian's internal knowledge assistant. Answer the user's question using ONLY "
    "the context provided. If the context does not contain the answer, say exactly: "
    "\"I don't have that information in the knowledge base.\" Do not use outside knowledge. "
    "Be concise and, where useful, cite the source document in parentheses."
)


def build_prompt(question, chunks):
    """Assemble the context block + question (the 'augment' step)."""
    if not chunks:
        context = "(no relevant context found)"
    else:
        context = "\n\n".join(
            f"[{i+1}] (source: {c['source']})\n{c['content']}"
            for i, c in enumerate(chunks)
        )
    return f"Context:\n{context}\n\nQuestion: {question}"


def generate(question, chunks, use_mock=False):
    """Return the model's grounded answer given the retrieved chunks."""
    user_prompt = build_prompt(question, chunks)
    if use_mock:
        return _mock_generate(question, chunks)
    return _anthropic_generate(user_prompt)


def _anthropic_generate(user_prompt):
    from anthropic import Anthropic
    client = Anthropic()                       # reads ANTHROPIC_API_KEY from env

    kwargs = dict(
        model=LLM_MODEL,
        max_tokens=LLM_MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
        temperature=0,                          # deterministic answers for a knowledge base
    )
    try:
        resp = client.messages.create(**kwargs)
    except TypeError:
        # Anthropic SDK v1.0+ removed `temperature`; retry without it.
        kwargs.pop("temperature", None)
        resp = client.messages.create(**kwargs)
    return resp.content[0].text


def _mock_generate(question, chunks):
    """No-API stand-in: echo the most relevant chunk so the flow is testable offline."""
    if not chunks:
        return "I don't have that information in the knowledge base."
    top = chunks[0]
    snippet = top["content"].strip().replace("\n", " ")
    if len(snippet) > 300:
        snippet = snippet[:300] + "..."
    return f"[MOCK ANSWER from top chunk of {top['source']}]: {snippet}"
