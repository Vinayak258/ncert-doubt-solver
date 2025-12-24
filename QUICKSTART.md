# 🚀 Quick Start Guide - NCERT Doubt-Solver Day-1

This guide will help you set up and run the Day-1 data ingestion pipeline in minutes.

## ⚡ Prerequisites Checklist

Before starting, ensure you have:

- [ ] **Python 3.10+** installed
- [ ] **Tesseract OCR** installed
- [ ] **Poppler** installed (for PDF to image conversion)

### Installing Prerequisites

#### Windows

1. **Tesseract OCR**:
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Install and add to PATH
   - Verify: `tesseract --version`

2. **Poppler**:
   - Download from: https://github.com/oschwartz10612/poppler-windows/releases/
   - Extract and add `bin` folder to PATH
   - Verify: `pdftoppm -v`

#### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr poppler-utils
```

#### macOS

```bash
brew install tesseract poppler
```

## 📦 Installation Steps

### 1. Navigate to Project Directory

```bash
cd "C:\Users\VINAYAK OJHA\OneDrive\Desktop\Intel Ai Project\ncert-doubt-solver"
```

### 2. Create Virtual Environment

```bash
# Create venv
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/macOS)
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

## 📚 Prepare Your Data

1. **Download NCERT PDF** (or use your own):
   - Visit: https://ncert.nic.in/textbook.php
   - Download Class 6 Science (English) or any NCERT book

2. **Place PDF in correct location**:
   ```
   data/raw_books/class6_science_english.pdf
   ```

## ▶️ Run the Pipeline

```bash
python scripts/run_ingestion.py
```

## ✅ Expected Output

The pipeline will:

1. Extract text from PDF pages
2. Run OCR on scanned pages (if any)
3. Clean and normalize text
4. Create semantic chunks
5. Save output to `data/cleaned_text/chunks.json`

### Sample Console Output

```
================================================================================
NCERT DOUBT-SOLVER: DATA INGESTION PIPELINE
================================================================================

[STEP 1/5] Extracting text from PDF...
Processing 150 pages from class6_science_english.pdf...
  Processed 150/150 pages

[STEP 2/5] Processing OCR pages...
Found 5 pages requiring OCR
  OCR processed 5/5 pages

[STEP 3/5] Cleaning text...
Cleaning text from 150 pages...

[STEP 4/5] Creating semantic chunks...
Created 450 semantic chunks.

[STEP 5/5] Saving final output...
Saved 450 chunks to data/cleaned_text/chunks.json

================================================================================
PIPELINE COMPLETED SUCCESSFULLY
================================================================================
```

## 🔍 Verify Output

Check the final output file:

```bash
# View first chunk
python -c "import json; print(json.load(open('data/cleaned_text/chunks.json'))[0])"
```

Expected structure:
```json
{
  "chunk_id": "uuid-here",
  "class": 6,
  "subject": "Science",
  "chapter": "Food: Where Does It Come From?",
  "page": 1,
  "language": "English",
  "text": "Chunk content...",
  "word_count": 350
}
```

## 🐛 Troubleshooting

### Error: `TesseractNotFoundError`

**Solution**: Tesseract not in PATH
```bash
# Windows: Add Tesseract to PATH
# Default location: C:\Program Files\Tesseract-OCR
```

### Error: `pdf2image` errors

**Solution**: Poppler not installed/in PATH
```bash
# Verify poppler installation
pdftoppm -v
```

### Error: PDF not found

**Solution**: Check PDF path in `scripts/run_ingestion.py`
```python
config = {
    "pdf_path": "data/raw_books/YOUR_PDF_NAME.pdf",
    # ...
}
```

## 🎯 Next Steps

After successful completion:

1. ✅ Verify `chunks.json` quality
2. ✅ Review intermediate outputs in `data/cleaned_text/`
3. ✅ Ready for Day-2: Embeddings + FAISS

## 📞 Need Help?

- Check main [README.md](README.md) for detailed documentation
- Review module docstrings in `ingestion/` folder
- Verify all prerequisites are correctly installed

---

**Happy Coding! 🚀**
