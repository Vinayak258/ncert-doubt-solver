"""
Build Vector Index from Chunks

This script:
1. Loads chunks.json from Day-1 ingestion
2. Generates embeddings for each chunk
3. Builds FAISS index with metadata
4. Saves index and metadata to disk
"""

import sys
import json
from pathlib import Path
from tqdm import tqdm

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from embeddings.embedder import embed_texts, get_embedding_dimension
from vector_store.faiss_index import create_index, save_index


def load_chunks(chunks_path: str) -> list:
    """
    Load chunks from JSON file.
    
    Args:
        chunks_path: Path to chunks.json
        
    Returns:
        List of chunk dictionaries
    """
    print(f"Loading chunks from: {chunks_path}")
    
    with open(chunks_path, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    print(f"✓ Loaded {len(chunks)} chunks")
    return chunks


def build_vector_index(
    chunks_path: str = "data/cleaned_text/chunks.json",
    output_dir: str = "data/vector_store",
    batch_size: int = 32
):
    """
    Build FAISS vector index from chunks.
    
    Args:
        chunks_path: Path to chunks.json
        output_dir: Directory to save index and metadata
        batch_size: Batch size for embedding generation
    """
    print("=" * 80)
    print("BUILDING VECTOR INDEX")
    print("=" * 80)
    
    # Load chunks
    chunks = load_chunks(chunks_path)
    
    if not chunks:
        print("❌ ERROR: No chunks found!")
        sys.exit(1)
    
    # Extract texts for embedding
    print("\nExtracting text from chunks...")
    texts = [chunk['text'] for chunk in chunks]
    print(f"✓ Extracted {len(texts)} texts")
    
    # Generate embeddings
    print(f"\nGenerating embeddings (batch_size={batch_size})...")
    print(f"Embedding dimension: {get_embedding_dimension()}")
    embeddings = embed_texts(texts, batch_size=batch_size, show_progress=True)
    print(f"✓ Generated embeddings with shape: {embeddings.shape}")
    
    # Prepare metadata (exclude text to save space)
    print("\nPreparing metadata...")
    metadata = []
    for chunk in chunks:
        meta = {
            'chunk_id': chunk['chunk_id'],
            'class': chunk['class'],
            'subject': chunk['subject'],
            'language': chunk['language'],
            'chapter': chunk['chapter'],
            'page': chunk['page'],
            'text': chunk['text'],  # Keep text for retrieval
            'word_count': chunk.get('word_count', 0)
        }
        metadata.append(meta)
    
    print(f"✓ Prepared metadata for {len(metadata)} chunks")
    
    # Create FAISS index
    print("\nCreating FAISS index...")
    index = create_index(embeddings)
    print(f"✓ Created FAISS index with {index.ntotal} vectors")
    
    # Save index and metadata
    print(f"\nSaving to: {output_dir}")
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    save_index(index, metadata, str(output_path))
    
    # Print summary
    print("\n" + "=" * 80)
    print("INDEX BUILD COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print(f"\nStatistics:")
    print(f"  Total chunks indexed: {len(chunks)}")
    print(f"  Embedding dimension: {embeddings.shape[1]}")
    print(f"  Index file: {output_path / 'faiss.index'}")
    print(f"  Metadata file: {output_path / 'metadata.pkl'}")
    
    # Print sample metadata distribution
    print(f"\nMetadata Distribution:")
    
    # Classes
    classes = {}
    for meta in metadata:
        cls = meta['class']
        classes[cls] = classes.get(cls, 0) + 1
    print(f"  Classes: {dict(sorted(classes.items()))}")
    
    # Subjects
    subjects = {}
    for meta in metadata:
        subj = meta['subject']
        subjects[subj] = subjects.get(subj, 0) + 1
    print(f"  Subjects: {subjects}")
    
    # Languages
    languages = {}
    for meta in metadata:
        lang = meta['language']
        languages[lang] = languages.get(lang, 0) + 1
    print(f"  Languages: {languages}")
    
    print("\n✓ Ready for retrieval!")
    print("=" * 80)


def main():
    """Main entry point."""
    # Default paths
    chunks_path = "data/cleaned_text/chunks.json"
    output_dir = "data/vector_store"
    
    # Check if chunks file exists
    if not Path(chunks_path).exists():
        print(f"❌ ERROR: Chunks file not found: {chunks_path}")
        print("\nPlease run Day-1 ingestion first:")
        print("  python scripts/run_ingestion.py")
        sys.exit(1)
    
    # Build index
    build_vector_index(
        chunks_path=chunks_path,
        output_dir=output_dir,
        batch_size=32
    )


if __name__ == "__main__":
    main()
