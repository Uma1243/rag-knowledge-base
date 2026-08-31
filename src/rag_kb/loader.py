"""Loading step (indexing Phase A, step 1): read the source documents from disk.

Each document becomes a dict with its text and metadata (source filename, title). Metadata
travels with every chunk so answers can cite where a fact came from.
"""

from pathlib import Path


def load_documents(kb_dir: Path):
    """Return a list of {"source", "title", "text"} for every .md/.txt file in kb_dir."""
    docs = []
    paths = sorted(kb_dir.glob("*.md")) + sorted(kb_dir.glob("*.txt"))
    for path in paths:
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            continue
        docs.append({
            "source": path.name,
            "title": _title_of(text, fallback=path.stem),
            "text": text,
        })
    return docs


def _title_of(text: str, fallback: str) -> str:
    """Use the first markdown H1 (`# ...`) as the document title if present."""
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback
