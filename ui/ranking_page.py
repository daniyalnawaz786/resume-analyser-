"""
ui/ranking_page.py

Rank all + per-candidate skill-gap / interview.
"""

from __future__ import annotations

import streamlit as st

from db import models as db
from services import interview_service, ranking_service, skill_gap_service


def render() -> None:
    st.header("🏆 Rank & Analyse")

    store = st.session_state["store"]
    if store.index.ntotal == 0:
        st.info("Ingest some resumes on the Upload page first.")
        return

    jd = st.session_state.get("job_description", "")
    if not jd.strip():
        st.warning("No job description saved yet — rankings will be weak without one.")

    # --- Rank everyone -----------------------------------------------------
    st.subheader("Rank all candidates")
    if st.button("Rank now"):
        with st.spinner("Ranking candidates..."):
            try:
                st.session_state["ranking_result"] = ranking_service.rank_candidates(store, jd)
            except Exception as exc:
                st.session_state["ranking_result"] = f"⚠️ {exc}"
    if st.session_state.get("ranking_result"):
        st.markdown(st.session_state["ranking_result"])

    st.divider()

    # --- Per-candidate deep dive ------------------------------------------
    st.subheader("Per-candidate analysis")
    resumes = db.list_resumes()
    if not resumes:
        st.info("No candidates to analyse.")
        return

    options = {f"{r['candidate_name']} (#{r['id']})": r for r in resumes}
    choice = st.selectbox("Choose a candidate", list(options.keys()))
    candidate = options[choice]

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Skill-gap analysis"):
            with st.spinner("Analysing skill gaps..."):
                try:
                    result = skill_gap_service.analyse_skill_gap(
                        store, jd, candidate["id"], candidate["candidate_name"]
                    )
                except Exception as exc:
                    result = f"⚠️ {exc}"
            st.markdown(result)
    with col2:
        if st.button("Interview questions"):
            with st.spinner("Generating questions..."):
                try:
                    result = interview_service.generate_questions(
                        store, jd, candidate["id"], candidate["candidate_name"]
                    )
                except Exception as exc:
                    result = f"⚠️ {exc}"
            st.markdown(result)
