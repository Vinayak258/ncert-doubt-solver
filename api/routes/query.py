import os
import httpx
from fastapi import APIRouter, HTTPException, Request
from ..schemas import UserQuery, BotResponse

router = APIRouter()

# Configuration
RAG_SERVICE_URL = os.getenv("RAG_SERVICE_URL", "http://rag_service:8001")

@router.post("/chat", response_model=BotResponse)
async def chat_endpoint(user_query: UserQuery):
    """
    Process a student's query by forwarding it to the RAG service.
    """
    
    # 1. Input Validation (Basic)
    # (Pydantic handles basic type validation, we can add logic here)
    if user_query.class_level and user_query.class_level not in [6, 7, 8, 9, 10, 11, 12]:
         # For now, just a warning or soft handle, or strict 400
         # Let's be lenient as the RAG might handle others if data exists
         pass

    # 2. Construct Filter
    filters = {}
    if user_query.class_level:
        filters["class"] = user_query.class_level
    if user_query.subject:
        filters["subject"] = user_query.subject
    # Add other filters if needed by RAG pipeline logic
    
    payload = {
        "query": user_query.query,
        "filters": filters
    }
    
    # 3. Call RAG Service
    async with httpx.AsyncClient() as client:
        try:
            # Note: The RAG service endpoint we defined is /rag/query
            response = await client.post(
                f"{RAG_SERVICE_URL}/rag/query", 
                json=payload,
                timeout=60.0 # LLM generation can be slow
            )
            response.raise_for_status()
            rag_data = response.json()
            
        except httpx.RequestError as exc:
            print(f"❌ Connection error to RAG Service: {exc}")
            raise HTTPException(status_code=503, detail="AI Service unavailable")
        except httpx.HTTPStatusError as exc:
            print(f"❌ RAG Service error {exc.response.status_code}: {exc.response.text}")
            raise HTTPException(status_code=500, detail="Error processing answer")

    # 4. Format Response
    return BotResponse(
        answer=rag_data.get("answer", ""),
        citations=rag_data.get("citations", []),
        fallback_mode=False
    )
