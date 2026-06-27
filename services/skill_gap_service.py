"""
services/skill_gap_service.py

Gap between one candidate and the job requirements.
"""

from __future__ import annotations

try:
    from recruitai.core import llm, prompt_builder, retriever
    from recruitai.core.vector_store import VectorStore
except ImportError:  # pragma: no cover - supports running this module from repo root.
    from core import llm, prompt_builder, retriever  # type: ignore[no-redef]
    from core.vector_store import VectorStore  # type: ignore[no-redef]


def analyse_skill_gap(store: VectorStore, jd: str, resume_id: int, name: str) -> str:
    """Compare one candidate's evidence against the JD and report skill gaps."""
    query = jd.strip() or "required skills and experience"
    chunks = retriever.retrieve_for_candidate(store, query, resume_id, k=6)
    context = retriever.format_chunks(chunks)
    system, user = prompt_builder.build_skill_gap_prompt(jd, name, context)
    return llm.generate(system, user)
