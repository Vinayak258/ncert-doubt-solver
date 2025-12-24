# 📚 Chapter-wise PDF Setup Guide

This guide shows you how to organize your NCERT chapter PDFs for the ingestion pipeline.

## 📁 Directory Structure

The pipeline expects PDFs organized in this structure:

```
data/raw_books/
└── class_X/
    └── subject/
        └── language/
            ├── ch01_chapter_name.pdf
            ├── ch02_chapter_name.pdf
            └── ch03_chapter_name.pdf
```

## 🎯 Real Example: Class 6 Science (English)

```
data/raw_books/class_6/science/english/
├── ch01_food_where_does_it_come_from.pdf
├── ch02_components_of_food.pdf
├── ch03_fibre_to_fabric.pdf
├── ch04_sorting_materials_into_groups.pdf
├── ch05_separation_of_substances.pdf
├── ch06_changes_around_us.pdf
├── ch07_getting_to_know_plants.pdf
├── ch08_body_movements.pdf
├── ch09_living_organisms_and_their_surroundings.pdf
├── ch10_motion_and_measurement_of_distances.pdf
├── ch11_light_shadows_and_reflections.pdf
├── ch12_electricity_and_circuits.pdf
├── ch13_fun_with_magnets.pdf
├── ch14_water.pdf
├── ch15_air_around_us.pdf
└── ch16_garbage_in_garbage_out.pdf
```

## 📝 Filename Format Rules

### ✅ Correct Format

```
chXX_chapter_name_with_underscores.pdf
```

**Examples**:
- `ch01_food_where_does_it_come_from.pdf`
- `ch02_components_of_food.pdf`
- `ch15_air_around_us.pdf`

### ❌ Incorrect Formats

```
# Missing chapter number prefix
food_where_does_it_come_from.pdf

# Spaces instead of underscores
ch01 food where does it come from.pdf

# Wrong chapter number format
chapter01_food_where_does_it_come_from.pdf
```

## 🔄 How Chapter Names Are Extracted

The pipeline automatically converts filenames to chapter names:

| Filename | Extracted Chapter Name |
|----------|------------------------|
| `ch01_food_where_does_it_come_from.pdf` | Food Where Does It Come From |
| `ch02_components_of_food.pdf` | Components Of Food |
| `ch15_air_around_us.pdf` | Air Around Us |

**Conversion Process**:
1. Remove `.pdf` extension
2. Remove `chXX_` prefix
3. Replace underscores with spaces
4. Convert to Title Case

## 🌍 Multiple Languages Example

You can organize multiple language versions:

```
data/raw_books/class_6/science/
├── english/
│   ├── ch01_food_where_does_it_come_from.pdf
│   └── ch02_components_of_food.pdf
├── hindi/
│   ├── ch01_भोजन_कहाँ_से_आता_है.pdf
│   └── ch02_भोजन_के_घटक.pdf
└── tamil/
    ├── ch01_உணவு_எங்கிருந்து_வருகிறது.pdf
    └── ch02_உணவின்_கூறுகள்.pdf
```

## 🚀 Quick Setup Commands

### Windows (PowerShell)

```powershell
# Create directory structure
New-Item -ItemType Directory -Force -Path "data\raw_books\class_6\science\english"

# Navigate to the directory
cd data\raw_books\class_6\science\english

# Place your PDFs here
```

### Linux/macOS

```bash
# Create directory structure
mkdir -p data/raw_books/class_6/science/english

# Navigate to the directory
cd data/raw_books/class_6/science/english

# Place your PDFs here
```

## 📥 Downloading NCERT PDFs

1. Visit: https://ncert.nic.in/textbook.php
2. Select your class and subject
3. Download individual chapter PDFs
4. Rename them to follow the `chXX_chapter_name.pdf` format
5. Place in the appropriate directory

## ✅ Verification

After placing your PDFs, verify the structure:

```bash
# List all PDFs
python -c "from ingestion.utils import get_chapter_pdfs; print('\n'.join(str(p) for p in get_chapter_pdfs('data/raw_books')))"
```

Expected output:
```
data\raw_books\class_6\science\english\ch01_food_where_does_it_come_from.pdf
data\raw_books\class_6\science\english\ch02_components_of_food.pdf
...
```

## 🔧 Testing Chapter Name Extraction

Test if your filenames will be parsed correctly:

```python
from ingestion.utils import extract_chapter_name

# Test your filename
filename = "ch01_food_where_does_it_come_from.pdf"
chapter = extract_chapter_name(filename)
print(f"{filename} → {chapter}")
```

## 🎓 Best Practices

1. **Consistent Naming**: Use the same format for all chapters
2. **Sequential Numbering**: Use `ch01`, `ch02`, etc. (with leading zeros)
3. **Descriptive Names**: Use full chapter names from NCERT
4. **No Special Characters**: Stick to letters, numbers, and underscores
5. **One Chapter Per PDF**: Don't merge multiple chapters

## 🐛 Common Issues

### Issue: "No PDF files found"

**Check**:
- Directory structure matches expected format
- PDFs are in the correct location
- Filenames end with `.pdf` (case-sensitive on Linux)

### Issue: Wrong chapter names in output

**Check**:
- Filenames follow `chXX_chapter_name.pdf` format
- Underscores used instead of spaces
- No special characters in filenames

### Issue: Metadata (class/subject/language) incorrect

**Check**:
- Directory structure: `class_X/subject/language/`
- Use `class_6` not `class6`
- Subject and language folders are lowercase

---

**Ready to process your chapters!** 🚀

Once your PDFs are organized, simply run:

```bash
python scripts/run_ingestion.py
```
