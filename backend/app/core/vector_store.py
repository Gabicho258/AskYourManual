# app/core/vector_store.py - Versión corregida que auto-crea la colección
import uuid
import asyncio
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.models import Distance, VectorParams, PointStruct
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self):
        self.client = None
        self.collection_name = settings.QDRANT_COLLECTION
        self.is_initialized = False
        self.collection_exists = False

    async def initialize(self):
        """Inicializar conexión con Qdrant"""
        try:
            self.client = QdrantClient(
                host=settings.QDRANT_HOST, port=settings.QDRANT_PORT, timeout=30
            )

            # Verificar conexión
            collections = self.client.get_collections()
            logger.info(
                f"Connected to Qdrant. Collections: {len(collections.collections)}"
            )

            # Verificar si la colección existe
            existing_collections = [col.name for col in collections.collections]
            if self.collection_name in existing_collections:
                self.collection_exists = True
                logger.info(f"Collection {self.collection_name} already exists")
            else:
                logger.info(f"Collection {self.collection_name} does not exist. Will create on first use.")

            self.is_initialized = True

        except Exception as e:
            logger.error(f"Failed to initialize Qdrant client: {e}")
            raise

    async def ensure_collection_exists(self, vector_dim: int = 384):
        """Asegurar que la colección existe antes de indexar"""
        if self.collection_exists:
            return

        try:
            logger.info(f"Creating collection: {self.collection_name}")
            
            # Crear nueva colección
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_dim, distance=Distance.COSINE),
            )

            # Crear índices para mejor rendimiento
            try:
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="pdf_name",
                    field_schema=models.PayloadSchemaType.KEYWORD,
                )
                logger.info("Created index for pdf_name field")
            except Exception as e:
                logger.warning(f"Could not create pdf_name index: {e}")

            try:
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="chunk_id",
                    field_schema=models.PayloadSchemaType.KEYWORD,
                )
                logger.info("Created index for chunk_id field")
            except Exception as e:
                logger.warning(f"Could not create chunk_id index: {e}")

            self.collection_exists = True
            logger.info(f"Collection {self.collection_name} created successfully")

        except Exception as e:
            if "already exists" in str(e).lower():
                self.collection_exists = True
                logger.info(f"Collection {self.collection_name} already exists")
            else:
                logger.error(f"Error creating collection: {e}")
                raise

    async def create_collection(self, vector_dim: int, force_recreate: bool = False):
        """Crear colección en Qdrant"""
        try:
            # Verificar si la colección existe
            try:
                collection_info = self.client.get_collection(self.collection_name)
                if force_recreate:
                    logger.info(f"Recreating collection: {self.collection_name}")
                    self.client.delete_collection(self.collection_name)
                    self.collection_exists = False
                else:
                    logger.info(f"Collection {self.collection_name} already exists")
                    self.collection_exists = True
                    return
            except Exception:
                # La colección no existe, crearla
                pass

            await self.ensure_collection_exists(vector_dim)

        except Exception as e:
            logger.error(f"Error in create_collection: {e}")
            raise

    async def index_chunks(
        self,
        vectors: List[List[float]],
        chunks: List[str],
        pdf_name: str,
        metadata: Optional[List[Dict]] = None,
    ):
        """Indexar chunks en Qdrant"""
        try:
            if not self.client:
                raise RuntimeError("Vector store not initialized")

            if not vectors:
                logger.warning("No vectors provided for indexing")
                return 0

            # Asegurar que la colección existe antes de indexar
            vector_dim = len(vectors[0]) if vectors else 384
            await self.ensure_collection_exists(vector_dim)

            points = []
            for i, (vector, chunk) in enumerate(zip(vectors, chunks)):
                chunk_id = str(uuid.uuid4())

                payload = {
                    "text": chunk,
                    "pdf_name": pdf_name,
                    "chunk_id": chunk_id,
                    "chunk_index": i,
                    "indexed_at": str(asyncio.get_event_loop().time()),
                }

                # Añadir metadata adicional si se proporciona
                if metadata and i < len(metadata):
                    payload.update(metadata[i])

                point = PointStruct(id=chunk_id, vector=vector, payload=payload)
                points.append(point)

            # Insertar puntos en lotes para mejor rendimiento
            batch_size = 100
            total_indexed = 0
            
            for i in range(0, len(points), batch_size):
                batch = points[i : i + batch_size]
                
                try:
                    self.client.upsert(collection_name=self.collection_name, points=batch)
                    total_indexed += len(batch)
                    logger.debug(f"Indexed batch {i//batch_size + 1}: {len(batch)} points")
                except Exception as e:
                    logger.error(f"Error indexing batch {i//batch_size + 1}: {e}")
                    # Continuar con los siguientes lotes
                    continue

            logger.info(f"Successfully indexed {total_indexed}/{len(points)} chunks for {pdf_name}")
            return total_indexed

        except Exception as e:
            logger.error(f"Error indexing chunks: {e}")
            raise

    async def search(
        self,
        query_vector: List[float],
        limit: int = 10,
        filters: Optional[Dict] = None,
        score_threshold: float = 0.0,
    ):
        """Buscar vectores similares"""
        try:
            if not self.client:
                raise RuntimeError("Vector store not initialized")

            if not self.collection_exists:
                logger.warning(f"Collection {self.collection_name} does not exist. No results returned.")
                return []

            # Construir filtros de Qdrant
            qdrant_filter = None
            if filters:
                qdrant_filter = self._build_qdrant_filter(filters)

            # Realizar búsqueda
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                query_filter=qdrant_filter,
                score_threshold=score_threshold,
                with_payload=True,
                with_vectors=False,
            )

            return search_result

        except Exception as e:
            logger.error(f"Error during search: {e}")
            if "does not exist" in str(e).lower():
                logger.warning("Collection does not exist. Returning empty results.")
                return []
            raise

    async def search_with_filters(self, filters: Dict, limit: int = 10):
        """Buscar con filtros específicos (para búsqueda por palabras clave)"""
        try:
            if not self.client:
                raise RuntimeError("Vector store not initialized")

            if not self.collection_exists:
                logger.warning(f"Collection {self.collection_name} does not exist. No results returned.")
                return []

            # Para búsqueda por texto, usar scroll con filtros
            qdrant_filter = self._build_qdrant_filter(filters)

            points, _ = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=qdrant_filter,
                limit=limit,
                with_payload=True,
                with_vectors=False,
            )

            # Simular estructura de search result
            class MockHit:
                def __init__(self, point):
                    self.payload = point.payload
                    self.score = 1.0  # Score neutro para filtros
                    self.id = point.id

            return [MockHit(point) for point in points]

        except Exception as e:
            logger.error(f"Error during filtered search: {e}")
            if "does not exist" in str(e).lower():
                return []
            raise

    def _build_qdrant_filter(self, filters: Dict):
        """Construir filtro de Qdrant desde diccionario"""
        qdrant_conditions = []

        # Manejar filtros "must"
        if "must" in filters:
            for condition in filters["must"]:
                if "key" in condition and "match" in condition:
                    qdrant_conditions.append(
                        models.FieldCondition(
                            key=condition["key"],
                            match=models.MatchValue(value=condition["match"]["text"]),
                        )
                    )

        # Filtro por documento específico
        if "pdf_name" in filters:
            qdrant_conditions.append(
                models.FieldCondition(
                    key="pdf_name", match=models.MatchValue(value=filters["pdf_name"])
                )
            )

        if qdrant_conditions:
            return models.Filter(must=qdrant_conditions)

        return None

    async def delete_document(self, pdf_name: str):
        """Eliminar todos los chunks de un documento"""
        try:
            if not self.client:
                raise RuntimeError("Vector store not initialized")

            if not self.collection_exists:
                logger.warning(f"Collection {self.collection_name} does not exist. Nothing to delete.")
                return

            # Eliminar por filtro
            filter_condition = models.Filter(
                must=[
                    models.FieldCondition(
                        key="pdf_name", match=models.MatchValue(value=pdf_name)
                    )
                ]
            )

            result = self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(filter=filter_condition),
            )

            logger.info(f"Deleted chunks for document: {pdf_name}")
            return result

        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            raise

    async def get_collection_info(self):
        """Obtener información de la colección"""
        try:
            if not self.client:
                raise RuntimeError("Vector store not initialized")

            if not self.collection_exists:
                return {
                    "collection_exists": False,
                    "vectors_count": 0,
                    "unique_documents": 0,
                    "documents_list": []
                }

            collection_info = self.client.get_collection(self.collection_name)

            # Obtener estadísticas adicionales
            stats = {
                "collection_exists": True,
                "vectors_count": collection_info.vectors_count or 0,
                "indexed_vectors_count": collection_info.indexed_vectors_count or 0,
                "points_count": collection_info.points_count or 0,
                "segments_count": collection_info.segments_count or 0,
                "status": collection_info.status,
                "optimizer_status": collection_info.optimizer_status,
                "vector_size": collection_info.config.params.vectors.size,
                "distance_metric": collection_info.config.params.vectors.distance,
            }

            # Obtener documentos únicos
            unique_docs = await self._get_unique_documents()
            stats["unique_documents"] = len(unique_docs)
            stats["documents_list"] = unique_docs

            return stats

        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {
                "collection_exists": False,
                "error": str(e),
                "vectors_count": 0,
                "unique_documents": 0,
                "documents_list": []
            }

    async def _get_unique_documents(self):
        """Obtener lista de documentos únicos"""
        try:
            if not self.collection_exists:
                return []

            # Usar scroll para obtener todos los pdf_names únicos
            unique_docs = set()
            offset = None

            while True:
                points, offset = self.client.scroll(
                    collection_name=self.collection_name,
                    limit=1000,
                    offset=offset,
                    with_payload=["pdf_name"],
                    with_vectors=False,
                )

                for point in points:
                    if "pdf_name" in point.payload:
                        unique_docs.add(point.payload["pdf_name"])

                if offset is None:
                    break

            return list(unique_docs)

        except Exception as e:
            logger.error(f"Error getting unique documents: {e}")
            return []

    async def get_sample_vectors(self, sample_size: int = 100):
        """Obtener muestra de vectores para análisis"""
        try:
            if not self.client or not self.collection_exists:
                return []

            points, _ = self.client.scroll(
                collection_name=self.collection_name,
                limit=sample_size,
                with_payload=False,
                with_vectors=True,
            )

            return [point.vector for point in points if point.vector]

        except Exception as e:
            logger.error(f"Error getting sample vectors: {e}")
            return []

    async def health_check(self):
        """Verificar salud de la conexión"""
        try:
            if not self.client:
                return False

            collections = self.client.get_collections()
            collection_exists = any(
                col.name == self.collection_name for col in collections.collections
            )

            return collection_exists

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    async def optimize_collection(self):
        """Optimizar la colección para mejor rendimiento"""
        try:
            if not self.client or not self.collection_exists:
                logger.warning("Cannot optimize: collection does not exist")
                return

            # Forzar optimización de índices
            self.client.update_collection(
                collection_name=self.collection_name,
                optimizer_config=models.OptimizersConfigDiff(indexing_threshold=10000),
            )

            logger.info(f"Collection {self.collection_name} optimization requested")

        except Exception as e:
            logger.error(f"Error optimizing collection: {e}")
            raise

    async def backup_collection(self, backup_path: str):
        """Crear snapshot de la colección"""
        try:
            if not self.client or not self.collection_exists:
                raise RuntimeError("Cannot backup: collection does not exist")

            # Crear snapshot
            snapshot_info = self.client.create_snapshot(
                collection_name=self.collection_name
            )

            logger.info(f"Snapshot created: {snapshot_info}")
            return snapshot_info

        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            raise

    async def close(self):
        """Cerrar conexión"""
        try:
            if self.client:
                # Qdrant client no tiene método close explícito
                self.client = None
                self.is_initialized = False
                self.collection_exists = False
                logger.info("Vector store connection closed")
        except Exception as e:
            logger.error(f"Error closing vector store: {e}")

    def __del__(self):
        """Destructor"""
        if self.is_initialized:
            asyncio.create_task(self.close())