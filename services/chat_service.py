"""
services/chat_service.py

Free-form Q&A over the whole corpus (normal top-k retrieval).
"""

from __future__ import annotations

try:
    from recruitai.core import llm, prompt_builder, retriever
    from recruitai.core.vector_store import VectorStore
except ImportError:  # pragma: no cover - supports running this module from repo root.
    from core import llm, prompt_builder, retriever  # type: ignore[no-redef]
    from core.vector_store import VectorStore  # type: ignore[no-redef]


def answer_question(store: VectorStore, jd: str, question: str) -> str:
    """Answer a recruiter question using top-k retrieval across all resumes."""
    chunks = retriever.retrieve(store, question)
    context = retriever.format_chunks(chunks)
    system, user = prompt_builder.build_chat_prompt(jd, question, context)
    return llm.generate(system, user)
