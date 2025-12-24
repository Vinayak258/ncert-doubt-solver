"""
PDF to Text Extraction Module

This module handles extraction of text from text-based PDF pages.
It automatically detects pages that may need OCR processing.
"""

import pdfplumber
import json
from pathlib import Path
from typing import List, Dict


class PDFTextExtractor:
    """Extract text from PDF files with automatic OCR detection."""
    
    def __init__(self, min_text_threshold: int = 50):
        """
        Initialize the PDF text extractor.
        
        Args:
            min_text_threshold: Minimum character count to consider a page as text-based.
                               Pages below this threshold will be marked for OCR.
        """
        self.min_text_threshold = min_text_threshold
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict]:
        """
        Extract text from all pages in a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of dictionaries containing page number, extracted text, and OCR flag
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        extracted_pages = []
        
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"Processing {total_pages} pages from {pdf_path.name}...")
            
            for page_num, page in enumerate(pdf.pages, start=1):
                # Extract text from the page
                text = page.extract_text()
                
                # Determine if OCR is needed
                needs_ocr = False
                if text is None or len(text.strip()) < self.min_text_threshold:
                    needs_ocr = True
                    text = ""  # Empty text for OCR pages
                
                page_data = {
                    "page": page_num,
                    "text": text.strip() if text else "",
                    "needs_ocr": needs_ocr
                }
                
                extracted_pages.append(page_data)
                
                # Progress indicator
                if page_num % 10 == 0 or page_num == total_pages:
                    print(f"  Processed {page_num}/{total_pages} pages")
        
        return extracted_pages
    
    def save_extracted_text(self, extracted_pages: List[Dict], output_path: str):
        """
        Save extracted text data to a JSON file.
        
        Args:
            extracted_pages: List of page data dictionaries
            output_path: Path to save the JSON output
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(extracted_pages, f, ensure_ascii=False, indent=2)
        
        print(f"Saved extracted text to {output_path}")
    
    def get_ocr_pages(self, extracted_pages: List[Dict]) -> List[int]:
        """
        Get list of page numbers that need OCR processing.
        
        Args:
            extracted_pages: List of page data dictionaries
            
        Returns:
            List of page numbers requiring OCR
        """
        return [page["page"] for page in extracted_pages if page["needs_ocr"]]


def main():
    """Example usage of PDFTextExtractor."""
    # Example configuration
    pdf_path = "data/raw_books/class6_science_english.pdf"
    output_path = "data/ocr_text/extracted_pages.json"
    
    extractor = PDFTextExtractor(min_text_threshold=50)
    
    # Extract text from PDF
    extracted_pages = extractor.extract_text_from_pdf(pdf_path)
    
    # Save results
    extractor.save_extracted_text(extracted_pages, output_path)
    
    # Report OCR requirements
    ocr_pages = extractor.get_ocr_pages(extracted_pages)
    print(f"\nPages requiring OCR: {len(ocr_pages)}")
    if ocr_pages:
        print(f"OCR page numbers: {ocr_pages[:10]}{'...' if len(ocr_pages) > 10 else ''}")


if __name__ == "__main__":
    main()
