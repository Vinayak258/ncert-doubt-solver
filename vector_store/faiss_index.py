"""
FAISS Index Management

This module handles creation, saving, and loading of FAISS vector indices.

FAISS (Facebook AI Similarity Search) is used for efficient similarity search
and clustering of dense vectors.
"""

import faiss
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple


def create_index(embeddings: np.ndarray) -> faiss.IndexFlatL2:
    """
    Create a FAISS index from embeddings.
    
    Uses IndexFlatL2 for exact L2 (Euclidean) distance search.
    This is suitable for datasets with < 1M vectors.
    
    Args:
        embeddings: numpy array of shape (n_vectors, dimension)
        
    Returns:
        FAISS index with all embeddings added
        
    Examples:
        >>> embeddings = np.random.rand(1000, 384)
        >>> index = create_index(embeddings)
        >>> index.ntotal
        1000
    """
    dimension = embeddings.shape[1]
    
    # Create index (L2 distance)
    index = faiss.IndexFlatL2(dimension)
    
    # Add vectors to index
    index.add(embeddings.astype('float32'))
    
    print(f"✓ Created FAISS index: {index.ntotal} vectors, dimension {dimension}")
    
    return index


def save_index(index: faiss.IndexFlatL2, metadata: List[Dict], output_dir: str):
    """
    Save FAISS index and metadata to disk.
    
    Args:
        index: FAISS index to save
        metadata: List of metadata dictionaries (one per vector)
        output_dir: Directory to save files
        
    Files created:
        - faiss.index: Binary FAISS index file
        - metadata.pkl: Pickled metadata list
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save FAISS index
    index_path = output_path / "faiss.index"
    faiss.write_index(index, str(index_path))
    print(f"✓ Saved FAISS index: {index_path}")
    
    # Save metadata
    metadata_path = output_path / "metadata.pkl"
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata, f)
    print(f"✓ Saved metadata: {metadata_path}")
    
    # Verify alignment
    if len(metadata) != index.ntotal:
        raise ValueError(
            f"Metadata length ({len(metadata)}) does not match "
            f"index size ({index.ntotal})"
        )


def load_index(index_dir: str) -> Tuple[faiss.IndexFlatL2, List[Dict]]:
    """
    Load FAISS index and metadata from disk.
    
    Args:
        index_dir: Directory containing index files
        
    Returns:
        Tuple of (index, metadata)
        
    Raises:
        FileNotFoundError: If index files don't exist
        
    Examples:
        >>> index, metadata = load_index("data/vector_store")
        >>> print(f"Loaded {index.ntotal} vectors")
    """
    index_path = Path(index_dir)
    
    # Load FAISS index
    faiss_file = index_path / "faiss.index"
    if not faiss_file.exists():
        raise FileNotFoundError(f"FAISS index not found: {faiss_file}")
    
    index = faiss.read_index(str(faiss_file))
    print(f"✓ Loaded FAISS index: {index.ntotal} vectors")
    
    # Load metadata
    metadata_file = index_path / "metadata.pkl"
    if not metadata_file.exists():
        raise FileNotFoundError(f"Metadata file not found: {metadata_file}")
    
    with open(metadata_file, 'rb') as f:
        metadata = pickle.load(f)
    print(f"✓ Loaded metadata: {len(metadata)} entries")
    
    # Verify alignment
    if len(metadata) != index.ntotal:
        raise ValueError(
            f"Metadata length ({len(metadata)}) does not match "
            f"index size ({index.ntotal})"
        )
    
    return index, metadata


if __name__ == "__main__":
    # Test FAISS index operations
    print("=" * 80)
    print("TESTING FAISS INDEX MODULE")
    print("=" * 80)
    
    # Create sample embeddings
    print("\nTest 1: Create index")
    n_vectors = 100
    dimension = 384
    embeddings = np.random.rand(n_vectors, dimension).astype('float32')
    
    index = create_index(embeddings)
    print(f"Index size: {index.ntotal}")
    print(f"Index dimension: {index.d}")
    
    # Create sample metadata
    print("\nTest 2: Save and load index")
    metadata = [
        {
            'chunk_id': f'chunk_{i}',
            'class': 6,
            'subject': 'Science',
            'language': 'English',
            'chapter': 'Chapter 1',
            'page': i % 10 + 1,
            'text': f'Sample text {i}'
        }
        for i in range(n_vectors)
    ]
    
    # Save
    test_dir = "test_vector_store"
    save_index(index, metadata, test_dir)
    
    # Load
    loaded_index, loaded_metadata = load_index(test_dir)
    print(f"Loaded index size: {loaded_index.ntotal}")
    print(f"Loaded metadata count: {len(loaded_metadata)}")
    
    # Test search
    print("\nTest 3: Search test")
    query_vector = np.random.rand(1, dimension).astype('float32')
    distances, indices = loaded_index.search(query_vector, k=5)
    
    print(f"Query shape: {query_vector.shape}")
    print(f"Top 5 results:")
    for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
        print(f"  {i+1}. Index {idx}, Distance: {dist:.4f}")
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir)
    print("\n✓ Test directory cleaned up")
    
    print("\n" + "=" * 80)
    print("✓ All tests completed successfully!")
    print("=" * 80)
