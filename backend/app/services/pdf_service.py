# app/services/pdf_service.py
import os
import asyncio
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import PyPDF2
from datetime import datetime
import hashlib

from app.services.embedding_service import EmbeddingService
from app.core.vector_store import VectorStore
from app.config import settings

logger = logging.getLogger(__name__)


class PDFService:
    def __init__(self, embedding_service: EmbeddingService, vector_store: VectorStore):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.processed_files = set()

    async def process_pdf(self, file_path: str, filename: str) -> Dict[str, Any]:
        """Procesar un archivo PDF"""
        start_time = datetime.now()
        
        try:
            logger.info(f"Processing PDF: {filename}")
            
            # Verificar si ya fue procesado
            if filename in self.processed_files:
                logger.info(f"PDF {filename} already processed")
                return {"status": "already_processed", "filename": filename}

            # Extraer texto del PDF
            text_chunks = await self._extract_text_from_pdf(file_path)
            
            if not text_chunks:
                raise ValueError("No text extracted from PDF")

            # Generar embeddings
            embeddings = await self.embedding_service.embed_texts(text_chunks)
            
            # Indexar en vector store
            indexed_count = await self.vector_store.index_chunks(
                vectors=embeddings,
                chunks=text_chunks,
                pdf_name=filename
            )

            # Marcar como procesado
            self.processed_files.add(filename)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "status": "completed",
                "filename": filename,
                "chunk_count": indexed_count,
                "processing_time": processing_time,
                "indexed_at": datetime.now().isoformat()
            }
            
            logger.info(f"PDF processed successfully: {filename} - {indexed_count} chunks in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Error processing PDF {filename}: {e}")
            return {
                "status": "failed", 
                "filename": filename,
                "error": str(e),
                "processing_time": (datetime.now() - start_time).total_seconds()
            }

    async def _extract_text_from_pdf(self, file_path: str) -> List[str]:
        """Extraer texto del PDF y dividir en chunks"""
        try:
            text_chunks = []
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extraer texto de todas las páginas
                full_text = ""
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    full_text += text + "\n"

            # Dividir en chunks
            chunks = self._chunk_text(full_text)
            
            # Filtrar chunks muy pequeños
            filtered_chunks = [
                chunk for chunk in chunks 
                if len(chunk.strip()) >= settings.MIN_CHUNK_SIZE
            ]
            
            return filtered_chunks
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise

    def _chunk_text(self, text: str) -> List[str]:
        """Dividir texto en chunks con overlap"""
        chunks = []
        chunk_size = settings.CHUNK_SIZE
        overlap = settings.CHUNK_OVERLAP
        
        # Limpiar texto
        text = text.replace('\n\n', '\n').replace('\t', ' ')
        sentences = text.split('. ')
        
        current_chunk = ""
        current_size = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            sentence_size = len(sentence)
            
            # Si agregar esta oración excede el tamaño del chunk
            if current_size + sentence_size > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                
                # Crear overlap tomando las últimas palabras
                words = current_chunk.split()
                overlap_words = words[-overlap//10:] if len(words) > overlap//10 else words
                current_chunk = ' '.join(overlap_words) + '. ' + sentence
                current_size = len(current_chunk)
            else:
                if current_chunk:
                    current_chunk += '. ' + sentence
                else:
                    current_chunk = sentence
                current_size += sentence_size
        
        # Agregar el último chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks

    async def process_existing_pdfs(self):
        """Procesar PDFs existentes en el directorio"""
        try:
            pdf_dir = Path(settings.PDF_STORAGE_PATH)
            if not pdf_dir.exists():
                pdf_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created PDF directory: {pdf_dir}")
                return

            pdf_files = list(pdf_dir.glob("*.pdf"))
            
            if not pdf_files:
                logger.info("No PDF files found to process")
                return

            logger.info(f"Found {len(pdf_files)} PDF files to process")
            
            for pdf_file in pdf_files:
                try:
                    await self.process_pdf(str(pdf_file), pdf_file.name)
                    # Pequeña pausa entre archivos
                    await asyncio.sleep(0.1)
                except Exception as e:
                    logger.error(f"Error processing {pdf_file.name}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error processing existing PDFs: {e}")

    async def delete_document(self, filename: str) -> bool:
        """Eliminar documento del índice"""
        try:
            await self.vector_store.delete_document(filename)
            self.processed_files.discard(filename)
            logger.info(f"Document deleted: {filename}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document {filename}: {e}")
            return False

    def get_processed_files(self) -> List[str]:
        """Obtener lista de archivos procesados"""
        return list(self.processed_files)

