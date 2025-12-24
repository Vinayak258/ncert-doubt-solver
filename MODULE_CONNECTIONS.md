# 🔗 Module Connection Guide

## How the Modules Work Together

This document explains how the four core ingestion modules connect and pass data through the pipeline.

## Data Flow Overview

```
PDF Input → PDFTextExtractor → OCRPipeline (if needed) → TextCleaner → SemanticChunker → chunks.json
```

## Module Connections

### 1️⃣ PDFTextExtractor → OCRPipeline

**Connection**: Page numbers requiring OCR

```python
from ingestion.pdf_to_text import PDFTextExtractor
from ingestion.ocr_pipeline import OCRPipeline

# Extract text
extractor = PDFTextExtractor()
extracted_pages = extractor.extract_text_from_pdf("input.pdf")

# Get pages needing OCR
ocr_page_numbers = extractor.get_ocr_pages(extracted_pages)

# Process OCR pages
ocr_pipeline = OCRPipeline()
ocr_results = ocr_pipeline.process_ocr_pages("input.pdf", ocr_page_numbers)

# Merge results back
for page in extracted_pages:
    for ocr_page in ocr_results:
        if page['page'] == ocr_page['page']:
            page['text'] = ocr_page['text']
```

**Data Format**:
```json
{
  "page": 5,
  "text": "Extracted or OCR text",
  "needs_ocr": false
}
```

### 2️⃣ OCRPipeline → TextCleaner

**Connection**: Merged page data

```python
from ingestion.text_cleaner import TextCleaner

# Clean all pages (both extracted and OCR)
cleaner = TextCleaner()
cleaned_pages = cleaner.clean_pages(extracted_pages)
```

**Data Format** (same structure, cleaned text):
```json
{
  "page": 5,
  "text": "Cleaned and normalized text",
  "needs_ocr": false
}
```

### 3️⃣ TextCleaner → SemanticChunker

**Connection**: Cleaned page data

```python
from ingestion.chunker import SemanticChunker

# Create chunks with metadata
chunker = SemanticChunker(
    class_num=6,
    subject="Science",
    language="English"
)

chunks = chunker.chunk_pages(
    cleaned_pages,
    chapter_mapping={1: "Chapter 1", 10: "Chapter 2"}
)
```

**Output Format**:
```json
{
  "chunk_id": "uuid",
  "class": 6,
  "subject": "Science",
  "chapter": "Chapter Name",
  "page": 5,
  "language": "English",
  "text": "Semantic chunk content...",
  "word_count": 350
}
```

## Complete Pipeline Example

```python
from ingestion import PDFTextExtractor, OCRPipeline, TextCleaner, SemanticChunker

# 1. Extract text
extractor = PDFTextExtractor()
pages = extractor.extract_text_from_pdf("data/raw_books/book.pdf")

# 2. Process OCR pages
ocr_pages = extractor.get_ocr_pages(pages)
if ocr_pages:
    ocr = OCRPipeline()
    ocr_results = ocr.process_ocr_pages("data/raw_books/book.pdf", ocr_pages)
    # Merge OCR results into pages
    for page in pages:
        for ocr_page in ocr_results:
            if page['page'] == ocr_page['page']:
                page['text'] = ocr_page['text']

# 3. Clean text
cleaner = TextCleaner()
cleaned = cleaner.clean_pages(pages)

# 4. Create chunks
chunker = SemanticChunker(class_num=6, subject="Science")
chunks = chunker.chunk_pages(cleaned)

# 5. Save output
chunker.save_chunks(chunks, "data/cleaned_text/chunks.json")
```

## Key Design Decisions

### Why Separate Modules?

1. **Testability**: Each module can be tested independently
2. **Reusability**: Modules can be used in different pipelines
3. **Maintainability**: Changes to one module don't affect others
4. **Debugging**: Easy to identify which stage has issues

### Data Format Consistency

All modules use the same JSON structure for page data:
- `page`: Page number (int)
- `text`: Text content (str)
- `needs_ocr`: OCR flag (bool)

This consistency makes module integration seamless.

### Error Handling

Each module handles its own errors:
- **PDFTextExtractor**: File not found, corrupt PDFs
- **OCRPipeline**: Image conversion failures, Tesseract errors
- **TextCleaner**: Empty text, encoding issues
- **SemanticChunker**: Insufficient text for chunking

## Customization Points

### 1. Change OCR Threshold
```python
extractor = PDFTextExtractor(min_text_threshold=100)  # Default: 50
```

### 2. Adjust Chunk Size
```python
chunker = SemanticChunker(
    min_chunk_words=200,  # Default: 300
    max_chunk_words=500   # Default: 400
)
```

### 3. OCR Language
```python
ocr = OCRPipeline(language='hin')  # For Hindi
```

### 4. Custom Chapter Mapping
```python
chapters = {
    1: "Introduction",
    15: "Advanced Topics",
    30: "Conclusion"
}
chunks = chunker.chunk_pages(cleaned, chapter_mapping=chapters)
```

## Intermediate Outputs

The orchestrator (`run_ingestion.py`) saves intermediate files:

1. `01_extracted_pages.json` - After PDF extraction
2. `02_merged_pages.json` - After OCR processing
3. `03_cleaned_pages.json` - After text cleaning
4. `chunks.json` - Final output

This allows you to:
- Debug specific stages
- Resume processing from any point
- Compare before/after at each stage

## Performance Considerations

### Bottlenecks

1. **OCR Processing**: Slowest step (~20-30 sec/page)
2. **PDF Extraction**: Fast (~0.2 sec/page)
3. **Text Cleaning**: Very fast (~0.03 sec/page)
4. **Chunking**: Fast (~0.07 sec/page)

### Optimization Tips

- Process OCR pages in parallel (future enhancement)
- Lower OCR DPI for faster processing (trade-off: accuracy)
- Batch process multiple PDFs
- Cache OCR results to avoid reprocessing

## Extending the Pipeline

### Adding New Modules

To add a new processing step:

1. Create new module in `ingestion/`
2. Follow the same data format (page dictionaries)
3. Add to `__init__.py`
4. Integrate in `run_ingestion.py`

Example: Adding a spell checker
```python
# ingestion/spell_checker.py
class SpellChecker:
    def check_pages(self, pages):
        # Process pages
        return corrected_pages

# In run_ingestion.py
spell_checker = SpellChecker()
corrected = spell_checker.check_pages(cleaned_pages)
chunks = chunker.chunk_pages(corrected)
```

---

**This modular design makes the pipeline flexible, maintainable, and production-ready!**
