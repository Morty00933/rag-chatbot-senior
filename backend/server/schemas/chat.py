from typing import List, Optional
from pydantic import BaseModel


class Reference(BaseModel):
    document_id: int
    filename: str
    score: float
    chunk_ord: int
    preview: str


class ChatRequest(BaseModel):
    question: str
    top_k: int = 6


class ChatResponse(BaseModel):
    answer: str
    references: List[Reference]
