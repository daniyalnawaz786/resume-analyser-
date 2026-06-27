# 🧭 RecruitAI — AI-Powered Recruitment Intelligence Platform

A RAG-based tool for recruiters. Upload resumes + a job description, then chat
with an AI agent to **rank candidates**, find **skill gaps**, generate
**interview questions**, and produce **hiring reports**.

> Status: scaffold. Code files are stubs — see **BUILD_GUIDE.md** for what to
> implement and in what order.

## Stack
| Layer        | Choice |
|--------------|--------|
| UI           | Streamlit |
| Parsing      | pypdf + python-docx |
| Embeddings   | sentence-transformers `all-MiniLM-L6-v2` (local, free, auto-downloads) |
| Vector store | FAISS (cosine via inner product on normalised vectors) |
| LLM          | Groq (Llama 3.3 70B) — free tier |
| Persistence  | SQLite |

## Setup
```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # then paste your free Groq key into .env

streamlit run app.py
```
First run downloads the embedding model (~80 MB) automatically.

## The flow
1. Upload resumes → text → section chunks → vectors → FAISS (+ SQLite row).
2. Save a job description.
3. Chat → top-k FAISS retrieval → prompt → Groq → answer.
4. Rank → **per-candidate** retrieval (fairer than one global query) → Groq.
5. Reports persist to SQLite so you can revisit them.

## Folders
- `core/` — the RAG pipeline, one job per file.
- `services/` — business logic that composes core modules.
- `db/` — SQLite connection + CRUD.
- `ui/` — Streamlit pages.
- `config.py` — all paths, model names, tunables.
- `app.py` — entry point + routing.
# resume-analyser-
