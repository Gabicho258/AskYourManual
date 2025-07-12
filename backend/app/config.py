# app/config.py - Versión corregida para Pydantic v2 con parsing fix
import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    # Configuración general
    DEBUG: bool = False
    PORT: int = 8000

    # CORS - Cambio importante: usar str y procesar manualmente
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Qdrant
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "komatsu_manuals"

    # PDF Processing
    PDF_STORAGE_PATH: str = "./data/pdfs"
    PROCESSED_STORAGE_PATH: str = "./data/processed"
    MAX_FILE_SIZE: int = 52428800  # 50MB

    # Embeddings
    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    EMBEDDING_BATCH_SIZE: int = 32

    # Chunking
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    MIN_CHUNK_SIZE: int = 100

    # Search
    DEFAULT_SEARCH_LIMIT: int = 10
    MAX_SEARCH_LIMIT: int = 100

    # Cache
    CACHE_TTL: int = 3600  # 1 hora
    MAX_CACHE_SIZE: int = 1000

    # Logging
    LOG_LEVEL: str = "INFO"

    # Validador para convertir ALLOWED_ORIGINS de string a lista
    @field_validator('ALLOWED_ORIGINS')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v

    # Validador para DEBUG
    @field_validator('DEBUG')
    @classmethod
    def parse_debug(cls, v):
        if isinstance(v, str):
            return v.lower() in ('true', '1', 'yes', 'on')
        return bool(v)

    # Configuración del modelo para Pydantic v2
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore"
    }

    # Método para obtener orígenes como lista (backward compatibility)
    def get_allowed_origins_list(self) -> List[str]:
        if isinstance(self.ALLOWED_ORIGINS, str):
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(',') if origin.strip()]
        return self.ALLOWED_ORIGINS


# Configuraciones específicas por modelo
EMBEDDING_MODELS = {
    "multilingual": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    "fast": "sentence-transformers/all-MiniLM-L6-v2",
    "accurate": "sentence-transformers/all-mpnet-base-v2",
    "spanish": "sentence-transformers/distiluse-base-multilingual-cased",
}

# Estrategias de chunking
CHUNK_STRATEGIES = {
    "fixed": {"size": 1000, "overlap": 200},
    "semantic": {"min_size": 500, "max_size": 2000, "overlap": 100},
    "sentence": {"sentences_per_chunk": 5, "overlap_sentences": 1},
}

# Configuración de métricas
METRICS_CONFIG = {
    "precision_k_values": [1, 3, 5, 10],
    "recall_k_values": [1, 3, 5, 10],
    "latency_percentiles": [50, 90, 95, 99],
    "quality_thresholds": {
        "semantic_coherence": 0.7,
        "diversity": 0.5,
        "stability": 0.8,
    },
}

settings = Settings()