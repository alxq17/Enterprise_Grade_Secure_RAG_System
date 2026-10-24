from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
     question: str = Field(..., min_length=3, max_length=2000, description="Content of the question to be looked up")
     top_k: Optional[int] = Field(default=3, ge=1, le=10, description="Number of extracted document segments")

class SourceItem(BaseModel):
    source_file: str
    page_number: int
    chunk_id: Optional[str] = None

class RetrievedChunkItem(BaseModel):
    chunk_id: str
    rerank_score: float
    source_file: str
    page_number: int

class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[SourceItem]
    retrieved_chunks: List[RetrievedChunkItem]
    tokens: Dict[str, int]
    timings_ms: Dict[str, float]
    request_id: Optional[str] = None