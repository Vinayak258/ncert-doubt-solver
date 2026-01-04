"""
Vector Store module for NCERT Doubt-Solver.

This module handles FAISS index management and semantic retrieval.
"""

from .faiss_index import create_index, save_index, load_index
from .retriever import retrieve, Retriever

__all__ = ['create_index', 'save_index', 'load_index', 'retrieve', 'Retriever']
