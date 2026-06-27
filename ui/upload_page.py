"""
ui/upload_page.py

Upload resumes (PDF/DOCX) + paste JD; ingest into the store.
"""

from __future__ import annotations

import streamlit as st

from core import ingestion
from db import models as db


def render() -> None:
    st.header("📤 Upload & Ingest")

    # --- Job description ---------------------------------------------------
    st.subheader("Job description")
    jd_title = st.text_input("Role title", value=st.session_state.get("jd_title", "Untitled role"))
    jd_text = st.text_area(
        "Paste the job description",
        value=st.session_state.get("job_description", ""),
        height=200,
    )
    if st.button("Save job description"):
        if jd_text.strip():
            db.add_job_description(jd_text, jd_title)
            st.session_state["job_description"] = jd_text
            st.session_state["jd_title"] = jd_title
            st.success("Job description saved.")
        else:
            st.warning("Please paste a job description first.")

    st.divider()

    # --- Resumes -----------------------------------------------------------
    st.subheader("Resumes")
    files = st.file_uploader(
        "Upload resumes (PDF or DOCX)",
        type=["pdf", "docx", "txt", "md"],
        accept_multiple_files=True,
    )
    if st.button("Ingest resumes"):
        if not files:
            st.warning("Add at least one file first.")
        else:
            store = st.session_state["store"]
            progress = st.progress(0.0)
            for i, file in enumerate(files, start=1):
                try:
                    result = ingestion.ingest_resume(store, file.name, file.getvalue())
                    st.write(
                        f"✅ **{result['candidate_name']}** — "
                        f"{result['num_chunks']} chunks ({file.name})"
                    )
                except Exception as exc:  # surface per-file errors, keep going.
                    st.error(f"❌ {file.name}: {exc}")
                progress.progress(i / len(files))
            store.save()
            st.success("Done. Vector index saved.")

    # --- Current corpus ----------------------------------------------------
    st.divider()
    st.subheader("Ingested candidates")
    resumes = db.list_resumes()
    if resumes:
        st.dataframe(
            [
                {
                    "ID": r["id"],
                    "Candidate": r["candidate_name"],
                    "File": r["filename"],
                    "Chunks": r["num_chunks"],
                    "Added": r["created_at"],
                }
                for r in resumes
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No resumes ingested yet.")
