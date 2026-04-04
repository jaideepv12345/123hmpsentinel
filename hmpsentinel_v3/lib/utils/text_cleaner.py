# api/utils/text_cleaner.py
"""
Text Cleaner
Cleans and normalizes extracted text from PDFs
"""

import re
import unicodedata


class TextCleaner:
    """
    Cleans and normalizes text extracted from PDF documents.
    Removes common PDF artifacts and normalizes text for analysis.
    """
    
    def __init__(self):
        pass
    
    def clean(self, text: str) -> str:
        """
        Clean and normalize text
        Returns cleaned text suitable for analysis
        """
        if not text:
            return ""
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Normalize unicode
        text = unicodedata.normalize('NFKD', text)
        
        # Remove excessive whitespace
        text = self._normalize_whitespace(text)
        
        # Remove common PDF artifacts
        text = self._remove_artifacts(text)
        
        # Fix common OCR/encoding errors
        text = self._fix_encoding_errors(text)
        
        return text
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace in text"""
        
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        # Replace multiple newlines with double newline
        text = re.sub(r'\n\n+', '\n\n', text)
        
        # Replace multiple tabs with single tab
        text = re.sub(r'\t\t+', '\t', text)
        
        # Remove trailing/leading whitespace from each line
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        return text
    
    def _remove_artifacts(self, text: str) -> str:
        """Remove common PDF artifacts"""
        
        # Remove page numbers (common patterns)
        text = re.sub(r'\n\s*Page\s+\d+\s+of\s+\d+\n', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'\n\s*-\s*\d+\s*-\n', '\n', text)
        
        # Remove headers/footers (common patterns)
        text = re.sub(r'^(?:guilford|county|hazard|mitigation|plan).*\n', '', text, flags=re.IGNORECASE | re.MULTILINE)
        
        # Remove line drawing characters
        text = re.sub(r'[-=_]{3,}', '', text)
        
        # Remove box drawing characters
        text = re.sub(r'[┌┐└┘├┤┬┴┼═║╔╗╚╝╠╣╦╩╬]', '', text)
        
        # Remove bullet points that are just hyphens
        text = re.sub(r'\n\s*-\s*(?=[A-Z])', '\n• ', text)
        
        return text
    
    def _fix_encoding_errors(self, text: str) -> str:
        """Fix common OCR/encoding errors"""
        
        # Fix form feed characters
        text = text.replace('\x0c', '')
        
        # Fix common patterns
        fixes = {
            r'\|': 'l',
            r'\u2026': '...',
        }
        
        for pattern, replacement in fixes.items():
            text = re.sub(pattern, replacement, text)
        
        # Fix common letter duplications (e.g., "hazzard" -> "hazard")
        text = re.sub(r'(.)\1{2,}', r'\1\1', text)
        
        return text
    
    def extract_sentences(self, text: str) -> list:
        """Extract sentences from text"""
        # Simple sentence extraction
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def extract_paragraphs(self, text: str) -> list:
        """Extract paragraphs from text"""
        paragraphs = text.split('\n\n')
        return [p.strip() for p in paragraphs if p.strip()]
