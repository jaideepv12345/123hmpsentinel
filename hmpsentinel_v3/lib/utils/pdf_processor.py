# api/utils/pdf_processor.py
"""
PDF Text Processor
Handles PDF text extraction with fallback for scanned documents
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class PDFProcessor:
    """
    Processes PDF files and extracts text content.
    Supports both digital PDFs and provides fallback for scanned documents.
    """
    
    def __init__(self):
        self.extracted_text = ""
    
    def extract_text(self, filepath: str) -> str:
        """
        Extract text from PDF file
        Returns extracted text or empty string if extraction fails
        """
        text = ""
        
        # Try pdfplumber first (better for text-based PDFs)
        try:
            import pdfplumber
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            if len(text.strip()) > 500:
                logger.info(f"Extracted {len(text)} characters using pdfplumber")
                return text
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {str(e)}")
        
        # Try PyPDF2 as fallback
        try:
            import PyPDF2
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            if len(text.strip()) > 500:
                logger.info(f"Extracted {len(text)} characters using PyPDF2")
                return text
        except Exception as e:
            logger.warning(f"PyPDF2 extraction failed: {str(e)}")
        
        # Try pdfminer.six as another fallback
        try:
            from pdfminer.high_level import extract_text
            text = extract_text(filepath)
            
            if len(text.strip()) > 500:
                logger.info(f"Extracted {len(text)} characters using pdfminer")
                return text
        except Exception as e:
            logger.warning(f"pdfminer extraction failed: {str(e)}")
        
        # If all text extraction fails, return empty
        logger.error("All PDF text extraction methods failed")
        return ""
    
    def extract_metadata(self, filepath: str) -> dict:
        """Extract PDF metadata"""
        metadata = {
            'title': '',
            'author': '',
            'subject': '',
            'creator': '',
            'producer': '',
            'creation_date': None,
            'modification_date': None
        }
        
        try:
            import PyPDF2
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                if pdf_reader.metadata:
                    metadata = {
                        'title': pdf_reader.metadata.get('/Title', ''),
                        'author': pdf_reader.metadata.get('/Author', ''),
                        'subject': pdf_reader.metadata.get('/Subject', ''),
                        'creator': pdf_reader.metadata.get('/Creator', ''),
                        'producer': pdf_reader.metadata.get('/Producer', ''),
                        'creation_date': pdf_reader.metadata.get('/CreationDate', ''),
                        'modification_date': pdf_reader.metadata.get('/ModDate', '')
                    }
        except Exception as e:
            logger.warning(f"Metadata extraction failed: {str(e)}")
        
        return metadata
    
    def get_page_count(self, filepath: str) -> int:
        """Get number of pages in PDF"""
        try:
            import PyPDF2
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                return len(pdf_reader.pages)
        except:
            return 0
