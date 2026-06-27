"""
db/models.py

Thin CRUD over the SQLite tables (all SQL lives here).
"""

from __future__ import annotations

try:
    from recruitai.db.database import get_conn
except ImportError:  # pragma: no cover - supports running this module from repo root.
    from db.database import get_conn  # type: ignore[no-redef]


# --- resumes ---------------------------------------------------------------
def add_resume(candidate_name: str, filename: str, raw_text: str, num_chunks: int) -> int:
    """Insert a resume row and return its new id."""
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO resumes (candidate_name, filename, raw_text, num_chunks) "
            "VALUES (?, ?, ?, ?)",
            (candidate_name, filename, raw_text, num_chunks),
        )
        return int(cur.lastrowid)


def list_resumes() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, candidate_name, filename, num_chunks, created_at "
            "FROM resumes ORDER BY created_at DESC, id DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def get_resume(resume_id: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM resumes WHERE id = ?", (resume_id,)
        ).fetchone()
    return dict(row) if row else None


# --- job_descriptions ------------------------------------------------------
def add_job_description(text: str, title: str = "Untitled role") -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO job_descriptions (title, text) VALUES (?, ?)",
            (title, text),
        )
        return int(cur.lastrowid)


def get_latest_job_description() -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM job_descriptions ORDER BY created_at DESC, id DESC LIMIT 1"
        ).fetchone()
    return dict(row) if row else None


# --- chat_history ----------------------------------------------------------
def add_chat(question: str, answer: str) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO chat_history (question, answer) VALUES (?, ?)",
            (question, answer),
        )
        return int(cur.lastrowid)


def list_chat(limit: int = 50) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, question, answer, created_at "
            "FROM chat_history ORDER BY created_at ASC, id ASC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


# --- reports ---------------------------------------------------------------
def add_report(title: str, content: str) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO reports (title, content) VALUES (?, ?)",
            (title, content),
        )
        return int(cur.lastrowid)


def list_reports() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, title, content, created_at "
            "FROM reports ORDER BY created_at DESC, id DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def get_report(report_id: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM reports WHERE id = ?", (report_id,)
        ).fetchone()
    return dict(row) if row else None
