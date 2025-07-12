# app/services/embedding_service.py
import asyncio
import logging
from typing import List, Optional
from sentence_transformers import SentenceTransformer
import torch
import numpy as np

from app.config import settings, EMBEDDING_MODELS

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.batch_size = settings.EMBEDDING_BATCH_SIZE

    async def initialize(self):
        """Inicializar el modelo de embeddings"""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            
            # Cargar modelo en un hilo separado para no bloquear
            self.model = await asyncio.get_event_loop().run_in_executor(
                None, self._load_model
            )
            
            logger.info(f"Embedding model loaded successfully on {self.device}")
            
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise

    def _load_model(self):
        """Cargar modelo de sentence transformers"""
        model = SentenceTransformer(self.model_name)
        model = model.to(self.device)
        return model

    async def embed_query(self, query: str) -> List[float]:
        """Generar embedding para una consulta"""
        if not self.model:
            await self.initialize()
            
        try:
            # Ejecutar embedding en hilo separado
            embedding = await asyncio.get_event_loop().run_in_executor(
                None, self._encode_single, query
            )
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            raise

    def _encode_single(self, text: str) -> np.ndarray:
        """Codificar un texto individual"""
        return self.model.encode(text, convert_to_tensor=False, normalize_embeddings=True)

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generar embeddings para múltiples textos"""
        if not self.model:
            await self.initialize()
            
        try:
            # Procesar en lotes para mejor rendimiento
            all_embeddings = []
            
            for i in range(0, len(texts), self.batch_size):
                batch = texts[i:i + self.batch_size]
                
                # Ejecutar embedding en hilo separado
                batch_embeddings = await asyncio.get_event_loop().run_in_executor(
                    None, self._encode_batch, batch
                )
                
                all_embeddings.extend(batch_embeddings)
                
                # Pequeña pausa entre lotes
                if i + self.batch_size < len(texts):
                    await asyncio.sleep(0.01)

            logger.info(f"Generated embeddings for {len(texts)} texts")
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Error generating text embeddings: {e}")
            raise

    def _encode_batch(self, texts: List[str]) -> List[List[float]]:
        """Codificar un lote de textos"""
        embeddings = self.model.encode(
            texts, 
            convert_to_tensor=False, 
            normalize_embeddings=True,
            batch_size=self.batch_size
        )
        return embeddings.tolist()

    def get_embedding_dimension(self) -> int:
        """Obtener dimensión de los embeddings"""
        if not self.model:
            return 384  # Dimensión por defecto para MiniLM
        return self.model.get_sentence_embedding_dimension()

    async def change_model(self, new_model_name: str):
        """Cambiar modelo de embedding"""
        try:
            old_model = self.model_name
            self.model_name = new_model_name
            self.model = None
            
            await self.initialize()
            
            logger.info(f"Embedding model changed from {old_model} to {new_model_name}")
            
        except Exception as e:
            logger.error(f"Error changing embedding model: {e}")
            raise

    def get_available_models(self) -> dict:
        """Obtener modelos disponibles"""
        return EMBEDDING_MODELS