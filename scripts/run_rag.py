"""
RAG Pipeline Test Script

Demonstrates the full RAG pipeline: Retrieval + Prompting + LLM Generation.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

import traceback
from rag.pipeline import RAGPipeline

def load_env():
    """Load .env file manually."""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        print(f"Loading environment from {env_path}")
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

def main():
    """Run RAG pipeline test."""
    load_env()
    
    print("=" * 80)
    print("NCERT RAG PIPELINE DEMO")
    print("=" * 80)
    
    # Check for API key (Mock check/Warning)
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("\n⚠️  WARNING: GOOGLE_API_KEY environment variable not found.")
        print("   The pipeline will perform retrieval but generation will fail/mocked.")
        print("   To enable generation: Set GOOGLE_API_KEY in .env or environment")
    else:
        print(f"\n✓ API Key found: {api_key[:5]}...{api_key[-5:]}")
    
    # Initialize Pipeline
    print("Initializing RAG Pipeline...")
    try:
        pipeline = RAGPipeline()
    except Exception as e:
        print(f"❌ Failed to initialize pipeline: {e}")
        return

    # Test Queries
    queries = [
        {
            "text": "What are the components of food?",
            "filters": {"class_filter": 6}
        },
        {
            "text": "Explain the process of photosynthesis.",
            "filters": {"subject_filter": "Science"}
        },
        {
        "text": "What is DNA replication?",
        "filters": {"class_filter": 6}
        }
    ]
    
    for q in queries:
        print("-" * 80)
        print(f"QUESTION: {q['text']}")
        print(f"FILTERS: {q['filters']}")
        print("-" * 80)
        
        try:
            result = pipeline.run(q['text'], filters=q['filters'])
            
            print(f"\n✅ RECOVERED {len(result.get('context', []))} chunks")
            print(f"⏱️  Latency: {result['latency']:.2f}s")
            
            print("\n🤖 LLM ANSWER:")
            print(result.get('answer'))
            
            if not api_key and "Error" in result.get('answer', ''):
                print("\n(Note: This error is expected without an API key)")
                
        except Exception:
            print("❌ Pipeline run failed:")
            traceback.print_exc()
            
    print("\n" + "=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
