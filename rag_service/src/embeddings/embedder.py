"""
Text Embedder Module

This module provides text-to-vector conversion using a multilingual
sentence transformer model that supports both English and Hindi.

Model: all-MiniLM-L6-v2
- Dimension: 384
- Languages: English (supported), Multilingual (limited)
- Speed: ~1000 sentences/sec on CPU
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Union


# Global model instance (singleton pattern)
_model = None


def get_embedder() -> SentenceTransformer:
    """
    Get or initialize the embedding model (singleton).
    
    The model is loaded once and reused for all subsequent calls.
    
    Returns:
        SentenceTransformer: Loaded multilingual embedding model
    """
    global _model
    
    if _model is None:
        print("Loading lightweight embedding model...")
        print("Model: all-MiniLM-L6-v2")
        _model = SentenceTransformer('all-MiniLM-L6-v2')
        print(f"✓ Model loaded successfully (dimension: {_model.get_sentence_embedding_dimension()})")
    
    return _model


def embed_texts(texts: List[str], batch_size: int = 32, show_progress: bool = True) -> np.ndarray:
    """
    Convert a list of texts to embedding vectors.
    
    Args:
        texts: List of text strings to embed
        batch_size: Number of texts to process in each batch
        show_progress: Whether to show progress bar
        
    Returns:
        numpy array of shape (len(texts), embedding_dim)
        
    Examples:
        >>> texts = ["What is photosynthesis?", "Explain gravity"]
        >>> embeddings = embed_texts(texts)
        >>> embeddings.shape
        (2, 384)
    """
    if not texts:
        return np.array([])
    
    model = get_embedder()
    
    # Generate embeddings with batching
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=show_progress,
        convert_to_numpy=True,
        normalize_embeddings=True  # L2 normalization for better similarity
    )
    
    return embeddings


def embed_single(text: str) -> np.ndarray:
    """
    Convert a single text to an embedding vector.
    
    Args:
        text: Text string to embed
        
    Returns:
        numpy array of shape (embedding_dim,)
        
    Examples:
        >>> embedding = embed_single("What is photosynthesis?")
        >>> embedding.shape
        (384,)
    """
    model = get_embedder()
    
    embedding = model.encode(
        text,
        convert_to_numpy=True,
        normalize_embeddings=True
    )
    
    return embedding


def get_embedding_dimension() -> int:
    """
    Get the dimension of the embedding vectors.
    
    Returns:
        int: Embedding dimension (384 for this model)
    """
    model = get_embedder()
    return model.get_sentence_embedding_dimension()


if __name__ == "__main__":
    # Test the embedder
    print("=" * 80)
    print("TESTING EMBEDDER MODULE")
    print("=" * 80)
    
    # Test 1: Single embedding
    print("\nTest 1: Single text embedding")
    text = "What is photosynthesis?"
    embedding = embed_single(text)
    print(f"Text: {text}")
    print(f"Embedding shape: {embedding.shape}")
    print(f"Embedding (first 5 values): {embedding[:5]}")
    
    # Test 2: Batch embedding
    print("\nTest 2: Batch text embedding")
    texts = [
        "What is photosynthesis?",
        "Explain Newton's laws of motion",
        "भारत की राजधानी क्या है?",  # Hindi: What is the capital of India?
        "How does the water cycle work?"
    ]
    embeddings = embed_texts(texts, show_progress=False)
    print(f"Number of texts: {len(texts)}")
    print(f"Embeddings shape: {embeddings.shape}")
    
    # Test 3: Similarity test
    print("\nTest 3: Semantic similarity")
    query = "photosynthesis in plants"
    query_emb = embed_single(query)
    
    # Calculate cosine similarity (dot product since normalized)
    similarities = embeddings @ query_emb
    
    print(f"Query: {query}")
    for i, (text, sim) in enumerate(zip(texts, similarities)):
        print(f"  {i+1}. [{sim:.3f}] {text}")
    
    print("\n" + "=" * 80)
    print("✓ All tests completed successfully!")
    print("=" * 80)
