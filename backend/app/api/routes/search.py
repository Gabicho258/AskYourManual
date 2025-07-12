# app/api/routes/search.py
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse

from app.models.schemas import (
    SearchRequest,
    SearchResponse,
    BatchSearchRequest,
    BatchSearchResponse,
    SearchSuggestionsResponse,
    SearchStrategy
)
from app.services.search_service import SearchService
from app.services.metrics_service import MetricsService

logger = logging.getLogger(__name__)

router = APIRouter()

# Variables globales que se configurarán en main.py
search_service: Optional[SearchService] = None
metrics_service: Optional[MetricsService] = None


@router.post("/", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """Buscar en documentos PDF"""
    if not search_service:
        raise HTTPException(status_code=500, detail="Search service not initialized")
    
    try:
        # Realizar búsqueda
        response = await search_service.search(request)
        
        # Registrar métricas
        if metrics_service:
            relevance_scores = [result.score for result in response.results]
            metrics_service.record_search_metric(
                query=request.query,
                strategy=request.strategy.value,
                results_count=response.total_results,
                search_time=response.search_time,
                relevance_scores=relevance_scores
            )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in search: {e}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.post("/batch", response_model=BatchSearchResponse)
async def batch_search_documents(request: BatchSearchRequest):
    """Realizar búsquedas por lotes"""
    if not search_service:
        raise HTTPException(status_code=500, detail="Search service not initialized")
    
    try:
        response = await search_service.batch_search(request)
        return response
        
    except Exception as e:
        logger.error(f"Error in batch search: {e}")
        raise HTTPException(status_code=500, detail=f"Batch search error: {str(e)}")


@router.get("/suggestions", response_model=SearchSuggestionsResponse)
async def get_search_suggestions(
    query: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(default=5, ge=1, le=20)
):
    """Obtener sugerencias de búsqueda"""
    if not search_service:
        raise HTTPException(status_code=500, detail="Search service not initialized")
    
    try:
        response = await search_service.get_suggestions(query, limit)
        return response
        
    except Exception as e:
        logger.error(f"Error getting suggestions: {e}")
        raise HTTPException(status_code=500, detail=f"Suggestions error: {str(e)}")


@router.get("/stats")
async def get_search_stats():
    """Obtener estadísticas de búsqueda"""
    if not search_service:
        raise HTTPException(status_code=500, detail="Search service not initialized")
    
    try:
        stats = search_service.get_search_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting search stats: {e}")
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")


@router.delete("/cache")
async def clear_search_cache():
    """Limpiar caché de búsquedas"""
    if not search_service:
        raise HTTPException(status_code=500, detail="Search service not initialized")
    
    try:
        search_service.clear_cache()
        return {"message": "Search cache cleared successfully"}
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=f"Cache clear error: {str(e)}")
