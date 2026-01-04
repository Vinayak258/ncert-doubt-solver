from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class UserQuery(BaseModel):
    query: str = Field(..., min_length=3, description="The student's question")
    class_level: Optional[int] = Field(None, description="Class level (6, 8, 10)")
    subject: Optional[str] = Field(None, description="Subject (Maths, Science, etc.)")
    language: Optional[str] = Field("English", description="Language preference")

class Citation(BaseModel):
    text: str = Field(..., description="Formatted citation string")

class BotResponse(BaseModel):
    answer: str
    citations: List[str]
    query_id: Optional[str] = None
    fallback_mode: bool = False
