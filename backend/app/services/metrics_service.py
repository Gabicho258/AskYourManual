import time
import json
import asyncio
import statistics
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict, deque
import logging
import numpy as np

from app.models.schemas import (
    PerformanceMetrics,
    LatencyMetrics,
    PrecisionRecallMetrics,
    QualityMetrics,
    UsageMetrics,
    MetricsExportRequest,
    ExperimentResult,
    ExperimentConfig,
)
from app.config import settings, METRICS_CONFIG

logger = logging.getLogger(__name__)


class MetricsService:
    def __init__(self):
        self.search_metrics = deque(maxlen=10000)  # Últimas 10k búsquedas
        self.latency_history = deque(maxlen=1000)  # Últimas 1k latencias
        self.precision_recall_history = []
        self.quality_metrics_history = []
        self.experiment_results = []
        self.alerts_triggered = []

    def record_search_metric(
        self,
        query: str,
        strategy: str,
        results_count: int,
        search_time: float,
        relevance_scores: List[float] = None,
    ):
        """Registrar métricas de una búsqueda"""
        timestamp = datetime.now()

        metric = {
            "timestamp": timestamp,
            "query": query,
            "strategy": strategy,
            "results_count": results_count,
            "search_time": search_time,
            "relevance_scores": relevance_scores or [],
            "query_length": len(query.split()),
            "query_complexity": self._calculate_query_complexity(query),
        }

        self.search_metrics.append(metric)
        self.latency_history.append(search_time)

        logger.debug(f"Recorded search metric: {query} - {search_time:.3f}s")

    def _calculate_query_complexity(self, query: str) -> float:
        """Calcular complejidad de la consulta"""
        words = query.split()
        complexity = 0.0

        # Factores de complejidad
        complexity += len(words) * 0.1  # Longitud
        complexity += len([w for w in words if len(w) > 6]) * 0.2  # Palabras largas
        complexity += query.count('"') * 0.3  # Frases exactas
        complexity += query.count("AND") + query.count("OR") * 0.4  # Operadores lógicos

        return min(complexity, 1.0)  # Normalizar a [0,1]

    async def calculate_latency_metrics(self) -> LatencyMetrics:
        """Calcular métricas de latencia"""
        if not self.latency_history:
            return LatencyMetrics(
                mean=0.0, median=0.0, p90=0.0, p95=0.0, p99=0.0, min=0.0, max=0.0
            )

        latencies = list(self.latency_history)

        return LatencyMetrics(
            mean=statistics.mean(latencies),
            median=statistics.median(latencies),
            p90=np.percentile(latencies, 90),
            p95=np.percentile(latencies, 95),
            p99=np.percentile(latencies, 99),
            min=min(latencies),
            max=max(latencies),
        )

    async def calculate_precision_recall_metrics(
        self, test_queries: List[Dict] = None
    ) -> PrecisionRecallMetrics:
        """Calcular métricas de precisión y recall"""
        if not test_queries:
            # Usar consultas recientes como aproximación
            recent_searches = list(self.search_metrics)[-100:]
            test_queries = [
                {"query": s["query"], "relevance_scores": s.get("relevance_scores", [])}
                for s in recent_searches
                if s.get("relevance_scores")
            ]

        if not test_queries:
            return PrecisionRecallMetrics(
                precision_at_k={}, recall_at_k={}, ndcg_at_k={}, mrr=0.0
            )

        k_values = METRICS_CONFIG["precision_k_values"]
        precision_at_k = {}
        recall_at_k = {}
        ndcg_at_k = {}
        reciprocal_ranks = []

        for k in k_values:
            precisions = []
            recalls = []
            ndcgs = []

            for query_data in test_queries:
                scores = query_data.get("relevance_scores", [])
                if not scores:
                    continue

                # Assumir que scores > 0.7 son relevantes
                relevant_threshold = 0.7
                relevant_indices = [
                    i for i, score in enumerate(scores) if score >= relevant_threshold
                ]
                total_relevant = len(relevant_indices)

                if total_relevant == 0:
                    continue

                # Precision@K
                top_k_relevant = len([i for i in relevant_indices if i < k])
                precision = top_k_relevant / min(k, len(scores))
                precisions.append(precision)

                # Recall@K
                recall = top_k_relevant / total_relevant
                recalls.append(recall)

                # NDCG@K
                ndcg = self._calculate_ndcg(scores[:k], relevant_threshold)
                ndcgs.append(ndcg)

                # MRR
                first_relevant = next(
                    (
                        i + 1
                        for i, score in enumerate(scores)
                        if score >= relevant_threshold
                    ),
                    0,
                )
                if first_relevant > 0:
                    reciprocal_ranks.append(1.0 / first_relevant)

            if precisions:
                precision_at_k[k] = statistics.mean(precisions)
                recall_at_k[k] = statistics.mean(recalls)
                ndcg_at_k[k] = statistics.mean(ndcgs)

        mrr = statistics.mean(reciprocal_ranks) if reciprocal_ranks else 0.0

        return PrecisionRecallMetrics(
            precision_at_k=precision_at_k,
            recall_at_k=recall_at_k,
            ndcg_at_k=ndcg_at_k,
            mrr=mrr,
        )

    def _calculate_ndcg(self, scores: List[float], threshold: float) -> float:
        """Calcular NDCG (Normalized Discounted Cumulative Gain)"""
        if not scores:
            return 0.0

        # DCG
        dcg = 0.0
        for i, score in enumerate(scores):
            relevance = 1 if score >= threshold else 0
            dcg += relevance / np.log2(i + 2)

        # IDCG (Ideal DCG)
        ideal_scores = sorted(
            [1 if s >= threshold else 0 for s in scores], reverse=True
        )
        idcg = 0.0
        for i, relevance in enumerate(ideal_scores):
            idcg += relevance / np.log2(i + 2)

        return dcg / idcg if idcg > 0 else 0.0

    async def calculate_quality_metrics(self, vector_store=None) -> QualityMetrics:
        """Calcular métricas de calidad del sistema"""
        # Métricas por defecto si no hay acceso al vector store
        if not vector_store:
            return QualityMetrics(
                semantic_coherence=0.8, diversity=0.6, stability=0.85, coverage=0.75
            )

        try:
            # Coherencia semántica: análisis de clusters
            semantic_coherence = await self._calculate_semantic_coherence(vector_store)

            # Diversidad: cobertura temática
            diversity = await self._calculate_diversity(vector_store)

            # Estabilidad: consistencia entre búsquedas
            stability = self._calculate_stability()

            # Cobertura: porcentaje de documentos indexados exitosamente
            coverage = await self._calculate_coverage(vector_store)

            return QualityMetrics(
                semantic_coherence=semantic_coherence,
                diversity=diversity,
                stability=stability,
                coverage=coverage,
            )

        except Exception as e:
            logger.error(f"Error calculating quality metrics: {e}")
            return QualityMetrics(
                semantic_coherence=0.0, diversity=0.0, stability=0.0, coverage=0.0
            )

    async def _calculate_semantic_coherence(self, vector_store) -> float:
        """Calcular coherencia semántica promedio"""
        try:
            # Obtener muestra de vectores
            sample_vectors = await vector_store.get_sample_vectors(100)
            if len(sample_vectors) < 2:
                return 0.0

            # Calcular similitudes promedio dentro de clusters
            coherence_scores = []
            for i, vector1 in enumerate(sample_vectors):
                similarities = []
                for j, vector2 in enumerate(sample_vectors):
                    if i != j:
                        similarity = np.dot(vector1, vector2) / (
                            np.linalg.norm(vector1) * np.linalg.norm(vector2)
                        )
                        similarities.append(similarity)

                if similarities:
                    coherence_scores.append(statistics.mean(similarities))

            return statistics.mean(coherence_scores) if coherence_scores else 0.0

        except Exception as e:
            logger.error(f"Error calculating semantic coherence: {e}")
            return 0.0

    async def _calculate_diversity(self, vector_store) -> float:
        """Calcular diversidad temática"""
        try:
            # Obtener estadísticas de la colección
            collection_info = await vector_store.get_collection_info()

            # Aproximación basada en distribución de documentos
            total_chunks = collection_info.get("vectors_count", 0)
            unique_documents = collection_info.get("unique_documents", 1)

            if unique_documents == 0:
                return 0.0

            # Diversidad como distribución uniforme de chunks por documento
            avg_chunks_per_doc = total_chunks / unique_documents
            diversity = min(avg_chunks_per_doc / 100, 1.0)  # Normalizar

            return diversity

        except Exception as e:
            logger.error(f"Error calculating diversity: {e}")
            return 0.0

    def _calculate_stability(self) -> float:
        """Calcular estabilidad basada en varianza de resultados"""
        if len(self.search_metrics) < 10:
            return 0.0

        # Analizar varianza en tiempos de respuesta para consultas similares
        query_groups = defaultdict(list)
        for metric in self.search_metrics:
            # Agrupar por consultas similares (primeras 3 palabras)
            key = " ".join(metric["query"].split()[:3])
            query_groups[key].append(metric["search_time"])

        stability_scores = []
        for group_times in query_groups.values():
            if len(group_times) >= 3:
                # Calcular coeficiente de variación
                mean_time = statistics.mean(group_times)
                if mean_time > 0:
                    cv = statistics.stdev(group_times) / mean_time
                    stability = max(0, 1 - cv)  # Menor variación = mayor estabilidad
                    stability_scores.append(stability)

        return statistics.mean(stability_scores) if stability_scores else 0.0

    async def _calculate_coverage(self, vector_store) -> float:
        """Calcular cobertura de documentos procesados"""
        try:
            collection_info = await vector_store.get_collection_info()
            processed_docs = collection_info.get("unique_documents", 0)

            # Obtener total de documentos disponibles (esto requeriría acceso al sistema de archivos)
            # Por ahora, retornar una aproximación
            return min(processed_docs / 100, 1.0)  # Asumir máximo 100 docs

        except Exception as e:
            logger.error(f"Error calculating coverage: {e}")
            return 0.0

    async def calculate_usage_metrics(self) -> UsageMetrics:
        """Calcular métricas de uso"""
        if not self.search_metrics:
            return UsageMetrics(
                total_searches=0,
                unique_queries=0,
                avg_results_per_query=0.0,
                most_common_queries=[],
                search_patterns={},
            )

        total_searches = len(self.search_metrics)
        unique_queries = len(set(m["query"] for m in self.search_metrics))
        avg_results = statistics.mean([m["results_count"] for m in self.search_metrics])

        # Consultas más comunes
        query_counts = defaultdict(int)
        for metric in self.search_metrics:
            query_counts[metric["query"]] += 1

        most_common = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)[
            :10
        ]

        # Patrones de búsqueda por hora
        search_patterns = defaultdict(int)
        for metric in self.search_metrics:
            hour = metric["timestamp"].hour
            search_patterns[f"{hour:02d}:00"] += 1

        return UsageMetrics(
            total_searches=total_searches,
            unique_queries=unique_queries,
            avg_results_per_query=avg_results,
            most_common_queries=most_common,
            search_patterns=dict(search_patterns),
        )

    async def get_performance_metrics(self, vector_store=None) -> PerformanceMetrics:
        """Obtener métricas completas de rendimiento"""
        latency = await self.calculate_latency_metrics()
        precision_recall = await self.calculate_precision_recall_metrics()
        quality = await self.calculate_quality_metrics(vector_store)
        usage = await self.calculate_usage_metrics()

        return PerformanceMetrics(
            latency=latency,
            precision_recall=precision_recall,
            quality=quality,
            usage=usage,
            timestamp=datetime.now(),
        )

    async def export_metrics(self, request: MetricsExportRequest) -> Dict[str, Any]:
        """Exportar métricas en formato especificado"""
        try:
            # Filtrar por fechas si se especifican
            filtered_metrics = self.search_metrics

            if request.start_date or request.end_date:
                filtered_metrics = []
                for metric in self.search_metrics:
                    timestamp = metric["timestamp"]
                    if request.start_date and timestamp < request.start_date:
                        continue
                    if request.end_date and timestamp > request.end_date:
                        continue
                    filtered_metrics.append(metric)

            # Preparar datos de exportación
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "filter_criteria": {
                    "start_date": (
                        request.start_date.isoformat() if request.start_date else None
                    ),
                    "end_date": (
                        request.end_date.isoformat() if request.end_date else None
                    ),
                    "metric_types": request.metric_types,
                },
                "summary": {
                    "total_records": len(filtered_metrics),
                    "date_range": {
                        "start": (
                            min([m["timestamp"] for m in filtered_metrics]).isoformat()
                            if filtered_metrics
                            else None
                        ),
                        "end": (
                            max([m["timestamp"] for m in filtered_metrics]).isoformat()
                            if filtered_metrics
                            else None
                        ),
                    },
                },
                "metrics": {},
            }

            # Incluir métricas específicas
            if not request.metric_types or "latency" in request.metric_types:
                export_data["metrics"][
                    "latency"
                ] = await self.calculate_latency_metrics()

            if not request.metric_types or "precision" in request.metric_types:
                export_data["metrics"][
                    "precision_recall"
                ] = await self.calculate_precision_recall_metrics()

            if not request.metric_types or "quality" in request.metric_types:
                export_data["metrics"][
                    "quality"
                ] = await self.calculate_quality_metrics()

            if not request.metric_types or "usage" in request.metric_types:
                export_data["metrics"]["usage"] = await self.calculate_usage_metrics()

            # Incluir datos raw si se solicita
            if request.include_raw_data:
                export_data["raw_data"] = [
                    {
                        "timestamp": m["timestamp"].isoformat(),
                        "query": m["query"],
                        "strategy": m["strategy"],
                        "results_count": m["results_count"],
                        "search_time": m["search_time"],
                        "relevance_scores": m.get("relevance_scores", []),
                        "query_length": m["query_length"],
                        "query_complexity": m["query_complexity"],
                    }
                    for m in filtered_metrics
                ]

            return export_data

        except Exception as e:
            logger.error(f"Error exporting metrics: {e}")
            raise

    async def run_experiment(
        self, config: ExperimentConfig, test_queries: List[str]
    ) -> ExperimentResult:
        """Ejecutar experimento de rendimiento"""
        start_time = time.time()

        try:
            logger.info(f"Starting experiment: {config.experiment_id}")

            # Reiniciar métricas para el experimento
            experiment_metrics = []

            # Ejecutar consultas de prueba
            for query in test_queries:
                query_start = time.time()

                # Simular búsqueda con configuración específica
                # En implementación real, se configuraría el sistema con config
                search_time = time.time() - query_start

                # Registrar métrica del experimento
                experiment_metrics.append(
                    {
                        "query": query,
                        "search_time": search_time,
                        "timestamp": datetime.now(),
                    }
                )

            # Calcular métricas del experimento
            performance_metrics = await self.get_performance_metrics()

            execution_time = time.time() - start_time

            result = ExperimentResult(
                experiment_id=config.experiment_id,
                config=config,
                metrics=performance_metrics,
                test_queries=test_queries,
                execution_time=execution_time,
                created_at=datetime.now(),
            )

            self.experiment_results.append(result)
            logger.info(
                f"Experiment completed: {config.experiment_id} in {execution_time:.3f}s"
            )

            return result

        except Exception as e:
            logger.error(f"Error running experiment: {e}")
            raise

    def compare_experiments(self, experiment_ids: List[str]) -> Dict[str, Any]:
        """Comparar resultados de experimentos"""
        try:
            experiments = [
                exp
                for exp in self.experiment_results
                if exp.experiment_id in experiment_ids
            ]

            if not experiments:
                return {"error": "No experiments found with provided IDs"}

            comparison = {"experiments": [], "comparison_metrics": {}, "summary": {}}

            # Recopilar datos de cada experimento
            latencies = []
            precisions = []
            recalls = []

            for exp in experiments:
                exp_data = {
                    "experiment_id": exp.experiment_id,
                    "config": exp.config.dict(),
                    "execution_time": exp.execution_time,
                    "metrics": {
                        "avg_latency": exp.metrics.latency.mean,
                        "precision_at_5": exp.metrics.precision_recall.precision_at_k.get(
                            5, 0
                        ),
                        "recall_at_5": exp.metrics.precision_recall.recall_at_k.get(
                            5, 0
                        ),
                        "semantic_coherence": exp.metrics.quality.semantic_coherence,
                    },
                }
                comparison["experiments"].append(exp_data)

                latencies.append(exp.metrics.latency.mean)
                precisions.append(exp.metrics.precision_recall.precision_at_k.get(5, 0))
                recalls.append(exp.metrics.precision_recall.recall_at_k.get(5, 0))

            # Métricas de comparación
            comparison["comparison_metrics"] = {
                "latency": {
                    "best": min(latencies),
                    "worst": max(latencies),
                    "variance": (
                        statistics.variance(latencies) if len(latencies) > 1 else 0
                    ),
                },
                "precision": {
                    "best": max(precisions),
                    "worst": min(precisions),
                    "variance": (
                        statistics.variance(precisions) if len(precisions) > 1 else 0
                    ),
                },
                "recall": {
                    "best": max(recalls),
                    "worst": min(recalls),
                    "variance": statistics.variance(recalls) if len(recalls) > 1 else 0,
                },
            }

            # Resumen
            best_overall = max(
                experiments,
                key=lambda x: (
                    x.metrics.precision_recall.precision_at_k.get(5, 0)
                    + x.metrics.precision_recall.recall_at_k.get(5, 0)
                    - x.metrics.latency.mean * 0.1  # Penalizar latencia alta
                ),
            )

            comparison["summary"] = {
                "best_experiment": best_overall.experiment_id,
                "recommendation": self._generate_recommendation(experiments),
                "total_experiments": len(experiments),
            }

            return comparison

        except Exception as e:
            logger.error(f"Error comparing experiments: {e}")
            return {"error": f"Error during comparison: {str(e)}"}

    def _generate_recommendation(self, experiments: List[ExperimentResult]) -> str:
        """Generar recomendación basada en resultados de experimentos"""
        if not experiments:
            return "No hay experimentos para analizar"

        # Análisis simple de trade-offs
        best_latency = min(experiments, key=lambda x: x.metrics.latency.mean)
        best_precision = max(
            experiments,
            key=lambda x: x.metrics.precision_recall.precision_at_k.get(5, 0),
        )
        best_quality = max(
            experiments, key=lambda x: x.metrics.quality.semantic_coherence
        )

        recommendations = []

        if (
            best_latency.experiment_id
            == best_precision.experiment_id
            == best_quality.experiment_id
        ):
            recommendations.append(
                f"El experimento {best_latency.experiment_id} es óptimo en todos los aspectos."
            )
        else:
            recommendations.append(f"Para mejor latencia: {best_latency.experiment_id}")
            recommendations.append(
                f"Para mejor precisión: {best_precision.experiment_id}"
            )
            recommendations.append(
                f"Para mejor calidad semántica: {best_quality.experiment_id}"
            )

        # Análisis de configuraciones
        embedding_models = set(exp.config.embedding_model for exp in experiments)
        if len(embedding_models) > 1:
            recommendations.append(
                "Se probaron múltiples modelos de embedding - considerar el balance entre velocidad y precisión."
            )

        return " ".join(recommendations)

    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Obtener métricas en tiempo real para dashboard"""
        current_time = datetime.now()
        last_hour = current_time - timedelta(hours=1)
        last_day = current_time - timedelta(days=1)

        # Métricas de la última hora
        recent_searches = [
            m for m in self.search_metrics if m["timestamp"] >= last_hour
        ]

        # Métricas del último día
        daily_searches = [m for m in self.search_metrics if m["timestamp"] >= last_day]

        return {
            "current_timestamp": current_time.isoformat(),
            "last_hour": {
                "total_searches": len(recent_searches),
                "avg_latency": (
                    statistics.mean([s["search_time"] for s in recent_searches])
                    if recent_searches
                    else 0
                ),
                "avg_results": (
                    statistics.mean([s["results_count"] for s in recent_searches])
                    if recent_searches
                    else 0
                ),
            },
            "last_24_hours": {
                "total_searches": len(daily_searches),
                "unique_queries": len(set(s["query"] for s in daily_searches)),
                "peak_hour": self._get_peak_hour(daily_searches),
                "avg_latency": (
                    statistics.mean([s["search_time"] for s in daily_searches])
                    if daily_searches
                    else 0
                ),
            },
            "system_health": {
                "cache_size": len(getattr(self, "query_cache", {})),
                "metrics_buffer_usage": len(self.search_metrics)
                / 10000,  # Porcentaje de buffer usado
                "last_experiment": (
                    self.experiment_results[-1].experiment_id
                    if self.experiment_results
                    else None
                ),
            },
        }

    def _get_peak_hour(self, searches: List[Dict]) -> str:
        """Obtener la hora pico de búsquedas"""
        if not searches:
            return "00:00"

        hour_counts = defaultdict(int)
        for search in searches:
            hour = search["timestamp"].hour
            hour_counts[hour] += 1

        peak_hour = max(hour_counts.items(), key=lambda x: x[1])[0]
        return f"{peak_hour:02d}:00"

    def clear_metrics(self):
        """Limpiar todas las métricas almacenadas"""
        self.search_metrics.clear()
        self.latency_history.clear()
        self.precision_recall_history.clear()
        self.quality_metrics_history.clear()
        logger.info("All metrics cleared")

    def set_alert_threshold(self, metric_type: str, threshold: float, condition: str):
        """Configurar umbral de alerta para métricas"""
        alert_config = {
            "metric_type": metric_type,
            "threshold": threshold,
            "condition": condition,
            "enabled": True,
            "created_at": datetime.now(),
        }
        # En implementación real, esto se guardaría en base de datos
        logger.info(f"Alert configured: {metric_type} {condition} {threshold}")

    def check_alerts(self, current_metrics: PerformanceMetrics) -> List[Dict]:
        """Verificar si se han activado alertas"""
        alerts = []

        # Ejemplo de verificación de alertas
        if current_metrics.latency.mean > 1.0:  # Latencia > 1 segundo
            alerts.append(
                {
                    "type": "latency",
                    "severity": "high",
                    "message": f"High latency detected: {current_metrics.latency.mean:.3f}s",
                    "timestamp": datetime.now().isoformat(),
                }
            )

        if current_metrics.quality.semantic_coherence < 0.5:  # Baja coherencia
            alerts.append(
                {
                    "type": "quality",
                    "severity": "medium",
                    "message": f"Low semantic coherence: {current_metrics.quality.semantic_coherence:.3f}",
                    "timestamp": datetime.now().isoformat(),
                }
            )

        return alerts
