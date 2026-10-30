from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(
        ..., min_length=3, max_length=2000, description="Content of the question to be looked up"
    )
    top_k: int | None = Field(
        default=3, ge=1, le=10, description="Number of extracted document segments"
    )


class SourceItem(BaseModel):
    source_file: str
    page_number: int
    chunk_id: str | None = None


class RetrievedChunkItem(BaseModel):
    chunk_id: str
    rerank_score: float
    source_file: str
    page_number: int


class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceItem]
    retrieved_chunks: list[RetrievedChunkItem]
    tokens: dict[str, int]
    timings_ms: dict[str, float]
    request_id: str | None = None
