"""
ui/chat_page.py

Chat interface over the corpus.
"""

from __future__ import annotations

import streamlit as st

from db import models as db
from services import chat_service


def render() -> None:
    st.header("💬 Chat with the candidate pool")

    store = st.session_state["store"]
    if store.index.ntotal == 0:
        st.info("Ingest some resumes on the Upload page first.")
        return

    # Replay prior turns from this session.
    history = st.session_state.setdefault("chat_messages", [])
    for msg in history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    question = st.chat_input("Ask about the candidates...")
    if not question:
        return

    history.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                answer = chat_service.answer_question(
                    store, st.session_state.get("job_description", ""), question
                )
            except Exception as exc:
                answer = f"⚠️ {exc}"
        st.markdown(answer)

    history.append({"role": "assistant", "content": answer})
    db.add_chat(question, answer)
