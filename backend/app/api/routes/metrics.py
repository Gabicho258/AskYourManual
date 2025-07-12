# app/api/routes/metrics.py
import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from app.models.schemas import (
    PerformanceMetrics,
    MetricsExportRequest,
    ExperimentConfig,
    ExperimentResult,
    MetricType
)
from app.services.metrics_service import MetricsService

logger = logging.getLogger(__name__)

router = APIRouter()

# Variable global que se configurará en main.py
metrics_service: Optional[MetricsService] = None


@router.get("/performance", response_model=PerformanceMetrics)
async def get_performance_metrics():
    """Obtener métricas de rendimiento completas"""
    if not metrics_service:
        raise HTTPException(status_code=500, detail="Metrics service not initialized")
    
    try:
        metrics = await metrics_service.get_performance_metrics()
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Metrics error: {str(e)}")


@router.get("/realtime")
async def get_realtime_metrics():
    """Obtener métricas en tiempo real"""
    if not metrics_service:
        raise HTTPException(status_code=500, detail="Metrics service not initialized")
    
    try:
        metrics = metrics_service.get_real_time_metrics()
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting realtime metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Realtime metrics error: {str(e)}")


@router.post("/export")
async def export_metrics(request: MetricsExportRequest):
    """Exportar métricas en formato especificado"""
    if not metrics_service:
        raise HTTPException(status_code=500, detail="Metrics service not initialized")
    
    try:
        export_data = await metrics_service.export_metrics(request)
        return export_data
        
    except Exception as e:
        logger.error(f"Error exporting metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")


@router.post("/experiments", response_model=ExperimentResult)
async def run_experiment(config: ExperimentConfig, test_queries: List[str]):
    """Ejecutar experimento de rendimiento"""
    if not metrics_service:
        raise HTTPException(status_code=500, detail="Metrics service not initialized")
    
    try:
        result = await metrics_service.run_experiment(config, test_queries)
        return result
        
    except Exception as e:
        logger.error(f"Error running experiment: {e}")
        raise HTTPException(status_code=500, detail=f"Experiment error: {str(e)}")


@router.get("/experiments")
async def list_experiments():
    """Listar experimentos ejecutados"""
    if not metrics_service:
        raise HTTPException(status_code=500, detail="Metrics service not initialized")
    
    try:
        experiments = [
            {
                "experiment_id": exp.experiment_id,
                "created_at": exp.created_at.isoformat(),
                "execution_time": exp.execution_time,
                "config": exp.config.dict()
            }
            for exp in metrics_service.experiment_results
        ]
        
        return {"experiments": experiments, "total": len(experiments)}
        
    except Exception as e:
        logger.error(f"Error listing experiments: {e}")
        raise HTTPException(status_code=500, detail=f"List experiments error: {str(e)}")


@router.post("/experiments/compare")
async def compare_experiments(experiment_ids: List[str]):
    """Comparar resultados de experimentos"""
    if not metrics_service:
        raise HTTPException(status_code=500, detail="Metrics service not initialized")
    
    try:
        comparison = metrics_service.compare_experiments(experiment_ids)
        return comparison
        
    except Exception as e:
        logger.error(f"Error comparing experiments: {e}")
        raise HTTPException(status_code=500, detail=f"Comparison error: {str(e)}")


@router.delete("/")
async def clear_metrics():
    """Limpiar todas las métricas"""
    if not metrics_service:
        raise HTTPException(status_code=500, detail="Metrics service not initialized")
    
    try:
        metrics_service.clear_metrics()
        return {"message": "All metrics cleared successfully"}
        
    except Exception as e:
        logger.error(f"Error clearing metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Clear metrics error: {str(e)}")


@router.get("/alerts")
async def check_alerts():
    """Verificar alertas activas"""
    if not metrics_service:
        raise HTTPException(status_code=500, detail="Metrics service not initialized")
    
    try:
        current_metrics = await metrics_service.get_performance_metrics()
        alerts = metrics_service.check_alerts(current_metrics)
        return {"alerts": alerts, "total": len(alerts)}
        
    except Exception as e:
        logger.error(f"Error checking alerts: {e}")
        raise HTTPException(status_code=500, detail=f"Alerts error: {str(e)}")