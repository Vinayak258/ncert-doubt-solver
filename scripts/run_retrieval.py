"""
Retrieval CLI Tool

This script demonstrates semantic retrieval with the NCERT vector database.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from vector_store.retriever import retrieve


def print_results(query: str, results: list, filters: dict = None):
    """
    Pretty print retrieval results.
    
    Args:
        query: Search query
        results: List of result dictionaries
        filters: Optional filters applied
    """
    print("=" * 80)
    print(f"QUERY: {query}")
    if filters:
        filter_str = ", ".join([f"{k}={v}" for k, v in filters.items() if v is not None])
        if filter_str:
            print(f"FILTERS: {filter_str}")
    print("=" * 80)
    
    if not results:
        print("\n❌ No results found")
        return
    
    print(f"\nFound {len(results)} results")
    if results:
        print(f"Retrieval time: {results[0]['retrieval_time']*1000:.2f} ms")
    print()
    
    for i, result in enumerate(results):
        print(f"{i+1}. [Similarity: {result['similarity_score']:.3f}]")
        print(f"   Class {result['class']} | {result['subject']} | {result['language']}")
        print(f"   {result['chapter']}, Page {result['page']}")
        print(f"   Text: {result['text'][:150]}...")
        print()


def main():
    """Run retrieval tests."""
    print("\n" + "=" * 80)
    print("NCERT DOUBT-SOLVER: SEMANTIC RETRIEVAL DEMO")
    print("=" * 80)
    
    # Check if index exists
    index_dir = Path("data/vector_store")
    if not index_dir.exists():
        print(f"\n❌ ERROR: Vector index not found at {index_dir}")
        print("\nPlease build the index first:")
        print("  python embeddings/build_index.py")
        sys.exit(1)
    
    # Test queries
    test_queries = [
        {
            'query': "What is photosynthesis?",
            'filters': {}
        },
        {
            'query': "Explain Newton's laws of motion",
            'filters': {}
        },
        {
            'query': "How does the water cycle work?",
            'filters': {'class_filter': 6}
        },
        {
            'query': "What is gravity?",
            'filters': {'language_filter': 'English'}
        },
        {
            'query': "cell structure and function",
            'filters': {'class_filter': 6, 'subject_filter': 'Science'}
        }
    ]
    
    # Run queries
    for test in test_queries:
        query = test['query']
        filters = test['filters']
        
        results = retrieve(
            query=query,
            top_k=5,
            **filters
        )
        
        print_results(query, results, filters)
        print()
    
    # Interactive mode
    print("=" * 80)
    print("INTERACTIVE MODE")
    print("=" * 80)
    print("\nEnter your queries (or 'quit' to exit):")
    print("You can also specify filters like: query | class=6 | language=English\n")
    
    while True:
        try:
            user_input = input("\nQuery: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n✓ Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Parse filters
            parts = [p.strip() for p in user_input.split('|')]
            query = parts[0]
            filters = {}
            
            for part in parts[1:]:
                if '=' in part:
                    key, value = part.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == 'class':
                        filters['class_filter'] = int(value)
                    elif key == 'subject':
                        filters['subject_filter'] = value
                    elif key == 'language':
                        filters['language_filter'] = value
            
            # Retrieve
            results = retrieve(query=query, top_k=5, **filters)
            print_results(query, results, filters)
            
        except KeyboardInterrupt:
            print("\n\n✓ Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            continue


if __name__ == "__main__":
    main()
