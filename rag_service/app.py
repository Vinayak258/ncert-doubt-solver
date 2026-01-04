import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# ---------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------
# Add src to path so we can import 'rag', 'vector_store', etc. if running locally
# When running in Docker, 'src' contents are already at root level.
base_path = Path(__file__).parent
src_path = base_path / "src"
if src_path.exists():
    sys.path.append(str(src_path))

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------
try:
    from rag.pipeline import RAGPipeline
except ImportError as e:
    raise ImportError(f"Failed to import RAGPipeline: {e}")

# ---------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------
app = FastAPI(title="NCERT RAG Service", version="1.0.0")

# ---------------------------------------------------------------------
# Global pipeline instance (initialized on startup)
# ---------------------------------------------------------------------
pipeline = None

# ---------------------------------------------------------------------
# Request / Response Schemas
# ---------------------------------------------------------------------
class RAGQuery(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None

class RAGResponse(BaseModel):
    answer: str
    context: List[Dict[str, Any]]
    citations: List[str] = []
    latency: float

# ---------------------------------------------------------------------
# Startup Event
# ---------------------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    """Initialize the RAG pipeline on startup."""
    global pipeline
    try:
        print("🚀 Initializing RAG Pipeline...")

        if not os.getenv("GOOGLE_API_KEY"):
            print("⚠️ WARNING: GOOGLE_API_KEY not found. RAG generation may fail.")

        pipeline = RAGPipeline()
        print("✅ RAG Pipeline Ready.")

    except Exception as e:
        print(f"❌ Error initializing pipeline: {e}")
        pipeline = None
        # Do not raise to allow container to start

# ---------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "pipeline_loaded": pipeline is not None
    }

# ---------------------------------------------------------------------
# RAG Query Endpoint
# ---------------------------------------------------------------------
@app.post("/rag/query", response_model=RAGResponse)
async def query_rag(request: RAGQuery):
    """
    Execute RAG retrieval and generation.
    """
    if pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="RAG Pipeline not yet initialized"
        )

    try:
        result = pipeline.run(
            request.query,
            filters=request.filters
        )

        # Build citations
        citations: List[str] = []
        for chunk in result.get("context", []):
            citation = (
                f"Class {chunk.get('class', 'N/A')} "
                f"{chunk.get('subject', 'N/A')} - "
                f"Ch {chunk.get('chapter', 'N/A')} "
                f"(Pg {chunk.get('page', 'N/A')})"
            )
            citations.append(citation)

        # Deduplicate while preserving order
        unique_citations = list(dict.fromkeys(citations))

        return RAGResponse(
            answer=result.get("answer", "No answer generated."),
            context=result.get("context", []),
            citations=unique_citations,
            latency=result.get("latency", 0.0)
        )

    except Exception as e:
        print(f"❌ Error processing query: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while processing RAG query"
        )

# ---------------------------------------------------------------------
# Local Development Entry Point
# ---------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
