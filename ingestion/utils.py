"""
Utility functions for the ingestion pipeline.

This module provides filename-based metadata extraction for NCERT PDFs
following the convention: c<Class>_<Subject>_<Language>_ch<Chapter>.pdf
"""

import re
from pathlib import Path
from typing import Tuple


def parse_filename(filename: str) -> Tuple[int, str, str, str]:
    """
    Extract metadata from PDF filename.
    
    Expected format: c<Class>_<Subject>_<Language>_ch<Chapter>.pdf
    
    Args:
        filename: PDF filename (e.g., "c06_sci_eng_ch01.pdf")
        
    Returns:
        Tuple of (class_number, subject, language, chapter_name)
        
    Examples:
        >>> parse_filename("c06_sci_eng_ch01.pdf")
        (6, 'Science', 'English', 'Chapter 1')
        >>> parse_filename("c10_math_hin_ch02.pdf")
        (10, 'Math', 'Hindi', 'Chapter 2')
        >>> parse_filename("c08_sst_eng_ch03.pdf")
        (8, 'SST', 'English', 'Chapter 3')
    """
    # Remove .pdf extension if present
    name = filename.replace(".pdf", "").replace(".PDF", "")
    
    # Parse pattern: c<Class>_<Subject>_<Language>_ch<Chapter>
    pattern = r'^c(\d+)_([a-z]+)_([a-z]+)_ch(\d+)$'
    match = re.match(pattern, name, re.IGNORECASE)
    
    if not match:
        raise ValueError(
            f"Filename '{filename}' does not match expected format: "
            f"c<Class>_<Subject>_<Language>_ch<Chapter>.pdf\n"
            f"Example: c06_sci_eng_ch01.pdf"
        )
    
    class_num = int(match.group(1))
    subject_code = match.group(2).lower()
    language_code = match.group(3).lower()
    chapter_num = int(match.group(4))
    
    # Map subject codes to full names
    subject_mapping = {
        'sci': 'Science',
        'math': 'Math',
        'sst': 'SST'
    }
    
    # Map language codes to full names
    language_mapping = {
        'eng': 'English',
        'hin': 'Hindi'
    }
    
    subject = subject_mapping.get(subject_code, subject_code.title())
    language = language_mapping.get(language_code, language_code.title())
    chapter = f"Chapter {chapter_num}"
    
    return class_num, subject, language, chapter


def get_chapter_pdfs(base_dir: str) -> list:
    """
    Find all chapter PDF files in the directory structure.
    
    Recursively searches for all PDF files in class folders (c01, c02, etc.)
    
    Args:
        base_dir: Base directory to search (e.g., "data/raw_books")
        
    Returns:
        List of Path objects for all PDF files found, sorted by filename
        
    Examples:
        >>> pdfs = get_chapter_pdfs("data/raw_books")
        >>> # Returns all PDFs from c06/, c08/, c10/, etc.
    """
    base_path = Path(base_dir)
    
    if not base_path.exists():
        return []
    
    # Find all PDF files recursively
    pdf_files = list(base_path.rglob("*.pdf")) + list(base_path.rglob("*.PDF"))
    
    # Sort by filename for consistent processing order
    pdf_files.sort(key=lambda p: p.name)
    
    return pdf_files


if __name__ == "__main__":
    # Test the functions
    print("Testing parse_filename:")
    test_files = [
        "c06_sci_eng_ch01.pdf",
        "c06_sci_hin_ch03.pdf",
        "c08_sst_eng_ch02.pdf",
        "c10_math_hin_ch02.pdf"
    ]
    
    for filename in test_files:
        try:
            class_num, subject, language, chapter = parse_filename(filename)
            print(f"  {filename}")
            print(f"    -> Class {class_num}, {subject}, {language}, {chapter}")
        except ValueError as e:
            print(f"  {filename} -> ERROR: {e}")
    
    print("\nTesting get_chapter_pdfs:")
    pdfs = get_chapter_pdfs("data/raw_books")
    print(f"  Found {len(pdfs)} PDF(s)")
    for pdf in pdfs[:5]:  # Show first 5
        print(f"    • {pdf.name}")
