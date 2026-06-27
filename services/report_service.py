"""
services/report_service.py

Overall hiring report, persisted to SQLite.
"""

from __future__ import annotations

try:
    from recruitai.core import llm, prompt_builder
    from recruitai.core.vector_store import VectorStore
    from recruitai.db import models as db
    from recruitai.services.ranking_service import build_per_candidate_context
except ImportError:  # pragma: no cover - supports running this module from repo root.
    from core import llm, prompt_builder  # type: ignore[no-redef]
    from core.vector_store import VectorStore  # type: ignore[no-redef]
    from db import models as db  # type: ignore[no-redef]
    from services.ranking_service import build_per_candidate_context  # type: ignore[no-redef]


def generate_report(store: VectorStore, jd: str, title: str) -> str:
    """Generate a hiring report over the whole pool and persist it to SQLite."""
    context = build_per_candidate_context(store, jd)
    system, user = prompt_builder.build_report_prompt(jd, title, context)
    content = llm.generate(system, user)
    db.add_report(title, content)
    return content
