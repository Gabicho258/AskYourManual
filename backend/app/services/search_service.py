import time
import uuid
import asyncio
from typing import List, Dict, Any, Optional
from collections import defaultdict, Counter
import logging

from app.models.schemas import (
    SearchRequest,
    SearchResponse,
    SearchResult,
    BatchSearchRequest,
    BatchSearchResponse,
    SearchStrategy,
    SearchSuggestion,
    SearchSuggestionsResponse,
)
from app.services.embedding_service import EmbeddingService
from app.core.vector_store import VectorStore
from app.config import settings

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(self, embedding_service: EmbeddingService, vector_store: VectorStore):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.search_history = []
        self.query_cache = {}
        self.suggestion_cache = {}

    async def search(self, request: SearchRequest) -> SearchResponse:
        """Realizar búsqueda semántica"""
        start_time = time.time()
        query_id = str(uuid.uuid4())

        try:
            # Verificar caché
            cache_key = f"{request.query}_{request.limit}_{request.strategy}"
            if cache_key in self.query_cache:
                cached_result = self.query_cache[cache_key]
                if time.time() - cached_result["timestamp"] < settings.CACHE_TTL:
                    logger.info(f"Cache hit for query: {request.query}")
                    cached_result["response"].query_id = query_id
                    return cached_result["response"]

            # Realizar búsqueda según estrategia
            if request.strategy == SearchStrategy.SEMANTIC:
                results = await self._semantic_search(request)
            elif request.strategy == SearchStrategy.HYBRID:
                results = await self._hybrid_search(request)
            elif request.strategy == SearchStrategy.KEYWORD:
                results = await self._keyword_search(request)
            else:
                raise ValueError(
                    f"Estrategia de búsqueda no soportada: {request.strategy}"
                )

            search_time = time.time() - start_time

            # Crear respuesta
            response = SearchResponse(
                query=request.query,
                results=results,
                total_results=len(results),
                search_time=search_time,
                strategy_used=request.strategy,
                query_id=query_id,
            )

            # Guardar en caché y historial
            if len(self.query_cache) < settings.MAX_CACHE_SIZE:
                self.query_cache[cache_key] = {
                    "response": response,
                    "timestamp": time.time(),
                }

            self.search_history.append(
                {
                    "query": request.query,
                    "strategy": request.strategy,
                    "results_count": len(results),
                    "search_time": search_time,
                    "timestamp": time.time(),
                    "query_id": query_id,
                }
            )

            logger.info(
                f"Search completed: {request.query} - {len(results)} results in {search_time:.3f}s"
            )
            return response

        except Exception as e:
            logger.error(f"Error in search: {e}")
            raise

    async def _semantic_search(self, request: SearchRequest) -> List[SearchResult]:
        """Búsqueda semántica usando embeddings"""
        try:
            # Generar embedding de la consulta
            query_vector = await self.embedding_service.embed_query(request.query)

            # Buscar en Qdrant
            search_results = await self.vector_store.search(
                query_vector=query_vector, limit=request.limit, filters=request.filters
            )

            # Convertir a formato de respuesta
            results = []
            for hit in search_results:
                result = SearchResult(
                    text=hit.payload.get("text", ""),
                    pdf_name=hit.payload.get("pdf_name", ""),
                    chunk_id=hit.payload.get("chunk_id", ""),
                    score=float(hit.score),
                    metadata=hit.payload if request.include_metadata else None,
                )
                results.append(result)

            return results

        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            raise

    async def _hybrid_search(self, request: SearchRequest) -> List[SearchResult]:
        """Búsqueda híbrida combinando semántica y texto completo"""
        try:
            # Realizar búsqueda semántica
            semantic_results = await self._semantic_search(request)

            # Realizar búsqueda por palabras clave
            keyword_results = await self._keyword_search(request)

            # Combinar y rerank resultados
            combined_results = self._combine_results(
                semantic_results,
                keyword_results,
                semantic_weight=0.7,
                keyword_weight=0.3,
            )

            return combined_results[: request.limit]

        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            raise

    async def _keyword_search(self, request: SearchRequest) -> List[SearchResult]:
        """Búsqueda por palabras clave"""
        try:
            # Implementar búsqueda por palabras clave usando filtros
            filters = {"must": [{"key": "text", "match": {"text": request.query}}]}

            if request.filters:
                filters["must"].extend(request.filters.get("must", []))

            # Buscar documentos que contengan las palabras clave
            search_results = await self.vector_store.search_with_filters(
                filters=filters, limit=request.limit
            )

            # Convertir a formato de respuesta
            results = []
            for hit in search_results:
                # Calcular score basado en frecuencia de términos
                score = self._calculate_keyword_score(
                    request.query, hit.payload.get("text", "")
                )

                result = SearchResult(
                    text=hit.payload.get("text", ""),
                    pdf_name=hit.payload.get("pdf_name", ""),
                    chunk_id=hit.payload.get("chunk_id", ""),
                    score=score,
                    metadata=hit.payload if request.include_metadata else None,
                )
                results.append(result)

            # Ordenar por score
            results.sort(key=lambda x: x.score, reverse=True)
            return results

        except Exception as e:
            logger.error(f"Error in keyword search: {e}")
            raise

    def _combine_results(
        self,
        semantic_results: List[SearchResult],
        keyword_results: List[SearchResult],
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3,
    ) -> List[SearchResult]:
        """Combinar resultados de búsqueda semántica y por palabras clave"""

        # Crear diccionario para combinar scores
        combined_scores = {}

        # Añadir scores semánticos
        for result in semantic_results:
            key = f"{result.pdf_name}_{result.chunk_id}"
            combined_scores[key] = {
                "result": result,
                "semantic_score": result.score * semantic_weight,
                "keyword_score": 0.0,
            }

        # Añadir scores de palabras clave
        for result in keyword_results:
            key = f"{result.pdf_name}_{result.chunk_id}"
            if key in combined_scores:
                combined_scores[key]["keyword_score"] = result.score * keyword_weight
            else:
                combined_scores[key] = {
                    "result": result,
                    "semantic_score": 0.0,
                    "keyword_score": result.score * keyword_weight,
                }

        # Calcular score final y crear lista de resultados
        final_results = []
        for key, data in combined_scores.items():
            final_score = data["semantic_score"] + data["keyword_score"]
            result = data["result"]
            result.score = final_score
            final_results.append(result)

        # Ordenar por score final
        final_results.sort(key=lambda x: x.score, reverse=True)
        return final_results

    def _calculate_keyword_score(self, query: str, text: str) -> float:
        """Calcular score para búsqueda por palabras clave"""
        query_terms = query.lower().split()
        text_lower = text.lower()

        score = 0.0
        for term in query_terms:
            # Contar occurrencias del término
            count = text_lower.count(term)
            if count > 0:
                # TF-IDF simplificado
                tf = count / len(text_lower.split())
                score += tf

        return score

    async def batch_search(self, request: BatchSearchRequest) -> BatchSearchResponse:
        """Realizar búsquedas por lotes"""
        start_time = time.time()
        batch_id = str(uuid.uuid4())

        try:
            # Crear tareas de búsqueda
            search_tasks = []
            for query in request.queries:
                search_request = SearchRequest(
                    query=query, limit=request.limit, strategy=request.strategy
                )
                task = self.search(search_request)
                search_tasks.append(task)

            # Ejecutar búsquedas en paralelo
            results = await asyncio.gather(*search_tasks, return_exceptions=True)

            # Filtrar errores
            valid_results = [r for r in results if isinstance(r, SearchResponse)]

            total_time = time.time() - start_time

            response = BatchSearchResponse(
                results=valid_results, total_search_time=total_time, batch_id=batch_id
            )

            logger.info(
                f"Batch search completed: {len(request.queries)} queries in {total_time:.3f}s"
            )
            return response

        except Exception as e:
            logger.error(f"Error in batch search: {e}")
            raise

    async def get_suggestions(
        self, query: str, limit: int = 5
    ) -> SearchSuggestionsResponse:
        """Obtener sugerencias de búsqueda"""
        try:
            # Verificar caché de sugerencias
            if query in self.suggestion_cache:
                cached = self.suggestion_cache[query]
                if time.time() - cached["timestamp"] < settings.CACHE_TTL:
                    return cached["suggestions"]

            # Generar sugerencias basadas en historial
            suggestions = self._generate_suggestions(query, limit)

            response = SearchSuggestionsResponse(
                suggestions=suggestions, total_suggestions=len(suggestions)
            )

            # Guardar en caché
            self.suggestion_cache[query] = {
                "suggestions": response,
                "timestamp": time.time(),
            }

            return response

        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return SearchSuggestionsResponse(suggestions=[], total_suggestions=0)

    def _generate_suggestions(self, query: str, limit: int) -> List[SearchSuggestion]:
        """Generar sugerencias basadas en historial de búsquedas"""
        query_lower = query.lower()
        suggestions = []

        # Contar consultas similares en el historial
        query_counts = Counter()
        for search in self.search_history:
            search_query = search["query"].lower()
            if query_lower in search_query or search_query in query_lower:
                query_counts[search["query"]] += 1

        # Crear sugerencias
        for query_text, frequency in query_counts.most_common(limit):
            if query_text.lower() != query_lower:
                # Calcular score de relevancia simple
                relevance = self._calculate_relevance(query, query_text)
                suggestion = SearchSuggestion(
                    query=query_text, frequency=frequency, relevance_score=relevance
                )
                suggestions.append(suggestion)

        # Ordenar por relevancia
        suggestions.sort(key=lambda x: x.relevance_score, reverse=True)
        return suggestions

    def _calculate_relevance(self, query1: str, query2: str) -> float:
        """Calcular relevancia entre dos consultas"""
        words1 = set(query1.lower().split())
        words2 = set(query2.lower().split())

        if not words1 or not words2:
            return 0.0

        # Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        return intersection / union if union > 0 else 0.0

    def get_search_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de búsqueda"""
        if not self.search_history:
            return {}

        total_searches = len(self.search_history)
        avg_search_time = (
            sum(s["search_time"] for s in self.search_history) / total_searches
        )
        avg_results = (
            sum(s["results_count"] for s in self.search_history) / total_searches
        )

        # Consultas más comunes
        query_counts = Counter(s["query"] for s in self.search_history)
        most_common = query_counts.most_common(10)

        # Estrategias más usadas
        strategy_counts = Counter(s["strategy"] for s in self.search_history)

        return {
            "total_searches": total_searches,
            "avg_search_time": avg_search_time,
            "avg_results_per_query": avg_results,
            "most_common_queries": most_common,
            "strategy_distribution": dict(strategy_counts),
            "cache_hit_rate": len(self.query_cache) / max(total_searches, 1),
        }

    def clear_cache(self):
        """Limpiar caché de consultas"""
        self.query_cache.clear()
        self.suggestion_cache.clear()
        logger.info("Search cache cleared")
