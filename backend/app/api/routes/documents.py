# app/api/routes/documents.py
import logging
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse

from app.services.pdf_service import PDFService
from app.services.metrics_service import MetricsService
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Variables globales que se configurarán en main.py
pdf_service: Optional[PDFService] = None
metrics_service: Optional[MetricsService] = None


@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
):
    """Subir y procesar un archivo PDF"""
    if not pdf_service:
        raise HTTPException(status_code=500, detail="PDF service not initialized")
    
    # Validar archivo
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    if file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    
    try:
        # Guardar archivo
        pdf_dir = Path(settings.PDF_STORAGE_PATH)
        pdf_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = pdf_dir / file.filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Procesar PDF
        result = await pdf_service.process_pdf(str(file_path), file.filename)
        
        # Agregar metadatos adicionales
        result.update({
            "title": title,
            "description": description,
            "file_size": file.size
        })
        
        logger.info(f"PDF uploaded and processed: {file.filename}")
        return result
        
    except Exception as e:
        logger.error(f"Error uploading PDF: {e}")
        # Limpiar archivo si hay error
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")


@router.get("/")
async def list_documents():
    """Listar documentos procesados"""
    if not pdf_service:
        raise HTTPException(status_code=500, detail="PDF service not initialized")
    
    try:
        processed_files = pdf_service.get_processed_files()
        
        # Obtener información adicional de archivos
        pdf_dir = Path(settings.PDF_STORAGE_PATH)
        documents = []
        
        for filename in processed_files:
            file_path = pdf_dir / filename
            if file_path.exists():
                stat = file_path.stat()
                documents.append({
                    "filename": filename,
                    "file_size": stat.st_size,
                    "created_at": stat.st_ctime,
                    "status": "completed"
                })
        
        return {"documents": documents, "total": len(documents)}
        
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=f"List error: {str(e)}")


@router.delete("/{filename}")
async def delete_document(filename: str):
    """Eliminar documento"""
    if not pdf_service:
        raise HTTPException(status_code=500, detail="PDF service not initialized")
    
    try:
        # Eliminar del índice
        success = await pdf_service.delete_document(filename)
        
        if success:
            # Eliminar archivo físico
            file_path = Path(settings.PDF_STORAGE_PATH) / filename
            if file_path.exists():
                file_path.unlink()
                
            return {"message": f"Document {filename} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
            
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=f"Delete error: {str(e)}")


@router.post("/reprocess/{filename}")
async def reprocess_document(filename: str):
    """Reprocesar un documento existente"""
    if not pdf_service:
        raise HTTPException(status_code=500, detail="PDF service not initialized")
    
    try:
        file_path = Path(settings.PDF_STORAGE_PATH) / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Eliminar del índice primero
        await pdf_service.delete_document(filename)
        
        # Reprocesar
        result = await pdf_service.process_pdf(str(file_path), filename)
        
        return result
        
    except Exception as e:
        logger.error(f"Error reprocessing document: {e}")
        raise HTTPException(status_code=500, detail=f"Reprocess error: {str(e)}")
