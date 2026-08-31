"""
Meridian Assistant — a Streamlit chatbot UI over the rag_kb RAG engine.

Run it (from the repo root, with your venv active):
    streamlit run app/streamlit_app.py

This is a thin UI layer. All the real work — retrieval and grounded generation — is done by
the same rag_kb package you built and tested. The app just:
  * makes sure the index exists (builds it on first run),
  * takes a question from a chat box,
  * shows the grounded answer with its sources,
  * and, when the docs don't contain the answer, shows the honest "I don't have that" reply.

A sidebar toggle switches between MOCK mode (no API key needed) and REAL mode (calls Claude).
"""

import os
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# --- Make the src/ package importable and load .env (for the API key) -------
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
load_dotenv(ROOT / ".env")

from rag_kb.pipeline import RagPipeline
from rag_kb.app_support import ensure_index, has_api_key, list_documents

# --- Page config ------------------------------------------------------------
st.set_page_config(page_title="Meridian Assistant", page_icon="💬", layout="centered")


# --- Cache the heavy objects so we don't rebuild/reload on every keystroke --
@st.cache_resource(show_spinner=False)
def get_pipeline():
    """Ensure an index exists, then load the RAG pipeline once and reuse it."""
    ensure_index(prefer_embedder="auto", log=lambda *_: None)
    return RagPipeline(prefer_embedder="auto")


# --- Sidebar: mode, info, sample questions ----------------------------------
with st.sidebar:
    st.title("💬 Meridian Assistant")
    st.caption("Ask questions about Meridian Data Co.'s internal documentation.")

    key_present = has_api_key()
    st.subheader("Answer mode")
    real_default = key_present
    use_real = st.toggle(
        "Real answers (Claude)",
        value=real_default,
        help="On: calls the Claude API for natural-language answers (needs ANTHROPIC_API_KEY). "
             "Off: mock mode — shows the top retrieved chunk, no API key needed.",
    )
    if use_real and not key_present:
        st.warning("No ANTHROPIC_API_KEY found. Set it in a .env file, or switch this off to use mock mode.")
    st.divider()

    top_k = st.slider("Chunks to retrieve (top-k)", min_value=1, max_value=8, value=4,
                      help="How many document passages to fetch and feed to the model.")
    show_chunks = st.checkbox("Show retrieved passages", value=False)
    st.divider()

    st.subheader("Knowledge base")
    st.caption("The assistant can only answer from these documents:")
    for doc in list_documents():
        st.markdown(f"- `{doc}`")
    st.divider()

    st.subheader("Try asking")
    samples = [
        "How long is bronze data kept before deletion?",
        "What are the SEV1 incident response targets?",
        "How is PII handled at ingestion?",
        "What is the medallion architecture?",
        "What is Meridian's revenue?",   # not in the docs -> honest 'I don't know'
    ]
    for s in samples:
        if st.button(s, use_container_width=True):
            st.session_state["pending_question"] = s


# --- Header -----------------------------------------------------------------
st.title("Meridian Assistant")
mode_label = "🟢 Real (Claude)" if (use_real and key_present) else "🟡 Mock (no API key)"
st.caption(f"Grounded Q&A over the company knowledge base · Mode: {mode_label}")

# --- Chat history in session state ------------------------------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Replay the conversation so far
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            _render_sources = msg["sources"]
            with st.expander("Sources"):
                for s in _render_sources:
                    st.markdown(f"- `{s['source']}` (relevance {s['score']})")


def answer_question(question: str):
    """Run one question through the RAG pipeline and append the result to the chat."""
    st.session_state["messages"].append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching the knowledge base..."):
            pipe = get_pipeline()
            use_mock = not (use_real and has_api_key())
            try:
                result = pipe.answer(question, k=top_k, use_mock_llm=use_mock)
            except Exception as e:
                err = f"Something went wrong while answering: `{e}`"
                st.error(err)
                st.session_state["messages"].append({"role": "assistant", "content": err})
                return

        st.markdown(result["answer"])

        if result["sources"]:
            with st.expander("Sources"):
                for s in result["sources"]:
                    st.markdown(f"- `{s['source']}` (relevance {s['score']})")
        if show_chunks:
            with st.expander("Retrieved passages"):
                for i, c in enumerate(result["chunks"], 1):
                    st.markdown(f"**[{i}] `{c['source']}`** · score {c['score']:.3f}")
                    st.caption(c["content"][:400] + ("..." if len(c["content"]) > 400 else ""))

    st.session_state["messages"].append({
        "role": "assistant",
        "content": result["answer"],
        "sources": result["sources"],
    })


# --- Handle a sidebar sample click ------------------------------------------
if "pending_question" in st.session_state:
    q = st.session_state.pop("pending_question")
    answer_question(q)

# --- Chat input -------------------------------------------------------------
if prompt := st.chat_input("Ask about Meridian's policies, architecture, runbooks..."):
    answer_question(prompt)
