/* eslint-disable @typescript-eslint/no-explicit-any */
export interface SearchResult {
  text: string;
  pdf_name: string;
  chunk_id: string;
  score: number;
  metadata?: Record<string, any>;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  total_results: number;
  search_time: number;
  strategy_used: SearchStrategy;
  query_id: string;
}

export interface SearchRequest {
  query: string;
  limit?: number;
  strategy?: SearchStrategy;
  filters?: Record<string, any>;
  include_metadata?: boolean;
}

export type SearchStrategy = "semantic" | "hybrid" | "keyword";

export interface Document {
  id: string;
  filename: string;
  title?: string;
  description?: string;
  status: DocumentStatus;
  file_size: number;
  chunk_count: number;
  created_at: string;
  updated_at: string;
  processing_time?: number;
  error_message?: string;
}

export type DocumentStatus = "pending" | "processing" | "completed" | "failed";

export interface SearchSuggestion {
  query: string;
  frequency: number;
  relevance_score: number;
}

export interface SearchSuggestionsResponse {
  suggestions: SearchSuggestion[];
  total_suggestions: number;
}

export interface PerformanceMetrics {
  latency: LatencyMetrics;
  precision_recall: PrecisionRecallMetrics;
  quality: QualityMetrics;
  usage: UsageMetrics;
  timestamp: string;
}

export interface LatencyMetrics {
  mean: number;
  median: number;
  p90: number;
  p95: number;
  p99: number;
  min: number;
  max: number;
}

export interface PrecisionRecallMetrics {
  precision_at_k: Record<number, number>;
  recall_at_k: Record<number, number>;
  ndcg_at_k: Record<number, number>;
  mrr: number;
}

export interface QualityMetrics {
  semantic_coherence: number;
  diversity: number;
  stability: number;
  coverage: number;
}

export interface UsageMetrics {
  total_searches: number;
  unique_queries: number;
  avg_results_per_query: number;
  most_common_queries: [string, number][];
  search_patterns: Record<string, number>;
}

export interface ApiError {
  detail: string;
  error?: string;
}

export interface UploadResponse {
  status: string;
  filename: string;
  chunk_count?: number;
  processing_time?: number;
  indexed_at?: string;
  title?: string;
  description?: string;
  file_size?: number;
  error?: string;
}
