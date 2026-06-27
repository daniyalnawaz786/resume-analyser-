"""
core/retriever.py

The 'R' in RAG: embed a query, search the store, return relevant chunks.
"""

from __future__ import annotations

try:
    from recruitai import config
    from recruitai.core import embedder
    from recruitai.core.vector_store import VectorStore
except ImportError:  # pragma: no cover - supports running this module from repo root.
    import config  # type: ignore[no-redef]
    from core import embedder  # type: ignore[no-redef]
    from core.vector_store import VectorStore  # type: ignore[no-redef]


def retrieve(store: VectorStore, query: str, k: int | None = None) -> list[dict]:
    """Top-k retrieval across the whole corpus."""
    k = k or config.TOP_K
    query_vec = embedder.embed_text(query)
    return store.search(query_vec, k)


def retrieve_for_candidate(
    store: VectorStore, query: str, resume_id: int, k: int | None = None
) -> list[dict]:
    """Top-k retrieval limited to one candidate.

    FAISS has no metadata filter, so we over-fetch then filter by resume_id.
    """
    k = k or config.TOP_K
    query_vec = embedder.embed_text(query)
    overfetch = max(k * 10, 50)
    hits = store.search(query_vec, overfetch)
    own = [hit for hit in hits if hit.get("resume_id") == resume_id]
    return own[:k]


def format_chunks(chunks: list[dict]) -> str:
    """Render retrieved chunks into a readable evidence block for prompts."""
    if not chunks:
        return "(no relevant resume content found)"

    blocks: list[str] = []
    for chunk in chunks:
        name = chunk.get("candidate_name", "Unknown")
        section = chunk.get("section", "general")
        text = chunk.get("text", "").strip()
        blocks.append(f"[{name} — {section}]\n{text}")
    return "\n\n".join(blocks)
