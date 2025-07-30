# Backend - AskYourManual

Sistema de búsqueda semántica para manuales Komatsu desarrollado con FastAPI y Qdrant.

## 🚀 Tecnologías Principales

- **FastAPI 0.104.1** - Framework web moderno y rápido
- **Qdrant** - Base de datos vectorial para búsqueda semántica
- **Sentence Transformers** - Modelos de embeddings multilingües
- **PyPDF2** - Procesamiento de documentos PDF
- **Pydantic** - Validación de datos y configuración
- **Python 3.11+** - Lenguaje de programación

## 📁 Estructura del Proyecto

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Aplicación principal FastAPI
│   ├── config.py              # Configuración del sistema
│   ├── api/
│   │   └── routes/
│   │       ├── search.py      # Endpoints de búsqueda
│   │       ├── documents.py   # Gestión de documentos
│   │       └── metrics.py     # Métricas y estadísticas
│   ├── core/
│   │   └── vector_store.py    # Cliente Qdrant
│   ├── models/
│   │   └── schemas.py         # Modelos de datos Pydantic
│   └── services/
│       ├── pdf_service.py     # Procesamiento de PDFs
│       ├── embedding_service.py # Generación de embeddings
│       ├── search_service.py  # Lógica de búsqueda
│       └── metrics_service.py # Cálculo de métricas
├── data/
│   ├── pdfs/                  # PDFs originales
│   └── processed/             # Archivos procesados
├── requirements.txt
├── docker-compose.yml
└── .env
```

## ⚙️ Configuración e Instalación

### 1. Requisitos Previos
- Python 3.11+
- Docker Desktop (para Qdrant)

### 2. Instalación del Entorno

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configurar Base de Datos Vectorial

```bash
# Iniciar Qdrant con Docker
docker-compose up -d qdrant

# Verificar que esté funcionando
curl http://localhost:6333/health
```

### 4. Configuración de Variables de Entorno (.env.example --> .env)

Crea un archivo `.env` con:

```env

# Configuración general
DEBUG=true
PORT=8000

# CORS - Sin espacios y comillas
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=komatsu_manuals

# PDF Processing
PDF_STORAGE_PATH=./data/pdfs
PROCESSED_STORAGE_PATH=./data/processed
MAX_FILE_SIZE=52428800

# Embeddings
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
EMBEDDING_BATCH_SIZE=32

# Chunking
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MIN_CHUNK_SIZE=100

# Search
DEFAULT_SEARCH_LIMIT=10
MAX_SEARCH_LIMIT=100

# Cache
CACHE_TTL=3600
MAX_CACHE_SIZE=1000

# Logging
LOG_LEVEL=INFO
```

### 5. Ejecutar la Aplicación

```bash
# Iniciar servidor de desarrollo
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# O usar Python directamente
python -m app.main
```


## 📊 Métricas del Sistema

### Métricas de Latencia
- **Media**: Tiempo promedio de respuesta
- **Mediana**: Tiempo del 50% de las consultas
- **P90/P95/P99**: Percentiles de latencia (90%, 95%, 99%)

### Métricas de Precisión y Recall
- **Precision@K**: Porcentaje de resultados relevantes en los primeros K
- **Recall@K**: Porcentaje de documentos relevantes encontrados en los primeros K

### Métricas de Calidad
- **Coherencia Semántica**: Consistencia de los embeddings generados (0-1)
- **Diversidad**: Variedad temática en los resultados (0-1)
- **Estabilidad**: Consistencia de resultados para consultas similares (0-1)
- **Cobertura**: Porcentaje de documentos indexados exitosamente (0-1)

### Métricas de Uso
- **Total de búsquedas**: Número acumulado de consultas realizadas
- **Consultas únicas**: Número de consultas distintas
- **Resultados promedio**: Número medio de resultados por consulta

## 🛠️ Endpoints de la API

### Búsqueda
- `POST /api/search/` - Búsqueda principal
- `POST /api/search/batch` - Búsqueda por lotes
- `GET /api/search/suggestions` - Sugerencias de consultas
- `GET /api/search/stats` - Estadísticas de búsqueda

### Documentos
- `POST /api/documents/upload` - Subir PDF
- `GET /api/documents/` - Listar documentos
- `DELETE /api/documents/{filename}` - Eliminar documento
- `POST /api/documents/reprocess/{filename}` - Reprocesar documento

### Métricas
- `GET /api/metrics/performance` - Métricas de rendimiento
- `GET /api/metrics/realtime` - Métricas en tiempo real
- `POST /api/metrics/export` - Exportar métricas
- `GET /api/metrics/alerts` - Verificar alertas

### Sistema
- `GET /health` - Estado del sistema
- `GET /docs` - Documentación Swagger

## 🔧 Procesamiento de PDFs

### Pipeline de Procesamiento
1. **Extracción**: PyPDF2 extrae texto página por página
2. **Chunking**: División en fragmentos con solapamiento configurable
3. **Embedding**: Generación de vectores con modelo multilingüe
4. **Indexación**: Almacenamiento en Qdrant con metadatos

### Configuración de Chunking
- **CHUNK_SIZE=1000**: Tamaño óptimo para párrafos técnicos
- **CHUNK_OVERLAP=200**: 20% de solapamiento para mantener contexto
- **MIN_CHUNK_SIZE=100**: Evita fragmentos muy pequeños sin valor semántico

### Consideraciones de Seguridad
- Validación de tipos de archivo (solo PDF)
- Límites de tamaño de archivo (50MB por defecto)
- CORS configurado para orígenes específicos

## 📈 Optimización de Rendimiento

### Configuración de Embeddings
- Procesamiento en lotes (EMBEDDING_BATCH_SIZE=32)
- Modelo multilingüe optimizado para español e inglés
- Cache de embeddings para consultas frecuentes

### Optimización de Qdrant
- Índices automáticos en campos clave (pdf_name, chunk_id)
- Configuración de distancia coseno para mejor rendimiento
- Optimización automática de la colección
