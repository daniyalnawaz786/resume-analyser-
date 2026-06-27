"""
services/ranking_service.py

Rank ALL candidates via per-candidate retrieval, NOT one global query.
"""

from __future__ import annotations

try:
    from recruitai.core import llm, prompt_builder, retriever
    from recruitai.core.vector_store import VectorStore
except ImportError:  # pragma: no cover - supports running this module from repo root.
    from core import llm, prompt_builder, retriever  # type: ignore[no-redef]
    from core.vector_store import VectorStore  # type: ignore[no-redef]


def build_per_candidate_context(store: VectorStore, jd: str, per_candidate_k: int = 4) -> str:
    """Gather each candidate's JD-relevant chunks into one balanced context block.

    A single global FAISS query buries candidates whose wording differs from the
    query embedding. Instead we loop each candidate and pull *their* top chunks,
    so every candidate is represented before the LLM sees them.
    """
    query = jd.strip() or "candidate skills and experience"

    candidates: dict[int, str] = {}
    for meta in store.all_metadata():
        candidates.setdefault(meta["resume_id"], meta.get("candidate_name", "Unknown"))

    if not candidates:
        return "(no candidates ingested yet)"

    blocks: list[str] = []
    for resume_id, name in candidates.items():
        chunks = retriever.retrieve_for_candidate(store, query, resume_id, k=per_candidate_k)
        evidence = retriever.format_chunks(chunks)
        blocks.append(f"=== {name} (resume #{resume_id}) ===\n{evidence}")
    return "\n\n".join(blocks)


def rank_candidates(store: VectorStore, jd: str) -> str:
    """Rank every candidate against the JD with one balanced LLM call."""
    context = build_per_candidate_context(store, jd)
    system, user = prompt_builder.build_ranking_prompt(jd, context)
    return llm.generate(system, user)
