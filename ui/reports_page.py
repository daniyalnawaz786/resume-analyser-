"""
ui/reports_page.py

Generate + browse saved hiring reports.
"""

from __future__ import annotations

import streamlit as st

from db import models as db
from services import report_service


def render() -> None:
    st.header("📊 Hiring Reports")

    store = st.session_state["store"]

    # --- Generate ----------------------------------------------------------
    st.subheader("Generate a new report")
    title = st.text_input("Report title", value="Hiring report")
    if st.button("Generate report"):
        if store.index.ntotal == 0:
            st.warning("Ingest some resumes first.")
        else:
            with st.spinner("Writing report..."):
                try:
                    content = report_service.generate_report(
                        store, st.session_state.get("job_description", ""), title
                    )
                    st.success("Report generated and saved.")
                    st.markdown(content)
                except Exception as exc:
                    st.error(f"⚠️ {exc}")

    st.divider()

    # --- Browse saved ------------------------------------------------------
    st.subheader("Saved reports")
    reports = db.list_reports()
    if not reports:
        st.info("No reports saved yet.")
        return

    for report in reports:
        with st.expander(f"{report['title']} — {report['created_at']}"):
            st.markdown(report["content"])
