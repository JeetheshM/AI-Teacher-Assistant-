"""
pdf_extractor.py
----------------
Extracts text from uploaded PDF files page by page.
Returns a list of CurriculumContext chunks ready for QuizService.

Used by the /api/quizzes/generate-from-file endpoint.
Person 4 owns the full RAG pipeline; this is a lightweight
standalone extractor for direct file uploads.
"""

from __future__ import annotations

import io
from typing import List

import pdfplumber

from backend.models.quiz_models import CurriculumContext


def extract_text_from_pdf(
    file_bytes: bytes,
    filename: str,
    max_chars_per_page: int = 1500,
) -> List[CurriculumContext]:
    """
    Extract text from a PDF file and return as CurriculumContext chunks.

    Each page becomes one chunk. Pages with no extractable text are skipped.

    Args:
        file_bytes:         Raw bytes of the uploaded PDF.
        filename:           Original filename (used as source label).
        max_chars_per_page: Truncate very long pages to keep prompt manageable.

    Returns:
        List of CurriculumContext — one per non-empty page.
    """
    chunks: List[CurriculumContext] = []

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if not text or not text.strip():
                continue  # skip blank/image-only pages

            # Trim to keep prompt size reasonable
            text = text.strip()[:max_chars_per_page]

            chunks.append(
                CurriculumContext(
                    content=text,
                    source=filename,
                    page_number=page_num,
                )
            )

    return chunks


def extract_text_from_txt(file_bytes: bytes, filename: str) -> List[CurriculumContext]:
    """
    Extract text from a plain .txt file as a single chunk.
    """
    text = file_bytes.decode("utf-8", errors="replace").strip()
    if not text:
        return []
    return [CurriculumContext(content=text[:3000], source=filename, page_number=None)]
