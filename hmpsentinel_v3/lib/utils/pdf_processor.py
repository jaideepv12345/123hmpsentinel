# lib/utils/pdf_processor.py
"""
PDF Text Processor
Handles PDF text extraction with fallback for scanned documents.
Capped at MAX_PAGES to stay within Vercel Hobby 60-second function limit.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Vercel Hobby plan: 60s max. Large HMPs can be 400+ pages.
# Extracting 120 pages of dense text is sufficient for all 5 analysis modules
# and typically completes in < 20 seconds, leaving 40s for analysis.
MAX_PAGES = 120
MAX_CHARS = 800_000   # hard cap on characters to prevent memory issues


class PDFProcessor:
    """
    Processes PDF files and extracts text content.
    Page extraction is capped at MAX_PAGES to ensure completion within
    Vercel Hobby plan's 60-second function timeout.
    """

    def __init__(self):
        self.extracted_text = ""

    def extract_text(self, filepath: str) -> str:
        """
        Extract text from PDF file.
        Returns extracted text or empty string if extraction fails.
        Tries pdfplumber → PyPDF2 → pdfminer in order.
        """
        text = self._try_pdfplumber(filepath)
        if text:
            return text

        text = self._try_pypdf2(filepath)
        if text:
            return text

        text = self._try_pdfminer(filepath)
        if text:
            return text

        logger.error("All PDF text extraction methods failed")
        return ""

    # ── Extraction backends ───────────────────────────────────────────────────

    def _try_pdfplumber(self, filepath: str) -> str:
        try:
            import pdfplumber
            chunks = []
            total_chars = 0
            with pdfplumber.open(filepath) as pdf:
                total_pages = len(pdf.pages)
                pages_to_read = min(total_pages, MAX_PAGES)
                for i, page in enumerate(pdf.pages[:pages_to_read]):
                    page_text = page.extract_text() or ""
                    chunks.append(page_text)
                    total_chars += len(page_text)
                    if total_chars >= MAX_CHARS:
                        break

            text = "\n".join(chunks)
            if len(text.strip()) > 500:
                logger.info(
                    f"pdfplumber: extracted {len(text):,} chars "
                    f"({pages_to_read}/{total_pages} pages)"
                )
                return text[:MAX_CHARS]
        except Exception as e:
            logger.warning(f"pdfplumber failed: {e}")
        return ""

    def _try_pypdf2(self, filepath: str) -> str:
        try:
            import PyPDF2
            chunks = []
            total_chars = 0
            with open(filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                total_pages = len(reader.pages)
                pages_to_read = min(total_pages, MAX_PAGES)
                for page in reader.pages[:pages_to_read]:
                    page_text = page.extract_text() or ""
                    chunks.append(page_text)
                    total_chars += len(page_text)
                    if total_chars >= MAX_CHARS:
                        break

            text = "\n".join(chunks)
            if len(text.strip()) > 500:
                logger.info(
                    f"PyPDF2: extracted {len(text):,} chars "
                    f"({pages_to_read}/{total_pages} pages)"
                )
                return text[:MAX_CHARS]
        except Exception as e:
            logger.warning(f"PyPDF2 failed: {e}")
        return ""

    def _try_pdfminer(self, filepath: str) -> str:
        """pdfminer does not support per-page extraction easily; use as last resort."""
        try:
            from pdfminer.high_level import extract_text
            text = extract_text(filepath) or ""
            if len(text.strip()) > 500:
                logger.info(f"pdfminer: extracted {len(text):,} chars")
                return text[:MAX_CHARS]
        except Exception as e:
            logger.warning(f"pdfminer failed: {e}")
        return ""

    # ── Metadata helpers ──────────────────────────────────────────────────────

    def extract_metadata(self, filepath: str) -> dict:
        """Extract PDF metadata."""
        metadata = {
            "title": "", "author": "", "subject": "",
            "creator": "", "producer": "",
            "creation_date": None, "modification_date": None
        }
        try:
            import PyPDF2
            with open(filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                if reader.metadata:
                    metadata = {
                        "title":             reader.metadata.get("/Title", ""),
                        "author":            reader.metadata.get("/Author", ""),
                        "subject":           reader.metadata.get("/Subject", ""),
                        "creator":           reader.metadata.get("/Creator", ""),
                        "producer":          reader.metadata.get("/Producer", ""),
                        "creation_date":     reader.metadata.get("/CreationDate", ""),
                        "modification_date": reader.metadata.get("/ModDate", ""),
                    }
        except Exception as e:
            logger.warning(f"Metadata extraction failed: {e}")
        return metadata

    def get_page_count(self, filepath: str) -> int:
        """Return total page count of PDF."""
        try:
            import PyPDF2
            with open(filepath, "rb") as f:
                return len(PyPDF2.PdfReader(f).pages)
        except Exception:
            return 0
