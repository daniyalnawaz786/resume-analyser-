"""
app.py

Streamlit entry point: init DB, hold shared state, route pages.

Run with:  streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from core.vector_store import VectorStore
from db.database import init_db
from db import models as db
from ui import chat_page, ranking_page, reports_page, upload_page

PAGES = {
    "📤 Upload": upload_page,
    "💬 Chat": chat_page,
    "🏆 Rank & Analyse": ranking_page,
    "📊 Reports": reports_page,
}


def _bootstrap() -> None:
    """One-time per-session setup: schema, vector store, last-saved JD."""
    if st.session_state.get("_booted"):
        return
    init_db()
    st.session_state["store"] = VectorStore.load()
    latest_jd = db.get_latest_job_description()
    if latest_jd:
        st.session_state["job_description"] = latest_jd["text"]
        st.session_state["jd_title"] = latest_jd["title"]
    st.session_state["_booted"] = True


def main() -> None:
    st.set_page_config(page_title="RecruitAI", page_icon="🧭", layout="wide")
    _bootstrap()

    st.sidebar.title("🧭 RecruitAI")
    st.sidebar.caption("AI-powered recruitment intelligence")
    choice = st.sidebar.radio("Navigate", list(PAGES.keys()))

    store = st.session_state["store"]
    st.sidebar.metric("Indexed chunks", store.index.ntotal)

    PAGES[choice].render()


if __name__ == "__main__":
    main()
