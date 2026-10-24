from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Qdrant
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: str | None = None
    COLLECTION_NAME: str = "enterprise_docs"

    # Models
    EMBEDDING_MODEL: str = "BAAI/bge-m3"
    EMBEDDING_DIM: int = 1024
    RERANKER_MODEL: str = "BAAI/bge-reranker-v2-m3"

    # LLM
    GEMINI_API_KEY: str = Field(
        default="",
        description="Google Gemini API key",
    )
    GEMINI_MODEL: str = "gemini-1.5-flash"
    LLM_TIMEOUT_SECONDS: int = 30
    LLM_MAX_RETRIES: int = 3

    # API
    API_PORT: int = 8000
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Guardrails
    DOMAIN_SIMILARITY_THRESHOLD: float = 0.35
    MAX_QUERY_LENGTH: int = 2000

    # Eval
    API_BASE_URL: str = "http://localhost:8080"

settings = Settings()
