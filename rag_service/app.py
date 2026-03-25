import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ---------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------
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
# ✅ CORS MIDDLEWARE (CRITICAL FIX)
# ---------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # allow frontend domain (safe for demo)
    allow_credentials=True,
    allow_methods=["*"],          # REQUIRED for OPTIONS preflight
    allow_headers=["*"],
)

# ---------------------------------------------------------------------
# Lazy Pipeline Loader
# ---------------------------------------------------------------------
pipeline = None

def get_pipeline():
    """Initialize the pipeline only on first query (Lazy loading)."""
    global pipeline
    if pipeline is None:
        try:
            print("🚀 Initializing RAG Pipeline (Lazy Load)...")
            if not os.getenv("GOOGLE_API_KEY"):
                print("⚠️ WARNING: GOOGLE_API_KEY not found.")
            
            pipeline = RAGPipeline()
            # Note: We DON'T warm up here to keep latency acceptable for the first user
            print("✅ RAG Pipeline initialized and ready.")
        except Exception as e:
            print(f"❌ Pipeline initialization failed: {e}")
            pipeline = None
            raise HTTPException(status_code=500, detail="Failed to initialize RAG pipeline.")
    return pipeline

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

# Root Endpoint
@app.get("/")
def root():
    return {"message": "NCERT RAG API is running"}

# ---------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------
@app.get("/health")
def health_check():
    """Fast health check for Render/K8s."""
    return {"status": "ok"}

# ---------------------------------------------------------------------
# RAG Query Endpoint
# ---------------------------------------------------------------------
import asyncio

@app.post("/rag/query", response_model=RAGResponse)
async def query_rag(request: RAGQuery):
    # Lazy load pipeline
    current_pipeline = get_pipeline()

    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(
                current_pipeline.run,
                request.query,
                request.filters
            ),
            timeout=55  # seconds
        )

        citations = []
        for chunk in result.get("context", []):
            citations.append(
                f"Class {chunk.get('class', 'N/A')} "
                f"{chunk.get('subject', 'N/A')} - "
                f"Ch {chunk.get('chapter', 'N/A')} "
                f"(Pg {chunk.get('page', 'N/A')})"
            )

        return RAGResponse(
            answer=result.get("answer", ""),
            context=result.get("context", []),
            citations=list(dict.fromkeys(citations)),
            latency=result.get("latency", 0.0)
        )

    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Model is warming up. Please retry in 30 seconds."
        )


# ---------------------------------------------------------------------
# Local Development Entry Point
# ---------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
