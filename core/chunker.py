"""
core/chunker.py

ONE job: split resume text into section-based chunks (skills/experience/education...).
"""

from __future__ import annotations

import re
from collections.abc import Iterator

try:
    from recruitai import config
except ImportError:  # pragma: no cover - supports running this module from repo root.
    import config  # type: ignore[no-redef]


DEFAULT_CHUNK_SIZE = 900
DEFAULT_CHUNK_OVERLAP = 150

SECTION_NAMES = (
    "summary",
    "professional summary",
    "profile",
    "objective",
    "skills",
    "technical skills",
    "core competencies",
    "experience",
    "work experience",
    "professional experience",
    "employment history",
    "projects",
    "education",
    "certifications",
    "licenses",
    "awards",
    "publications",
    "languages",
    "interests",
    "references",
)

HEADER_PATTERN = re.compile(
    r"^\s*(?P<section>"
    + "|".join(re.escape(name) for name in sorted(SECTION_NAMES, key=len, reverse=True))
    + r")\s*:?\s*$",
    re.IGNORECASE | re.MULTILINE,
)


def chunk_text(text: str) -> list[dict[str, str]]:
    """Split resume text into section chunks, or fixed windows when no sections exist."""
    clean_text = _normalize_text(text)
    if not clean_text:
        return []

    section_chunks = _section_chunks(clean_text)
    if section_chunks:
        return section_chunks

    chunk_size = int(getattr(config, "CHUNK_SIZE", DEFAULT_CHUNK_SIZE))
    chunk_overlap = int(getattr(config, "CHUNK_OVERLAP", DEFAULT_CHUNK_OVERLAP))
    return [
        {"section": "general", "text": chunk}
        for chunk in _fixed_windows(clean_text, chunk_size, chunk_overlap)
    ]


def _normalize_text(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text.replace("\r\n", "\n").replace("\r", "\n")).strip()


def _section_chunks(text: str) -> list[dict[str, str]]:
    matches = list(HEADER_PATTERN.finditer(text))
    if not matches:
        return []

    chunks: list[dict[str, str]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        if body:
            chunks.append({"section": _section_label(match.group("section")), "text": body})

    return chunks


def _section_label(section: str) -> str:
    return re.sub(r"\s+", "_", section.strip().lower())


def _fixed_windows(text: str, chunk_size: int, chunk_overlap: int) -> Iterator[str]:
    chunk_size = max(1, chunk_size)
    chunk_overlap = max(0, min(chunk_overlap, chunk_size - 1))
    step = chunk_size - chunk_overlap

    for start in range(0, len(text), step):
        chunk = text[start : start + chunk_size].strip()
        if chunk:
            yield chunk
        if start + chunk_size >= len(text):
            break
