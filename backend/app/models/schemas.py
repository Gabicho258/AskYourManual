from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class SearchStrategy(str, Enum):
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    KEYWORD = "keyword"


class MetricType(str, Enum):
    PRECISION = "precision"
    RECALL = "recall"
    LATENCY = "latency"
    QUALITY = "quality"


# Schemas para documentos
class DocumentBase(BaseModel):
    filename: str
    title: Optional[str] = None
    description: Optional[str] = None


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class Document(DocumentBase):
    id: str
    status: DocumentStatus
    file_size: int
    chunk_count: int
    created_at: datetime
    updated_at: datetime
    processing_time: Optional[float] = None
    error_message: Optional[str] = None

    class Config:
        orm_mode = True


# Schemas para búsqueda
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    limit: int = Field(default=10, ge=1, le=100)
    strategy: SearchStrategy = SearchStrategy.SEMANTIC
    filters: Optional[Dict[str, Any]] = None
    include_metadata: bool = False


class SearchResult(BaseModel):
    text: str
    pdf_name: str
    chunk_id: str
    score: float
    metadata: Optional[Dict[str, Any]] = None


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: int
    search_time: float
    strategy_used: SearchStrategy
    query_id: str


class BatchSearchRequest(BaseModel):
    queries: List[str] = Field(..., min_items=1, max_items=50)
    limit: int = Field(default=10, ge=1, le=100)
    strategy: SearchStrategy = SearchStrategy.SEMANTIC


class BatchSearchResponse(BaseModel):
    results: List[SearchResponse]
    total_search_time: float
    batch_id: str


# Schemas para métricas
class LatencyMetrics(BaseModel):
    mean: float
    median: float
    p90: float
    p95: float
    p99: float
    min: float
    max: float


class PrecisionRecallMetrics(BaseModel):
    precision_at_k: Dict[int, float]
    recall_at_k: Dict[int, float]
    ndcg_at_k: Dict[int, float]
    mrr: float


class QualityMetrics(BaseModel):
    semantic_coherence: float
    diversity: float
    stability: float
    coverage: float


class UsageMetrics(BaseModel):
    total_searches: int
    unique_queries: int
    avg_results_per_query: float
    most_common_queries: List[tuple]
    search_patterns: Dict[str, int]


class PerformanceMetrics(BaseModel):
    latency: LatencyMetrics
    precision_recall: PrecisionRecallMetrics
    quality: QualityMetrics
    usage: UsageMetrics
    timestamp: datetime


class MetricsExportRequest(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    metric_types: List[MetricType] = Field(default_factory=list)
    format: str = Field(default="json", pattern="^(json|csv)$")
    include_raw_data: bool = False


class ExperimentConfig(BaseModel):
    experiment_id: str
    embedding_model: str
    chunk_strategy: str
    search_params: Dict[str, Any]
    description: Optional[str] = None


class ExperimentResult(BaseModel):
    experiment_id: str
    config: ExperimentConfig
    metrics: PerformanceMetrics
    test_queries: List[str]
    execution_time: float
    created_at: datetime


# Schemas para sugerencias
class SearchSuggestion(BaseModel):
    query: str
    frequency: int
    relevance_score: float


class SearchSuggestionsResponse(BaseModel):
    suggestions: List[SearchSuggestion]
    total_suggestions: int


# Schemas para análisis
class DocumentAnalysis(BaseModel):
    document_id: str
    total_chunks: int
    avg_chunk_size: int
    semantic_density: float
    topic_distribution: Dict[str, float]
    key_terms: List[str]


class CollectionAnalysis(BaseModel):
    total_documents: int
    total_chunks: int
    avg_chunks_per_document: float
    semantic_coverage: float
    topic_diversity: float
    index_health: Dict[str, float]
    last_updated: datetime


# Schemas para alertas
class AlertConfig(BaseModel):
    metric_type: MetricType
    threshold: float
    condition: str  # "above", "below", "equal"
    enabled: bool = True


class Alert(BaseModel):
    id: str
    config: AlertConfig
    triggered_at: datetime
    current_value: float
    message: str
    severity: str  # "low", "medium", "high", "critical"


# Schemas para configuración
class SystemConfig(BaseModel):
    embedding_model: str
    chunk_strategy: str
    search_defaults: Dict[str, Any]
    cache_settings: Dict[str, Any]
    alert_configs: List[AlertConfig]


class ConfigUpdateRequest(BaseModel):
    embedding_model: Optional[str] = None
    chunk_strategy: Optional[str] = None
    search_defaults: Optional[Dict[str, Any]] = None
    cache_settings: Optional[Dict[str, Any]] = None
