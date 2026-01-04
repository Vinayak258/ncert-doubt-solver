"""
NCERT Doubt-Solver - Student UI
Final Polished Version (Day-5)

DEPRECATED: This Streamlit app is now legacy.
Please use the Next.js Frontend for the production experience.
"""

import sys
import os
import streamlit as st
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from rag.pipeline import RAGPipeline
from ui.utils import handle_errors, display_chat_message

# Page Config
st.set_page_config(
    page_title="NCERT Doubt Solver (Legacy)",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Environment locally if needed
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    from scripts.run_rag import load_env
    load_env()

@st.cache_resource
def get_pipeline():
    """Initialize RAG Pipeline once."""
    return RAGPipeline()

def main():
    # --- DEPRECATION NOTICE ---
    st.error("⚠️ **LEGACY INTERFACE**: This Streamlit app is deprecated. Please use the Next.js web application for the full product experience.")
    
    # --- Header & Trust Signals ---
    st.title("📚 NCERT Doubt Solver (Legacy Mode)")
    st.markdown("### *Answers strictly from NCERT textbooks*")
    st.markdown("---")

    # --- Sidebar: Control Panel ---
    with st.sidebar:
        st.header("⚙️ Student Settings")
        
        st.info("🛡️ **Strict NCERT Mode ON**\n\nAnswers are grounded in official textbooks to prevent hallucinations.")
        
        st.markdown("### Filters")
        st.markdown("_Restricts answers to specific NCERT books_")
        
        selected_class = st.selectbox(
            "Class",
            options=[6, 8, 10],
            index=0,
            help="Select your standard"
        )
        
        selected_subject = st.selectbox(
            "Subject",
            options=["Science", "Math", "Social Science"],
            index=0,
            help="Select the subject you are studying"
        )
        
        selected_language = st.radio(
            "Language",
            options=["English", "Hindi"],
            index=0,
            horizontal=True
        )
        
        st.divider()
        st.caption("Built by Team iDeatorsX")

    # --- Chat State ---
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            # If there are citations, show them
            citations = msg.get("citations")
            if citations:
                with st.expander(f"📚 View {len(citations)} NCERT Sources"):
                    for chunk in citations:
                        st.markdown("---")
                        st.caption(
                            f"**Class {chunk.get('class')} - {chunk.get('subject')}** | "
                            f"{chunk.get('chapter')} (Page {chunk.get('page')})"
                        )
                        st.text(chunk.get('text', '')[:250] + "...")

    # --- User Input ---
    if prompt := st.chat_input("Ask a question from your textbook..."):
        # 1. Show User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # 2. Generate Answer
        with st.chat_message("assistant"):
            # Empty container for the answer
            answer_container = st.empty()
            sources_container = st.empty()
            
            with st.spinner("🔍 Reading NCERT textbooks..."):
                pipeline = get_pipeline()
                
                # Prepare Filters
                filters = {
                    "class_filter": selected_class,
                    "subject_filter": selected_subject if selected_subject != "Social Science" else "SST",
                    "language_filter": selected_language
                }
                
                # Run RAG
                result = pipeline.run(prompt, filters=filters)

            if result:
                answer = result.get("answer", "")
                context = result.get("context", [])
                
                # Display Answer
                answer_container.markdown(f"**✅ Answer:**\n\n{answer}")
                
                # Display Sources (Transparency)
                if context:
                    with sources_container:
                        with st.expander(f"📚 View {len(context)} NCERT Sources", expanded=False):
                            for chunk in context:
                                st.markdown("---")
                                st.caption(
                                    f"**Class {chunk.get('class')} - {chunk.get('subject')}** | "
                                    f"Chapter: {chunk.get('chapter')}"
                                )
                                st.markdown(f"> *Page {chunk.get('page')}*")
                                st.text(chunk.get('text', '')[:300] + "...")
                else:
                     with sources_container:
                        st.info("No direct NCERT matches found for the selected filters.")

                # Save to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "citations": context
                })

if __name__ == "__main__":
    main()
