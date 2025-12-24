"""
NCERT Doubt-Solver Ingestion Package

This package contains modules for processing NCERT PDFs into structured chunks.
"""

from .pdf_to_text import PDFTextExtractor
from .ocr_pipeline import OCRPipeline
from .text_cleaner import TextCleaner
from .chunker import SemanticChunker
from .utils import parse_filename, get_chapter_pdfs

__all__ = [
    'PDFTextExtractor',
    'OCRPipeline',
    'TextCleaner',
    'SemanticChunker',
    'parse_filename',
    'get_chapter_pdfs'
]
