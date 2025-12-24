"""
Main Ingestion Pipeline Script - Chapter-wise PDF Support

This script orchestrates the complete data ingestion pipeline for multiple chapter PDFs:
1. Discover all chapter PDFs in directory structure
2. For each PDF:
   - Extract text from pages
   - Run OCR on scanned pages
   - Clean extracted text
   - Create semantic chunks with metadata
3. Aggregate all chunks
4. Save final output
"""

import sys
import json
from pathlib import Path
from tqdm import tqdm

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from ingestion.pdf_to_text import PDFTextExtractor
from ingestion.ocr_pipeline import OCRPipeline
from ingestion.text_cleaner import TextCleaner
from ingestion.chunker import SemanticChunker
from ingestion.utils import parse_filename, get_chapter_pdfs


class MultiPDFIngestionPipeline:
    """Complete data ingestion pipeline for multiple chapter-wise NCERT PDFs."""
    
    def __init__(
        self,
        base_dir: str = "data/raw_books",
        output_dir: str = "data/cleaned_text",
        save_intermediates: bool = True
    ):
        """
        Initialize the multi-PDF ingestion pipeline.
        
        Args:
            base_dir: Base directory containing chapter PDFs
            output_dir: Directory to save output files
            save_intermediates: Whether to save intermediate processing steps
        """
        self.base_dir = Path(base_dir)
        self.output_dir = Path(output_dir)
        self.save_intermediates = save_intermediates
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.pdf_extractor = PDFTextExtractor(min_text_threshold=50)
        self.ocr_pipeline = OCRPipeline(language='eng', dpi=300)
        self.text_cleaner = TextCleaner()
    
    def process_single_pdf(self, pdf_path: Path) -> list:
        """
        Process a single PDF file through the complete pipeline.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of chunk dictionaries with metadata
        """
        # Extract metadata from filename
        class_num, subject, language, chapter_name = parse_filename(pdf_path.name)
        
        print(f"\n{'='*80}")
        print(f"Processing: {pdf_path.name}")
        print(f"Metadata: Class {class_num}, {subject}, {language}, {chapter_name}")
        print(f"{'='*80}")
        
        # Step 1: Extract text from PDF
        print("\n[1/4] Extracting text from PDF...")
        extracted_pages = self.pdf_extractor.extract_text_from_pdf(str(pdf_path))
        
        # Step 2: Process OCR pages
        print("\n[2/4] Processing OCR pages...")
        ocr_page_numbers = self.pdf_extractor.get_ocr_pages(extracted_pages)
        
        if ocr_page_numbers:
            print(f"Found {len(ocr_page_numbers)} pages requiring OCR")
            ocr_results = self.ocr_pipeline.process_ocr_pages(
                str(pdf_path),
                ocr_page_numbers
            )
            
            # Merge OCR results
            ocr_dict = {page['page']: page for page in ocr_results}
            for page in extracted_pages:
                if page['page'] in ocr_dict:
                    page['text'] = ocr_dict[page['page']]['text']
                    page['needs_ocr'] = False
        else:
            print("No pages require OCR processing")
        
        # Step 3: Clean text
        print("\n[3/4] Cleaning text...")
        cleaned_pages = self.text_cleaner.clean_pages(extracted_pages)
        
        # Step 4: Create semantic chunks
        print("\n[4/4] Creating semantic chunks...")
        chunker = SemanticChunker(
            min_chunk_words=300,
            max_chunk_words=400,
            class_num=class_num,
            subject=subject,
            language=language
        )
        
        # Force chapter name from filename (no auto-detection)
        chapter_mapping = {i: chapter_name for i in range(1, len(cleaned_pages) + 1)}
        chunks = chunker.chunk_pages(cleaned_pages, chapter_mapping)
        
        print(f"✓ Created {len(chunks)} chunks from {pdf_path.name}")
        
        return chunks
    
    def run(self):
        """Execute the complete multi-PDF ingestion pipeline."""
        print("=" * 80)
        print("NCERT DOUBT-SOLVER: MULTI-PDF DATA INGESTION PIPELINE")
        print("=" * 80)
        print(f"\nBase Directory: {self.base_dir}")
        print(f"Output Directory: {self.output_dir}\n")
        
        # Discover all chapter PDFs
        print("Discovering chapter PDFs...")
        pdf_files = get_chapter_pdfs(str(self.base_dir))
        
        if not pdf_files:
            print(f"\n❌ ERROR: No PDF files found in {self.base_dir}")
            print(f"\nExpected structure:")
            print(f"  {self.base_dir}/cXX/cXX_subject_lang_chXX.pdf")
            print(f"\nExample:")
            print(f"  {self.base_dir}/c06/c06_sci_eng_ch01.pdf")
            print(f"  {self.base_dir}/c08/c08_sst_eng_ch02.pdf")
            print(f"  {self.base_dir}/c10/c10_math_hin_ch03.pdf")
            sys.exit(1)
        
        # Load existing chunks if available
        final_output_path = self.output_dir / "chunks.json"
        all_chunks = []
        processed_chapters = set()
        
        if final_output_path.exists():
            print(f"Found existing output at {final_output_path}")
            try:
                with open(final_output_path, 'r', encoding='utf-8') as f:
                    all_chunks = json.load(f)
                print(f"✓ Loaded {len(all_chunks)} existing chunks")
                
                # Identify processed chapters
                for chunk in all_chunks:
                    # Create a unique key for each chapter: (class, subject, language, chapter)
                    # We use metadata from chunks to identify what's already done
                    key = (
                        chunk.get('class'),
                        chunk.get('subject'),
                        chunk.get('language'),
                        chunk.get('chapter')
                    )
                    processed_chapters.add(key)
                
                print(f"✓ Identified {len(processed_chapters)} processed chapters")
                
            except Exception as e:
                print(f"⚠️  Error loading existing chunks: {e}")
                print("Starting fresh...")
                all_chunks = []
        
        # Filter files to process
        files_to_process = []
        skipped_count = 0
        
        print("\nChecking for new files...")
        for pdf_path in pdf_files:
            # Parse filename to get metadata key
            class_num, subject, language, chapter_name = parse_filename(pdf_path.name)
            key = (class_num, subject, language, chapter_name)
            
            if key in processed_chapters:
                skipped_count += 1
            else:
                files_to_process.append(pdf_path)
                print(f"  • New file: {pdf_path.relative_to(self.base_dir)}")
        
        if skipped_count > 0:
            print(f"✓ Skipped {skipped_count} already processed PDFs")
        
        if not files_to_process:
            print("\n✓ No new PDFs to process.")
        else:
            print(f"\nFound {len(files_to_process)} new PDF file(s) to process.")
            
            # Process each new PDF
            new_chunks = []
            
            for pdf_path in tqdm(files_to_process, desc="Processing PDFs", unit="pdf"):
                try:
                    chunks = self.process_single_pdf(pdf_path)
                    new_chunks.extend(chunks)
                    
                    # Add to processed set immediately to avoid duplicates if something crashes/restarts weirdly
                    # (though strictly only one run instance assumed)
                    all_chunks.extend(chunks) # Add to main list as we go
                    
                except Exception as e:
                    print(f"\n⚠️  Error processing {pdf_path.name}: {str(e)}")
                    print("Continuing with next PDF...")
                    continue
            
            # Update file
            if new_chunks:
                print("\n" + "=" * 80)
                print("SAVING FINAL OUTPUT")
                print("=" * 80)
                
                with open(final_output_path, 'w', encoding='utf-8') as f:
                    json.dump(all_chunks, f, ensure_ascii=False, indent=2)
                
                print(f"\n✓ Added {len(new_chunks)} new chunks.")
                print(f"✓ Total chunks saved: {len(all_chunks)} to {final_output_path}")
        
        # Print statistics
        print("\n" + "=" * 80)
        print("PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 80)
        
        # Re-calculate statistics for comprehensive view
        chapters_count = {}
        for chunk in all_chunks:
            chapter = chunk.get('chapter', 'Unknown')
            chapters_count[chapter] = chapters_count.get(chapter, 0) + 1
        
        print(f"\nTotal Chunks in System: {len(all_chunks)}")
        print(f"\nChunks per Chapter:")
        for chapter, count in sorted(chapters_count.items()):
            print(f"  • {chapter}: {count} chunks")
        
        total_words = sum(chunk.get('word_count', 0) for chunk in all_chunks)
        avg_words = total_words / len(all_chunks) if all_chunks else 0
        
        print(f"\nChunk Statistics:")
        print(f"  • Average words per chunk: {avg_words:.1f}")
        print(f"  • Total words: {total_words:,}")
        
        print(f"\n✓ Output ready for RAG pipeline: {final_output_path}")
        print("=" * 80)


def main():
    """Main entry point for the multi-PDF ingestion pipeline."""
    # Configuration
    config = {
        "base_dir": "data/raw_books",
        "output_dir": "data/cleaned_text",
        "save_intermediates": True
    }
    
    # Check if base directory exists
    base_path = Path(config["base_dir"])
    if not base_path.exists():
        print(f"ERROR: Base directory not found: {base_path}")
        print(f"\nCreating directory structure...")
        
        # Create example structure
        example_dir = base_path / "class_6" / "science" / "english"
        example_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"✓ Created: {example_dir}")
        print(f"\nPlease place your chapter PDFs in this directory.")
        print(f"\nExpected filename format:")
        print(f"  c06_sci_eng_ch01.pdf")
        print(f"  c06_sci_hin_ch02.pdf")
        print(f"  c08_sst_eng_ch01.pdf")
        print(f"  c10_math_hin_ch03.pdf")
        print(f"  etc.")
        sys.exit(1)
    
    # Run pipeline
    pipeline = MultiPDFIngestionPipeline(**config)
    pipeline.run()


if __name__ == "__main__":
    main()
