import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Add src to path so we can import 'rag', 'vector_store', etc. if running locally
# When running in Docker, 'src' contents are at root level.
base_path = Path(__file__).parent
src_path = base_path / "src"
if src_path.exists():
    sys.path.append(str(src_path))

# Attempt imports
try:
    from rag.pipeline import RAGPipeline
except ImportError:
    # If standard import fails, try relative (shouldn't be needed with sys.path or Docker)
    raise

app = FastAPI(title="NCERT RAG Service", version="1.0.0")

# Global pipeline instance
pipeline = None

class RAGQuery(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None

class RAGResponse(BaseModel):
    answer: str
    context: List[Dict[str, Any]]
    citations: List[str] = []
    latency: float

@app.on_event("startup")
async def startup_event():
    """Initialize the RAG pipeline on startup."""
    global pipeline
    try:
        print("🚀 Initializing RAG Pipeline...")
        # Check for API key
        if not os.getenv("GOOGLE_API_KEY"):
            print("⚠️  WARNING: GOOGLE_API_KEY not found. RAG generation might fail.")
            
        pipeline = RAGPipeline()
        print("✅ RAG Pipeline Ready.")
    except Exception as e:
        print(f"❌ Error initializing pipeline: {e}")
        # We don't raise here to allow the container to start, but requests will fail.

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "pipeline_loaded": pipeline is not None}

@app.post("/rag/query", response_model=RAGResponse)
async def query_rag(request: RAGQuery):
    """
    Execute RAG retrieval and generation.
    """
    global pipeline
    if not pipeline:
        raise HTTPException(status_code=503, detail="RAG Pipeline not yet initialized")
    
    try:
        # Run pipeline
        # Note: existing logic might print to stdout, which will go to docker logs
        result = pipeline.run(request.query, filters=request.filters)
        
        # Format citations
        citations = []
        if 'context' in result:
            for chunk in result['context']:
                # Construct readable citation
                # Assuming chunk metadata has these fields
                c_string = (
                    f"Class {chunk.get('class', 'N/A')} "
                    f"{chunk.get('subject', 'KB')} - "
                    f"Ch: {chunk.get('chapter', 'N/A')} "
                    f"(Pg {chunk.get('page', 'N/A')})"
                )
                citations.append(c_string)
        
        # Deduplicate citations while preserving order
        unique_citations = list(dict.fromkeys(citations))
        
        return RAGResponse(
            answer=result.get("answer", "No answer generated."),
            context=result.get("context", []),
            citations=unique_citations,
            latency=result.get("latency", 0.0)
        )
        
    except Exception as e:
        print(f"❌ Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Test run
    uvicorn.run(app, host="0.0.0.0", port=8001)
