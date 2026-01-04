"""
Semantic Retriever Module

This module provides semantic search functionality with metadata filtering.
"""

import sys
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
import time

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from embeddings.embedder import embed_single
from vector_store.faiss_index import load_index


class Retriever:
    """
    Semantic retriever with metadata filtering.
    
    This class handles:
    - Loading FAISS index and metadata
    - Query embedding
    - Similarity search
    - Metadata filtering
    """
    
    def __init__(self, index_dir: str = "data/vector_store"):
        """
        Initialize the retriever.
        
        Args:
            index_dir: Directory containing FAISS index and metadata
        """
        self.index_dir = index_dir
        self.index = None
        self.metadata = None
        self._load()
    
    def _load(self):
        """Load FAISS index and metadata."""
        print(f"Loading index from: {self.index_dir}")
        self.index, self.metadata = load_index(self.index_dir)
        print(f"✓ Retriever ready with {self.index.ntotal} chunks")
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        class_filter: Optional[int] = None,
        subject_filter: Optional[str] = None,
        language_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve relevant chunks for a query with optional metadata filtering.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            class_filter: Filter by class number (e.g., 6, 8, 10)
            subject_filter: Filter by subject (e.g., "Science", "Math", "SST")
            language_filter: Filter by language (e.g., "English", "Hindi")
            
        Returns:
            List of dictionaries containing chunk data and similarity scores
            
        Examples:
            >>> retriever = Retriever()
            >>> results = retriever.retrieve("What is photosynthesis?", top_k=5)
            >>> results = retriever.retrieve("gravity", class_filter=6, language_filter="English")
        """
        start_time = time.time()
        
        # Embed query
        query_embedding = embed_single(query).reshape(1, -1).astype('float32')
        
        # Search FAISS index
        # Retrieve more candidates if filtering is needed
        search_k = top_k * 10 if any([class_filter, subject_filter, language_filter]) else top_k
        distances, indices = self.index.search(query_embedding, k=min(search_k, self.index.ntotal))
        
        # Collect results with metadata
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:  # FAISS returns -1 for empty results
                continue
            
            meta = self.metadata[idx]
            
            # Apply filters
            if class_filter is not None and meta['class'] != class_filter:
                continue
            if subject_filter is not None and meta['subject'] != subject_filter:
                continue
            if language_filter is not None and meta['language'] != language_filter:
                continue
            
            # Convert L2 distance to similarity score (inverse)
            # Lower distance = higher similarity
            similarity_score = 1 / (1 + dist)
            
            result = {
                'text': meta['text'],
                'class': meta['class'],
                'subject': meta['subject'],
                'language': meta['language'],
                'chapter': meta['chapter'],
                'page': meta['page'],
                'chunk_id': meta['chunk_id'],
                'similarity_score': float(similarity_score),
                'distance': float(dist)
            }
            results.append(result)
            
            # Stop if we have enough results
            if len(results) >= top_k:
                break
        
        elapsed_time = time.time() - start_time
        
        # Add retrieval metadata
        for result in results:
            result['retrieval_time'] = elapsed_time
        
        return results


# Global retriever instance (singleton)
_retriever = None


def get_retriever(index_dir: str = "data/vector_store") -> Retriever:
    """
    Get or initialize the global retriever instance.
    
    Args:
        index_dir: Directory containing FAISS index and metadata
        
    Returns:
        Retriever instance
    """
    global _retriever
    
    if _retriever is None:
        _retriever = Retriever(index_dir)
    
    return _retriever


def retrieve(
    query: str,
    top_k: int = 5,
    class_filter: Optional[int] = None,
    subject_filter: Optional[str] = None,
    language_filter: Optional[str] = None,
    index_dir: str = "data/vector_store"
) -> List[Dict]:
    """
    Convenience function for retrieval.
    
    Args:
        query: Search query text
        top_k: Number of results to return
        class_filter: Filter by class number
        subject_filter: Filter by subject
        language_filter: Filter by language
        index_dir: Directory containing FAISS index
        
    Returns:
        List of result dictionaries
        
    Examples:
        >>> results = retrieve("What is photosynthesis?", top_k=5)
        >>> results = retrieve("gravity", class_filter=6, language_filter="English")
    """
    retriever = get_retriever(index_dir)
    return retriever.retrieve(
        query=query,
        top_k=top_k,
        class_filter=class_filter,
        subject_filter=subject_filter,
        language_filter=language_filter
    )


if __name__ == "__main__":
    # Test retriever
    print("=" * 80)
    print("TESTING RETRIEVER MODULE")
    print("=" * 80)
    
    # Check if index exists
    index_dir = "data/vector_store"
    if not Path(index_dir).exists():
        print(f"\n❌ ERROR: Index not found at {index_dir}")
        print("\nPlease build the index first:")
        print("  python embeddings/build_index.py")
        sys.exit(1)
    
    # Test 1: Basic retrieval
    print("\nTest 1: Basic retrieval")
    query = "What is photosynthesis?"
    results = retrieve(query, top_k=3)
    
    print(f"\nQuery: {query}")
    print(f"Retrieved {len(results)} results:\n")
    for i, result in enumerate(results):
        print(f"{i+1}. [Score: {result['similarity_score']:.3f}] "
              f"Class {result['class']}, {result['subject']}, {result['language']}")
        print(f"   {result['chapter']}, Page {result['page']}")
        print(f"   Text: {result['text'][:100]}...")
        print()
    
    # Test 2: Filtered retrieval
    print("\n" + "=" * 80)
    print("Test 2: Filtered retrieval (Class 6, English)")
    results = retrieve(query, top_k=3, class_filter=6, language_filter="English")
    
    print(f"\nQuery: {query}")
    print(f"Filters: Class=6, Language=English")
    print(f"Retrieved {len(results)} results:\n")
    for i, result in enumerate(results):
        print(f"{i+1}. [Score: {result['similarity_score']:.3f}] "
              f"Class {result['class']}, {result['subject']}, {result['language']}")
        print(f"   {result['chapter']}, Page {result['page']}")
        print()
    
    # Test 3: Performance
    print("=" * 80)
    print("Test 3: Performance test")
    queries = [
        "photosynthesis",
        "Newton's laws",
        "water cycle",
        "cell structure",
        "gravity"
    ]
    
    total_time = 0
    for q in queries:
        results = retrieve(q, top_k=5)
        if results:
            total_time += results[0]['retrieval_time']
    
    avg_time = total_time / len(queries)
    print(f"\nAverage retrieval time: {avg_time*1000:.2f} ms")
    print(f"Status: {'✓ PASS' if avg_time < 1.0 else '❌ FAIL'} (target: < 1 second)")
    
    print("\n" + "=" * 80)
    print("✓ All tests completed!")
    print("=" * 80)
