"""
core/parser.py

ONE job: turn an uploaded PDF/DOCX file into plain text.
"""

from __future__ import annotations

import io
from pathlib import Path


def parse_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF bytes, page by page."""
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(file_bytes))
    pages = [(page.extract_text() or "") for page in reader.pages]
    return "\n\n".join(pages).strip()


def parse_docx(file_bytes: bytes) -> str:
    """Extract text from DOCX bytes, paragraph by paragraph."""
    from docx import Document

    document = Document(io.BytesIO(file_bytes))
    paragraphs = [para.text for para in document.paragraphs if para.text.strip()]
    return "\n".join(paragraphs).strip()


def parse_file(filename: str, file_bytes: bytes) -> str:
    """Dispatch to the right parser based on the file extension."""
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        return parse_pdf(file_bytes)
    if suffix in (".docx", ".doc"):
        return parse_docx(file_bytes)
    if suffix in (".txt", ".md"):
        return file_bytes.decode("utf-8", errors="ignore").strip()
    raise ValueError(f"Unsupported file type: {suffix or filename!r}. Use PDF or DOCX.")
