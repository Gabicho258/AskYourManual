import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.config import settings
from app.api.routes import search, documents, metrics
from app.services.pdf_service import PDFService
from app.services.embedding_service import EmbeddingService
from app.services.search_service import SearchService
from app.services.metrics_service import MetricsService
from app.core.vector_store import VectorStore

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Servicios globales
pdf_service = None
embedding_service = None
search_service = None
metrics_service = None
vector_store = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    global pdf_service, embedding_service, search_service, metrics_service, vector_store

    try:
        logger.info("Iniciando servicios...")

        # Inicializar servicios
        embedding_service = EmbeddingService()
        vector_store = VectorStore()
        await vector_store.initialize()

        pdf_service = PDFService(embedding_service, vector_store)
        search_service = SearchService(embedding_service, vector_store)
        metrics_service = MetricsService()

        # Configurar servicios en las rutas
        search.search_service = search_service
        search.metrics_service = metrics_service
        documents.pdf_service = pdf_service
        documents.metrics_service = metrics_service
        metrics.metrics_service = metrics_service

        logger.info("Servicios inicializados correctamente")

        # Procesar PDFs existentes en background
        asyncio.create_task(pdf_service.process_existing_pdfs())

        yield

    except Exception as e:
        logger.error(f"Error durante la inicialización: {e}")
        raise
    finally:
        logger.info("Cerrando servicios...")
        if vector_store:
            await vector_store.close()


app = FastAPI(
    title="PDF Search System",
    description="Sistema de búsqueda semántica sobre documentos PDF con métricas de rendimiento",
    version="1.0.0",
    lifespan=lifespan,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rutas
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])


@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/")
async def root():
    """Endpoint raíz"""
    return {"message": "PDF Search System API", "docs": "/docs", "health": "/health"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Manejo global de excepciones"""
    logger.error(f"Error no controlado: {exc}")
    return JSONResponse(
        status_code=500, content={"detail": "Error interno del servidor"}
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
