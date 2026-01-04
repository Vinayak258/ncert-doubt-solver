"""
RAG Pipeline Orchestrator

Connects retrieval (Vector Store) with generation (LLM).
"""

import time
from typing import Dict, Any

from vector_store.retriever import retrieve
from .generator import LLMGenerator
from .llm_config import LLMConfig

class RAGPipeline:
    """Orchestrates the Retrieval-Augmented Generation process."""
    
    def __init__(self):
        """Initialize the RAG pipeline."""
        self.config = LLMConfig.from_env()
        self.generator = LLMGenerator(self.config)
        
    def run(self, query: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run the full RAG pipeline.
        
        Args:
            query: User's question
            filters: Optional metadata filters (class, subject, language)
            
        Returns:
            Dictionary containing answer, context, and metadata
        """
        start_time = time.time()
        
        # 1. Retrieve Context
        print(f"🔍 Retrieving context for: '{query}'")
        retrieved_chunks = retrieve(
            query=query,
            top_k=self.config.max_context_chunks,
            **(filters or {})
        )
        
        if not retrieved_chunks:
            return {
                "answer": "I could not find any relevant information in the NCERT textbooks to answer your question.",
                "context": [],
                "latency": time.time() - start_time
            }
            
        # 2. Generate Answer
        print("🧠 Generating answer with LLM...")
        answer = self.generator.generate_response(query, retrieved_chunks)
        
        total_time = time.time() - start_time
        
        return {
            "query": query,
            "answer": answer,
            "context": retrieved_chunks,
            "latency": total_time
        }
