"""
OCR Pipeline Module

This module handles Optical Character Recognition (OCR) for scanned PDF pages
using Tesseract OCR engine.
"""

import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import pdfplumber
import json
import re
from pathlib import Path
from typing import List, Dict
import cv2
import numpy as np


class OCRPipeline:
    """Process scanned PDF pages using OCR."""
    
    def __init__(self, language: str = 'eng', dpi: int = 300):
        """
        Initialize the OCR pipeline.
        
        Args:
            language: Tesseract language code (e.g., 'eng' for English)
            dpi: DPI for PDF to image conversion (higher = better quality)
        """
        self.language = language
        self.dpi = dpi
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image to improve OCR accuracy.
        
        Args:
            image: PIL Image object
            
        Returns:
            Preprocessed PIL Image
        """
        # Convert PIL Image to OpenCV format
        img_array = np.array(image)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Apply thresholding to get binary image
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)
        
        # Convert back to PIL Image
        return Image.fromarray(denoised)
    
    def clean_ocr_text(self, text: str) -> str:
        """
        Clean OCR output to remove common noise.
        
        Args:
            text: Raw OCR text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove isolated special characters
        text = re.sub(r'\s+[^\w\s]\s+', ' ', text)
        
        # Fix common OCR mistakes
        replacements = {
            '|': 'I',
            '0': 'O',  # Only in specific contexts
            '§': 'S',
        }
        
        # Apply replacements cautiously
        for old, new in replacements.items():
            # Only replace if surrounded by letters (to avoid replacing actual numbers)
            text = re.sub(f'(?<=[a-zA-Z]){re.escape(old)}(?=[a-zA-Z])', new, text)
        
        return text.strip()
    
    def ocr_page(self, pdf_path: str, page_num: int) -> str:
        """
        Perform OCR on a specific PDF page.
        
        Args:
            pdf_path: Path to the PDF file
            page_num: Page number to process (1-indexed)
            
        Returns:
            Extracted text from the page
        """
        try:
            # Convert specific page to image
            images = convert_from_path(
                pdf_path,
                dpi=self.dpi,
                first_page=page_num,
                last_page=page_num
            )
            
            if not images:
                return ""
            
            # Preprocess the image
            image = self.preprocess_image(images[0])
            
            # Perform OCR
            text = pytesseract.image_to_string(image, lang=self.language)
            
            # Clean the OCR output
            cleaned_text = self.clean_ocr_text(text)
            
            return cleaned_text
            
        except Exception as e:
            print(f"Error processing page {page_num}: {str(e)}")
            return ""
    
    def process_ocr_pages(self, pdf_path: str, page_numbers: List[int]) -> List[Dict]:
        """
        Process multiple pages that require OCR.
        
        Args:
            pdf_path: Path to the PDF file
            page_numbers: List of page numbers to process
            
        Returns:
            List of dictionaries with page number and OCR text
        """
        ocr_results = []
        total = len(page_numbers)
        
        print(f"Processing {total} pages with OCR...")
        
        for idx, page_num in enumerate(page_numbers, start=1):
            text = self.ocr_page(pdf_path, page_num)
            
            ocr_results.append({
                "page": page_num,
                "text": text,
                "needs_ocr": False  # Already processed
            })
            
            # Progress indicator
            if idx % 5 == 0 or idx == total:
                print(f"  OCR processed {idx}/{total} pages")
        
        return ocr_results
    
    def save_ocr_results(self, ocr_results: List[Dict], output_path: str):
        """
        Save OCR results to a JSON file.
        
        Args:
            ocr_results: List of OCR result dictionaries
            output_path: Path to save the JSON output
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(ocr_results, f, ensure_ascii=False, indent=2)
        
        print(f"Saved OCR results to {output_path}")


def main():
    """Example usage of OCRPipeline."""
    # Example configuration
    pdf_path = "data/raw_books/class6_science_english.pdf"
    output_path = "data/ocr_text/ocr_results.json"
    
    # Pages that need OCR (example)
    ocr_pages = [1, 2, 3]
    
    pipeline = OCRPipeline(language='eng', dpi=300)
    
    # Process OCR pages
    results = pipeline.process_ocr_pages(pdf_path, ocr_pages)
    
    # Save results
    pipeline.save_ocr_results(results, output_path)


if __name__ == "__main__":
    main()
