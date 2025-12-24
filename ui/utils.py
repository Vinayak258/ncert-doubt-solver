"""
UI Utilities for NCERT Doubt-Solver.

Handles:
- Safe API calling (wrapping errors)
- Formatting citations
- Formatting messages
"""

import time
import functools
import streamlit as st

def handle_errors(func):
    """
    Decorator to wrap API calls with safe error handling 
    for the UI.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = str(e)
            
            # Check for Rate Limits (Quota Exceeded)
            if "429" in error_msg or "Resource has been exhausted" in error_msg:
                st.error("⚠️ The system is temporarily unable to generate an answer due to traffic. Please try again in a moment.")
                return None
            
            # General generation errors
            st.error(f"⚠️ An error occurred: {error_msg}")
            return None
    return wrapper

def format_citation(chunk):
    """Format a single chunk into a readable citation."""
    return (
        f"**Class {chunk.get('class')} {chunk.get('subject')}**\n"
        f"Chapter: {chunk.get('chapter')}, Page {chunk.get('page')}"
    )

def display_chat_message(role, content, citations=None):
    """
    Display a chat message with simplified UI style.
    """
    with st.chat_message(role):
        st.write(content)
        
        if citations and len(citations) > 0:
            with st.expander(f"📚 View {len(citations)} NCERT Sources"):
                for i, chunk in enumerate(citations):
                    st.markdown(f"---")
                    st.markdown(format_citation(chunk))
                    st.caption(f"\"{chunk.get('text', '')[:150]}...\"")
