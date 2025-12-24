"""
Embeddings module for NCERT Doubt-Solver.

This module handles text-to-vector conversion using multilingual models.
"""

from .embedder import get_embedder, embed_texts, embed_single

__all__ = ['get_embedder', 'embed_texts', 'embed_single']
