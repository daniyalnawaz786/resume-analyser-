"""
core/embedder.py

ONE job: text -> vector via sentence-transformers (all-MiniLM-L6-v2).
"""

from __future__ import annotations

import numpy as np

try:
    from recruitai import config
except ImportError:  # pragma: no cover - supports running this module from repo root.
    import config  # type: ignore[no-redef]


_model = None  # module-level singleton; load the model once per process.


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(config.EMBEDDING_MODEL_NAME)
    return _model


def embed_texts(texts: list[str]) -> np.ndarray:
    """Embed a list of strings into a normalised (N, 384) float32 array."""
    if not texts:
        return np.empty((0, config.EMBEDDING_DIM), dtype=np.float32)

    vectors = _get_model().encode(
        texts,
        normalize_embeddings=True,  # cosine similarity via inner product downstream.
        convert_to_numpy=True,
    )
    return np.asarray(vectors, dtype=np.float32)


def embed_text(text: str) -> np.ndarray:
    """Embed a single string into a normalised (384,) float32 vector."""
    return embed_texts([text])[0]
