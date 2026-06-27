"""
core/vector_store.py

ONE job: store chunk vectors + metadata in FAISS and search them.
"""

from __future__ import annotations

import pickle

import numpy as np

try:
    from recruitai import config
except ImportError:  # pragma: no cover - supports running this module from repo root.
    import config  # type: ignore[no-redef]


class VectorStore:
    """A FAISS IndexFlatIP plus a parallel metadata list (row i == metadata[i])."""

    def __init__(self) -> None:
        import faiss

        self.index = faiss.IndexFlatIP(config.EMBEDDING_DIM)
        self.metadata: list[dict] = []

    # --- writes ------------------------------------------------------------
    def add(self, vectors: np.ndarray, metadatas: list[dict]) -> None:
        """Append vectors and their aligned metadata dicts."""
        if len(metadatas) == 0:
            return
        vectors = np.asarray(vectors, dtype=np.float32)
        if vectors.shape[0] != len(metadatas):
            raise ValueError("vectors and metadatas must have the same length")
        self.index.add(vectors)
        self.metadata.extend(metadatas)

    # --- reads -------------------------------------------------------------
    def search(self, query_vec: np.ndarray, top_k: int) -> list[dict]:
        """Return the top_k metadata dicts, each with an added cosine 'score'."""
        if self.index.ntotal == 0:
            return []
        query = np.asarray(query_vec, dtype=np.float32).reshape(1, -1)
        k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(query, k)

        results: list[dict] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            hit = dict(self.metadata[idx])
            hit["score"] = float(score)
            results.append(hit)
        return results

    def all_metadata(self) -> list[dict]:
        return list(self.metadata)

    # --- persistence -------------------------------------------------------
    def save(self) -> None:
        import faiss

        faiss.write_index(self.index, str(config.INDEX_PATH))
        with open(config.METADATA_PATH, "wb") as fh:
            pickle.dump(self.metadata, fh)

    @classmethod
    def load(cls) -> "VectorStore":
        """Load a persisted store, or return a fresh empty one if none exists."""
        import faiss

        store = cls()
        if config.INDEX_PATH.exists() and config.METADATA_PATH.exists():
            store.index = faiss.read_index(str(config.INDEX_PATH))
            with open(config.METADATA_PATH, "rb") as fh:
                store.metadata = pickle.load(fh)
        return store
