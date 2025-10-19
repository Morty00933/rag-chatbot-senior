from __future__ import annotations
from functools import lru_cache
from pydantic_settings import BaseSettings  # <-- важно: из pydantic_settings
# pydantic v2: поля по умолчанию и типы — как в v2

class Settings(BaseSettings):
    # --- Core ---
    ENV: str = "dev"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:5173"
    MAX_UPLOAD_MB: int = 25

    # --- Auth ---
    JWT_SECRET: str = "change_me"
    JWT_EXPIRES_MIN: int = 60

    # --- LLM ---
    LLM_PROVIDER: str = "ollama"
    LLM_MODEL: str = "qwen2.5:3b"
    OLLAMA_HOST: str = "http://ollama:11434"
    OPENAI_API_KEY: str | None = None
    HF_API_TOKEN: str | None = None

    # --- Embeddings ---
    EMBED_PROVIDER: str = "sbert"
    EMBED_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBED_DIM: int = 384

    # --- Vector store ---
    VECTOR_BACKEND: str = "qdrant"
    QDRANT_URL: str = "http://qdrant:6333"
    QDRANT_COLLECTION: str = "kb"

    # --- DB / storage ---
    DB_URL: str = "sqlite+aiosqlite:///./data/app.db"
    DOCSTORE_PATH: str = "./data/chunks"

    # --- Redis/Celery ---
    REDIS_URL: str = "redis://redis:6379/0"

    # --- Telemetry ---
    PROMETHEUS_ENABLED: bool = True
    API_METRICS_PATH: str = "/metrics"
    WORKER_METRICS_PORT: int = 8001

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }

@lru_cache(maxsize=1)
def get_settings() -> "Settings":
    return Settings()

settings = get_settings()
