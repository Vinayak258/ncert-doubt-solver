"""
Text Cleaning Module

This module normalizes and cleans extracted text from PDFs and OCR,
removing noise while preserving academic formatting.
"""

import re
import json
from pathlib import Path
from typing import List, Dict


class TextCleaner:
    """Clean and normalize extracted text from PDFs and OCR."""
    
    def __init__(self):
        """Initialize the text cleaner with common patterns."""
        # Common NCERT footer/header patterns
        self.header_footer_patterns = [
            r'^\d+\s*$',  # Page numbers alone
            r'^NCERT.*$',  # NCERT headers
            r'^Chapter \d+.*$',  # Chapter headers (when repeated)
            r'^\d{4}-\d{2}$',  # Academic year patterns
        ]
    
    def remove_extra_whitespace(self, text: str) -> str:
        """
        Remove excessive whitespace while preserving paragraph structure.
        
        Args:
            text: Input text
            
        Returns:
            Text with normalized whitespace
        """
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        # Replace multiple newlines with double newline (paragraph break)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove spaces at start/end of lines
        lines = [line.strip() for line in text.split('\n')]
        
        return '\n'.join(lines)
    
    def fix_broken_lines(self, text: str) -> str:
        """
        Fix broken line breaks that split words or sentences.
        
        Args:
            text: Input text
            
        Returns:
            Text with fixed line breaks
        """
        # Join lines that end with lowercase and next starts with lowercase
        # (likely a broken sentence)
        lines = text.split('\n')
        fixed_lines = []
        
        i = 0
        while i < len(lines):
            current_line = lines[i].strip()
            
            # Check if we should merge with next line
            if i < len(lines) - 1:
                next_line = lines[i + 1].strip()
                
                # Merge if current line ends with lowercase and next starts with lowercase
                # or if current line ends with hyphen (word break)
                if current_line and next_line:
                    if current_line[-1].islower() and next_line[0].islower():
                        # Merge lines
                        if current_line.endswith('-'):
                            # Remove hyphen for word breaks
                            current_line = current_line[:-1] + next_line
                        else:
                            current_line = current_line + ' ' + next_line
                        i += 1  # Skip next line as it's merged
            
            if current_line:
                fixed_lines.append(current_line)
            
            i += 1
        
        return '\n'.join(fixed_lines)
    
    def remove_headers_footers(self, text: str) -> str:
        """
        Remove common headers and footers from NCERT books.
        
        Args:
            text: Input text
            
        Returns:
            Text with headers/footers removed
        """
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Check against header/footer patterns
            is_header_footer = False
            for pattern in self.header_footer_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    is_header_footer = True
                    break
            
            if not is_header_footer and line:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def preserve_academic_formatting(self, text: str) -> str:
        """
        Preserve important academic formatting like bullet points, numbering.
        
        Args:
            text: Input text
            
        Returns:
            Text with preserved formatting
        """
        # Ensure bullet points have proper spacing
        text = re.sub(r'([•●○])', r'\n\1 ', text)
        
        # Ensure numbered lists have proper spacing
        text = re.sub(r'(\d+\.)\s*', r'\n\1 ', text)
        
        # Clean up any excessive newlines created
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text
    
    def clean_text(self, text: str) -> str:
        """
        Apply all cleaning operations to text.
        
        Args:
            text: Raw input text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Apply cleaning steps in order
        text = self.remove_extra_whitespace(text)
        text = self.fix_broken_lines(text)
        text = self.remove_headers_footers(text)
        text = self.preserve_academic_formatting(text)
        
        # Final whitespace cleanup
        text = text.strip()
        
        return text
    
    def clean_pages(self, pages: List[Dict]) -> List[Dict]:
        """
        Clean text from all pages.
        
        Args:
            pages: List of page dictionaries with 'text' field
            
        Returns:
            List of page dictionaries with cleaned text
        """
        cleaned_pages = []
        
        print(f"Cleaning text from {len(pages)} pages...")
        
        for page in pages:
            cleaned_page = page.copy()
            cleaned_page['text'] = self.clean_text(page.get('text', ''))
            cleaned_pages.append(cleaned_page)
        
        print("Text cleaning completed.")
        
        return cleaned_pages
    
    def save_cleaned_pages(self, cleaned_pages: List[Dict], output_path: str):
        """
        Save cleaned pages to a JSON file.
        
        Args:
            cleaned_pages: List of cleaned page dictionaries
            output_path: Path to save the JSON output
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(cleaned_pages, f, ensure_ascii=False, indent=2)
        
        print(f"Saved cleaned text to {output_path}")


def main():
    """Example usage of TextCleaner."""
    # Example: Load extracted pages
    input_path = "data/ocr_text/extracted_pages.json"
    output_path = "data/cleaned_text/cleaned_pages.json"
    
    with open(input_path, 'r', encoding='utf-8') as f:
        pages = json.load(f)
    
    cleaner = TextCleaner()
    
    # Clean all pages
    cleaned_pages = cleaner.clean_pages(pages)
    
    # Save results
    cleaner.save_cleaned_pages(cleaned_pages, output_path)


if __name__ == "__main__":
    main()
