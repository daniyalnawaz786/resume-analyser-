# AGENTS.md — context for AI coding assistants

Read this before generating code. (Works as context for Cursor, Claude Code,
Copilot, Windsurf, etc. Rename to `.cursorrules` or `CLAUDE.md` if your tool
prefers that filename.)

## What this project is
RecruitAI: a Streamlit + RAG app. Recruiters upload resumes (PDF/DOCX) and a job
description, then chat with an LLM (Groq/Llama) to rank candidates, find skill
gaps, generate interview questions, and write hiring reports. Embeddings are
local (sentence-transformers); vectors live in FAISS; metadata in SQLite.

## Architecture in one line
`parse → chunk → embed → FAISS` on ingest, and
`query → embed → retrieve → build prompt → Groq` on ask.

## Hard rules
1. **One job per file.** Don't merge responsibilities. Parser only parses; embedder
   only embeds; llm.py only talks to Groq; etc.
2. **Import `config.py` for every constant** — no hard-coded model names, paths, or
   magic numbers in other files.
3. **All SQL lives in `db/models.py`.** No raw queries anywhere else.
4. **Services compose `core/`** — they add no new infrastructure, just orchestration.
5. **UI pages are thin.** Each `ui/*` file exposes one `render()` that reads/writes
   `st.session_state` and calls a service. No business logic in the UI.
6. **Fail loud with friendly messages**, especially a missing `GROQ_API_KEY`.

## Conventions
- Python 3.10+, type hints on public functions, module docstring at the top.
- Embeddings are **normalised**; FAISS uses `IndexFlatIP` (cosine).
- Vector metadata dict shape: `{resume_id, chunk_id, candidate_name, section, text}`.
- Prompt builders return `(system_prompt, user_prompt)` tuples.
- Shared session state keys: `store` (VectorStore), `job_description` (str),
  `candidates` (list of ingest summaries).

## Don't do this
- ❌ Don't rank all candidates with a single FAISS query — use per-candidate
  retrieval (see BUILD_GUIDE gotcha #1).
- ❌ Don't put an API key in code — read it from `.env` via `config.py`.
- ❌ Don't use `localStorage`/browser storage — this is a Python/Streamlit app;
  state goes in `st.session_state` and SQLite.
- ❌ Don't invent candidate facts — prompts must instruct the model to use only
  the provided evidence.

## Build order
Follow BUILD_GUIDE.md top to bottom: config → db → parser → chunker → embedder →
vector_store → retriever → ingestion → prompt_builder → llm → services → ui.
