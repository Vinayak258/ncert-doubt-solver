"""
LLM Generator Module

Handles interaction with the LLM API (Google Gemini).
"""

import os
import google.generativeai as genai
from typing import Optional
from pathlib import Path

from .llm_config import LLMConfig

class LLMGenerator:
    """Handles prompt construction and LLM generation."""
    
    def __init__(self, config: LLMConfig):
        """
        Initialize the generator.
        
        Args:
            config: LLM configuration
        """
        self.config = config
        self._setup_api()
        self.system_prompt = self._load_system_prompt()
        self.user_prompt_template = self._load_user_prompt_template()
        
        # Initialize model
        # Note: system_instruction not supported in google-generativeai==0.3.2
        self.model = genai.GenerativeModel(
            model_name=self.config.model_name
        )
        
    def _setup_api(self):
        """Configure the Gemini API."""
        if not self.config.api_key:
            print("⚠️  WARNING: GOOGLE_API_KEY not found in environment variables.")
            print("   LLM generation will fail unless key is provided.")
        else:
            genai.configure(api_key=self.config.api_key)
            
    def _load_system_prompt(self) -> str:
        """Load the master system prompt from file."""
        prompt_path = Path("prompts/system_prompt.md")
        try:
            return prompt_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"❌ Error loading system prompt: {e}")
            return "You are a helpful assistant." # Fallback
            
    def _load_user_prompt_template(self) -> str:
        """Load user prompt template."""
        prompt_path = Path("prompts/rag_query_template.txt")
        try:
            return prompt_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"❌ Error loading user prompt template: {e}")
            return "Context:\n{RETRIEVED_CHUNKS}\n\nQuestion: {USER_QUESTION}"
            
    def format_context(self, chunks: list[dict]) -> str:
        """
        Format retrieved chunks into the prompt context structure.
        
        Args:
            chunks: List of retrieved chunk dictionaries
            
        Returns:
            Formatted context string
        """
        formatted_chunks = []
        
        for chunk in chunks:
            # Safely get metadata with defaults
            c_class = chunk.get('class', 'N/A')
            c_subj = chunk.get('subject', 'N/A')
            c_lang = chunk.get('language', 'N/A')
            c_chap = chunk.get('chapter', 'N/A')
            c_page = chunk.get('page', 'N/A')
            text = chunk.get('text', '').strip()
            
            chunk_str = (
                f"[NCERT SOURCE]\n"
                f"Class: {c_class}\n"
                f"Subject: {c_subj}\n"
                f"Language: {c_lang}\n"
                f"Chapter: {c_chap}\n"
                f"Page: {c_page}\n\n"
                f"{text}"
            )
            formatted_chunks.append(chunk_str)
            
        return "\n\n---\n".join(formatted_chunks)
        
    def generate_response(self, question: str, chunks: list[dict]) -> str:
        """
        Generate an answer using RAG.
        
        Args:
            question: User's question
            chunks: Retrieved context chunks
            
        Returns:
            Generated response string
        """
        # 1. Format context
        context_str = self.format_context(chunks)
        
        # 2. Construct prompt
        # We manually prepend system prompt since older SDK doesn't support system_instruction
        user_part = self.user_prompt_template.format(
            RETRIEVED_CHUNKS=context_str,
            USER_QUESTION=question
        )
        prompt = f"{self.system_prompt}\n\n{user_part}"
        
        # 3. Call LLM
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.config.temperature,
                    top_p=self.config.top_p,
                    top_k=self.config.top_k,
                    max_output_tokens=self.config.max_output_tokens
                )
            )

            # Safe response extraction
            if hasattr(response, "text") and response.text:
                answer = response.text
            else:
                answer = response.candidates[0].content.parts[0].text
            
            return answer
            
        except Exception as e:
            print("🔥 GEMINI ERROR:", str(e))
            return f"ERROR: {str(e)}"
