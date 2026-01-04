"""
Configuration file for NCERT Doubt-Solver Ingestion Pipeline

Modify these settings to customize the pipeline for different NCERT books.
"""

# PDF Input Configuration - Chapter-wise PDFs
PDF_CONFIG = {
    "base_dir": "data/raw_books",  # Base directory containing chapter PDFs
    # PDFs will be auto-discovered in subdirectories
    # Example: data/raw_books/class_6/science/english/ch01_chapter_name.pdf
}

# Text Extraction Settings
EXTRACTION_CONFIG = {
    "min_text_threshold": 50,  # Minimum characters to consider page as text-based
}

# OCR Settings
OCR_CONFIG = {
    "language": "eng",  # Tesseract language code (eng, hin, tam, etc.)
    "dpi": 300,  # Image quality for OCR (higher = better quality, slower)
}

# Chunking Settings
CHUNKING_CONFIG = {
    "min_chunk_words": 300,
    "max_chunk_words": 400,
}

# Output Configuration
OUTPUT_CONFIG = {
    "output_dir": "data/cleaned_text",
    "save_intermediates": True,  # Save intermediate processing steps
}

# Advanced Settings
ADVANCED_CONFIG = {
    "enable_progress_bars": True,
    "verbose_logging": True,
}
