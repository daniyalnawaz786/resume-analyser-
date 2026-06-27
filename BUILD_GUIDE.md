# 🛠 BUILD_GUIDE — how to build RecruitAI, in order

Each file is a stub with a one-line docstring and a `# TODO`. Build them in the
order below. Lower layers first so you can test as you climb. Every module has
**one job** — don't let logic leak across boundaries.

Golden rule: a function takes clear inputs and returns clear outputs. If a file
starts doing two jobs, split it.

---

## Build order (bottom-up)

### 1. `config.py`  ← do this first, everything imports it
Holds paths, model names, and tunables. Load `.env` with `python-dotenv`.
Define at least:
- `BASE_DIR`, `DATA_DIR`, `UPLOAD_DIR`, `INDEX_DIR`, `DB_PATH` (create dirs on import)
- `EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"`, `EMBEDDING_DIM = 384`
- `CHUNK_SIZE`, `CHUNK_OVERLAP`, `TOP_K`
- `GROQ_API_KEY`, `GROQ_MODEL` (via `os.getenv`), `LLM_TEMPERATURE`, `LLM_MAX_TOKENS`

### 2. `db/database.py` + `db/models.py`
- `database.py`: `get_conn()` (context manager, `row_factory = sqlite3.Row`),
  `init_db()` running `CREATE TABLE IF NOT EXISTS` for **resumes**,
  **job_descriptions**, **chat_history**, **reports**.
- `models.py`: thin CRUD. Keep ALL SQL here.
- ✅ Test: `init_db()`, insert a resume, list it back. No ML needed.

### 3. `core/parser.py`
- `parse_file(filename, file_bytes)` → text. Dispatch on extension (.pdf/.docx).
- ✅ Test: feed a real PDF and a real DOCX, print the text.

### 4. `core/chunker.py`
- `chunk_text(text)` → `list[{"section": str, "text": str}]`.
- Try header detection (regex over known section names) → one chunk per section.
- Fall back to fixed-size overlapping windows when no headers found.
- ✅ Test: paste a fake resume string, check sections come out right. No ML needed.

### 5. `core/embedder.py`
- Lazy-load the model as a module-level singleton (load once per process).
- `embed_texts(list[str])` → `np.ndarray (N, 384) float32`, **normalised**.
- `embed_text(str)` → single vector.
- ✅ Test: embed two sentences, check shape is (2, 384).

### 6. `core/vector_store.py`
- `VectorStore` class wrapping `faiss.IndexFlatIP(384)` (inner product == cosine
  because vectors are normalised).
- FAISS stores vectors only → keep a parallel `self.metadata: list[dict]` where
  row i in the index == metadata[i].
- Methods: `add(vectors, metadatas)`, `search(query_vec, top_k)` → list of
  metadata dicts each with an added `score`, `all_metadata()`, `save()`, `load()`.
- Metadata dict shape: `{resume_id, chunk_id, candidate_name, section, text}`.
- ✅ Test: add a few vectors, search, confirm you get metadata back.

### 7. `core/retriever.py`
- `retrieve(store, query, k)`: embed query → `store.search`.
- `retrieve_for_candidate(store, query, resume_id, k)`: over-fetch then filter by
  `resume_id` (FAISS has no metadata filter).
- `format_chunks(chunks)` → readable string block for prompts.

### 8. `core/ingestion.py`  ← the glue
- `ingest_resume(store, filename, file_bytes, name?)`:
  parse → guess/accept name → `db.add_resume` (get resume_id) → chunk → embed →
  build metadata list → `store.add`. Return `{resume_id, candidate_name, num_chunks}`.
- ✅ Test: ingest one resume, then `store.search("python")` and see it.

### 9. `core/prompt_builder.py`
- One builder per task, each returning `(system_prompt, user_prompt)`:
  `build_chat_prompt`, `build_ranking_prompt`, `build_skill_gap_prompt`,
  `build_interview_prompt`, `build_report_prompt`.
- Share one `SYSTEM_PROMPT` ("expert recruiter, only use evidence given,
  say when info is missing").

### 10. `core/llm.py`
- Lazy Groq client from `config.GROQ_API_KEY`.
- `generate(system, user)` → text. Raise a friendly error if the key is missing.
- ✅ Test: call it with a trivial prompt, confirm Groq answers.

### 11. `services/*`  ← compose core, no new infra
- `chat_service.answer_question(store, jd, question)` — top-k retrieval.
- `ranking_service.rank_candidates(store, jd)` — **per-candidate** retrieval
  (loop unique resume_ids, gather each one's JD-relevant chunks), then ONE llm call.
- `skill_gap_service.analyse_skill_gap(store, jd, resume_id, name)`.
- `interview_service.generate_questions(store, jd, resume_id, name)`.
- `report_service.generate_report(store, jd, title)` — also `db.add_report`.

### 12. `ui/*` + `app.py`  ← last
- `app.py`: `init_db()`; put `store = VectorStore.load()` and `job_description`
  in `st.session_state`; sidebar radio → call the chosen page's `render()`.
- Each page module exposes a single `render()` that reads/writes `st.session_state`.

---

## ⚠️ Three gotchas (read before you start)

1. **Ranking ≠ one FAISS query.** "Rank everyone" with a single similarity search
   buries candidates whose wording doesn't match the query embedding. In
   `ranking_service`, loop over each candidate and pull *their* JD-relevant chunks,
   then send a balanced context to the LLM. Chat/Q&A keeps normal top-k.

2. **FAISS holds no metadata.** Keep the parallel `metadata` list perfectly aligned
   with insertion order, and persist both together (`index.faiss` + `metadata.pkl`).

3. **Normalise embeddings** (`normalize_embeddings=True`) so `IndexFlatIP` gives
   cosine similarity. Skip this and your scores are meaningless.

---

## Definition of done for v1
- [ ] Upload 2-3 resumes + a JD, see them ingested.
- [ ] Ask a question in chat, get a grounded answer.
- [ ] Rank all candidates with scores + justification.
- [ ] Skill-gap + interview questions for one candidate.
- [ ] Generate a report; it persists and reloads after restart.
