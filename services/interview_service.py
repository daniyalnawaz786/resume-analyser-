"""
services/interview_service.py

Tailored interview questions for one candidate.
"""

from __future__ import annotations

try:
    from recruitai.core import llm, prompt_builder, retriever
    from recruitai.core.vector_store import VectorStore
except ImportError:  # pragma: no cover - supports running this module from repo root.
    from core import llm, prompt_builder, retriever  # type: ignore[no-redef]
    from core.vector_store import VectorStore  # type: ignore[no-redef]


def generate_questions(store: VectorStore, jd: str, resume_id: int, name: str) -> str:
    """Generate interview questions tailored to one candidate and the JD."""
    query = jd.strip() or "required skills and experience"
    chunks = retriever.retrieve_for_candidate(store, query, resume_id, k=6)
    context = retriever.format_chunks(chunks)
    system, user = prompt_builder.build_interview_prompt(jd, name, context)
    return llm.generate(system, user)
