"""
config.py

Single source of truth: paths, model names, tunables. Loads .env.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# --- Paths -----------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
INDEX_DIR = DATA_DIR / "index"
DB_PATH = DATA_DIR / "recruitai.db"

for _dir in (DATA_DIR, UPLOAD_DIR, INDEX_DIR):
    _dir.mkdir(parents=True, exist_ok=True)

# Where the FAISS index + parallel metadata get persisted.
INDEX_PATH = INDEX_DIR / "index.faiss"
METADATA_PATH = INDEX_DIR / "metadata.pkl"

# Load .env (does nothing if the file is absent; never overrides real env vars).
load_dotenv(BASE_DIR / ".env")

# --- Embeddings ------------------------------------------------------------
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

# --- Chunking / retrieval --------------------------------------------------
CHUNK_SIZE = 900
CHUNK_OVERLAP = 150
TOP_K = 5

# --- LLM (Groq) ------------------------------------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2048"))
