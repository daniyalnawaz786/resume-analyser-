"""
core/ingestion.py

Glue: parse -> chunk -> embed -> store for one resume (+ DB row).
"""

from __future__ import annotations

import re
from pathlib import Path

try:
    from recruitai.core import chunker, embedder, parser
    from recruitai.core.vector_store import VectorStore
    from recruitai.db import models as db
except ImportError:  # pragma: no cover - supports running this module from repo root.
    from core import chunker, embedder, parser  # type: ignore[no-redef]
    from core.vector_store import VectorStore  # type: ignore[no-redef]
    from db import models as db  # type: ignore[no-redef]


def ingest_resume(
    store: VectorStore,
    filename: str,
    file_bytes: bytes,
    name: str | None = None,
) -> dict:
    """Parse, chunk, embed and index one resume; also persist a DB row.

    Returns {"resume_id", "candidate_name", "num_chunks"}.
    """
    text = parser.parse_file(filename, file_bytes)
    if not text.strip():
        raise ValueError(f"No readable text extracted from {filename!r}.")

    candidate_name = name or _guess_name(text, filename)
    chunks = chunker.chunk_text(text)
    if not chunks:
        raise ValueError(f"Could not chunk any content from {filename!r}.")

    resume_id = db.add_resume(candidate_name, filename, text, len(chunks))

    vectors = embedder.embed_texts([chunk["text"] for chunk in chunks])
    metadatas = [
        {
            "resume_id": resume_id,
            "chunk_id": i,
            "candidate_name": candidate_name,
            "section": chunk["section"],
            "text": chunk["text"],
        }
        for i, chunk in enumerate(chunks)
    ]
    store.add(vectors, metadatas)

    return {
        "resume_id": resume_id,
        "candidate_name": candidate_name,
        "num_chunks": len(chunks),
    }


def _guess_name(text: str, filename: str) -> str:
    """Best-effort candidate name: first plausible line, else the filename stem."""
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # A name line: 1-4 words, mostly letters, no digits or @.
        words = line.split()
        if 1 <= len(words) <= 4 and re.fullmatch(r"[A-Za-z.\-' ]+", line):
            return line.title()
        break  # only inspect the first non-empty line.

    return Path(filename).stem.replace("_", " ").replace("-", " ").strip().title() or "Unknown"
