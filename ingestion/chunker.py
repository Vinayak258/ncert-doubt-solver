"""
Semantic Chunking Module

This module converts cleaned text into semantic chunks with rich metadata
for downstream RAG processing.
"""

import json
import uuid
import re
from pathlib import Path
from typing import List, Dict, Optional
from langdetect import detect


class SemanticChunker:
    """Create semantic chunks from cleaned text with metadata."""
    
    def __init__(
        self,
        min_chunk_words: int = 300,
        max_chunk_words: int = 400,
        class_num: int = 6,
        subject: str = "Science",
        language: str = "English"
    ):
        """
        Initialize the semantic chunker.
        
        Args:
            min_chunk_words: Minimum words per chunk
            max_chunk_words: Maximum words per chunk
            class_num: NCERT class number
            subject: Subject name
            language: Language of the content
        """
        self.min_chunk_words = min_chunk_words
        self.max_chunk_words = max_chunk_words
        self.class_num = class_num
        self.subject = subject
        self.language = language
    

    
    def split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        # Split on sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def create_chunks(self, text: str, page_num: int, chapter: Optional[str] = None) -> List[str]:
        """
        Create semantic chunks from text.
        
        Args:
            text: Input text
            page_num: Page number
            chapter: Chapter name (optional)
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        sentences = self.split_into_sentences(text)
        chunks = []
        current_chunk = []
        current_word_count = 0
        
        for sentence in sentences:
            sentence_words = len(sentence.split())
            
            # Check if adding this sentence would exceed max words
            if current_word_count + sentence_words > self.max_chunk_words and current_word_count >= self.min_chunk_words:
                # Save current chunk and start new one
                chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_word_count = sentence_words
            else:
                # Add sentence to current chunk
                current_chunk.append(sentence)
                current_word_count += sentence_words
        
        # Add remaining chunk if it meets minimum requirement
        if current_chunk and current_word_count >= self.min_chunk_words:
            chunks.append(' '.join(current_chunk))
        elif current_chunk and chunks:
            # If last chunk is too small, merge with previous
            chunks[-1] += ' ' + ' '.join(current_chunk)
        elif current_chunk:
            # If it's the only chunk, keep it even if small
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def chunk_pages(self, pages: List[Dict], chapter_mapping: Optional[Dict[int, str]] = None) -> List[Dict]:
        """
        Convert pages into semantic chunks with metadata.
        
        Args:
            pages: List of page dictionaries with 'text' and 'page' fields
            chapter_mapping: Optional mapping of page numbers to chapter names
            
        Returns:
            List of chunk dictionaries with metadata
        """
        all_chunks = []
        current_chapter = None
        
        print(f"Creating semantic chunks from {len(pages)} pages...")
        
        for page in pages:
            page_num = page.get('page', 0)
            text = page.get('text', '')
            
            if not text:
                continue
            
            # Use provided chapter mapping (from filename)
            if chapter_mapping and page_num in chapter_mapping:
                current_chapter = chapter_mapping[page_num]
            
            # Create chunks for this page
            page_chunks = self.create_chunks(text, page_num, current_chapter)
            
            # Add metadata to each chunk
            for chunk_text in page_chunks:
                chunk_data = {
                    "chunk_id": str(uuid.uuid4()),
                    "class": self.class_num,
                    "subject": self.subject,
                    "chapter": current_chapter if current_chapter else "Unknown",
                    "page": page_num,
                    "language": self.language,
                    "text": chunk_text,
                    "word_count": len(chunk_text.split())
                }
                all_chunks.append(chunk_data)
        
        print(f"Created {len(all_chunks)} semantic chunks.")
        
        return all_chunks
    
    def save_chunks(self, chunks: List[Dict], output_path: str):
        """
        Save chunks to a JSON file.
        
        Args:
            chunks: List of chunk dictionaries
            output_path: Path to save the JSON output
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
        
        print(f"Saved {len(chunks)} chunks to {output_path}")
        
        # Print statistics
        total_words = sum(chunk['word_count'] for chunk in chunks)
        avg_words = total_words / len(chunks) if chunks else 0
        print(f"\nChunk Statistics:")
        print(f"  Total chunks: {len(chunks)}")
        print(f"  Average words per chunk: {avg_words:.1f}")
        print(f"  Total words: {total_words}")


def main():
    """Example usage of SemanticChunker."""
    # Example: Load cleaned pages
    input_path = "data/cleaned_text/cleaned_pages.json"
    output_path = "data/cleaned_text/chunks.json"
    
    with open(input_path, 'r', encoding='utf-8') as f:
        pages = json.load(f)
    
    # Optional: Define chapter mapping if known
    chapter_mapping = {
        1: "Nutrition in Plants",
        15: "Light",
        30: "Forests: Our Lifeline"
        # Add more mappings as needed
    }
    
    chunker = SemanticChunker(
        min_chunk_words=300,
        max_chunk_words=400,
        class_num=6,
        subject="Science",
        language="English"
    )
    
    # Create chunks
    chunks = chunker.chunk_pages(pages, chapter_mapping)
    
    # Save results
    chunker.save_chunks(chunks, output_path)


if __name__ == "__main__":
    main()
