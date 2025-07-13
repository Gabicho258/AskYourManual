# AskYourManual

Sistema inteligente de búsqueda semántica para manuales técnicos Komatsu. Permite realizar consultas en lenguaje natural sobre documentación técnica utilizando tecnologías de inteligencia artificial y procesamiento de lenguaje natural.

## 🎯 Descripción del Proyecto

AskYourManual es una solución completa que combina un potente backend de procesamiento de documentos con una interfaz web moderna, diseñada específicamente para facilitar la búsqueda de información en manuales técnicos de maquinaria Komatsu.

### Características Principales
- **Búsqueda Semántica Inteligente**: Comprende el contexto y significado de las consultas
- **Procesamiento Automático de PDFs**: Indexación automática de documentos técnicos
- **Múltiples Estrategias de Búsqueda**: Semántica, híbrida y por palabras clave
- **Dashboard de Métricas**: Monitoreo completo del rendimiento del sistema
- **Interfaz Responsive**: Acceso desde cualquier dispositivo

## 🏗️ Arquitectura del Sistema

```
AskYourManual/
├── backend/                 # API FastAPI + Qdrant
│   ├── app/
│   │   ├── api/routes/     # Endpoints REST
│   │   ├── services/       # Lógica de negocio
│   │   ├── core/          # Vector store y configuración
│   │   └── models/        # Esquemas de datos
│   ├── data/              # Almacenamiento de PDFs
│   └── requirements.txt
├── frontend/               # Aplicación React + TypeScript
│   ├── src/
│   │   ├── components/    # Componentes UI
│   │   ├── pages/         # Páginas principales
│   │   ├── services/      # Clientes API
│   │   └── hooks/         # Lógica reutilizable
│   └── package.json
└── README.md
```

## 🚀 Instalación y Configuración

### Requisitos del Sistema
- **Python 3.11+** (Backend)
- **Node.js 18+** (Frontend)
- **Docker Desktop** (Base de datos vectorial)
- **4GB RAM** mínimo recomendado
- **2GB espacio en disco** para modelos y datos

### Configuración Rápida

#### 1. Configurar Backend
```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate    # Windows

# Instalar dependencias
pip install -r requirements.txt

# Iniciar Qdrant
docker-compose up -d qdrant

# Ejecutar servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Configurar Frontend
```bash
cd frontend

# Instalar dependencias
npm install

# Iniciar aplicación
npm run dev
```

#### 3. Verificar Instalación
- **Backend**: `http://localhost:8000/health`
- **Frontend**: `http://localhost:3000`
- **API Docs**: `http://localhost:8000/docs`

## 🔍 Cómo Usar el Sistema

### 1. Subir Documentos
1. Accede a la sección **"Documentos"**
2. Arrastra un archivo PDF o haz clic para seleccionarlo
3. Agrega título y descripción (opcional)
4. El sistema procesará automáticamente el documento

### 2. Realizar Búsquedas
1. Ve a la sección **"Búsqueda"**
2. Escribe tu consulta en lenguaje natural:
   - "¿Cómo cambiar el aceite del motor?"
   - "Procedimientos de seguridad para mantenimiento"
   - "Especificaciones técnicas del bulldozer D65"
3. Selecciona la estrategia de búsqueda apropiada
4. Revisa los resultados ordenados por relevancia

### 3. Monitorear Performance
1. Accede a la sección **"Métricas"**
2. Revisa dashboard con:
   - Latencia de búsquedas
   - Precisión y recall
   - Patrones de uso
   - Estado del sistema

## 📊 Estrategias de Búsqueda

### 🧠 Semántica
**Cuándo usar**: Consultas conceptuales o cuando no conoces términos exactos
- ✅ "Procedimientos de arranque en frío"
- ✅ "Problemas de sobrecalentamiento"
- ✅ "Mantenimiento preventivo trimestral"

**Cómo funciona**: Utiliza embeddings para entender el significado y contexto de la consulta, encontrando información relacionada conceptualmente.

### ⚖️ Híbrida (Recomendada)
**Cuándo usar**: Para la mayoría de consultas generales
- ✅ "Cambio de filtros hidráulicos D375A"
- ✅ "Torque de pernos motor 6D125"
- ✅ "Calibración sistema GPS"

**Cómo funciona**: Combina búsqueda semántica (70%) y por palabras clave (30%) para obtener el mejor balance entre precisión y cobertura.

### 🔤 Palabras Clave
**Cuándo usar**: Búsquedas exactas de códigos, números de parte, o términos específicos
- ✅ "PC200-8M0"
- ✅ "6D125E-3"
- ✅ "Error code P0001"

**Cómo funciona**: Búsqueda literal de términos específicos en el texto, ideal para referencias exactas.

## 📈 Métricas y Monitoreo

### Métricas de Performance
- **Latencia Media**: Tiempo promedio de respuesta del sistema
- **P90/P95/P99**: Percentiles de latencia para identificar outliers
- **Throughput**: Número de consultas procesadas por minuto

### Métricas de Calidad
- **Precision@K**: % de resultados relevantes en los primeros K resultados
- **Recall@K**: % de documentos relevantes encontrados en los primeros K
- **NDCG@K**: Calidad del ranking de resultados (0-1, mayor es mejor)
- **MRR**: Posición promedio del primer resultado relevante

### Métricas de Sistema
- **Coherencia Semántica**: Consistencia de los embeddings (0-1)
- **Diversidad**: Variedad temática en resultados (0-1)
- **Estabilidad**: Consistencia para consultas similares (0-1)
- **Cobertura**: % de documentos indexados exitosamente

## 🛠️ Stack Tecnológico

### Backend
- **FastAPI**: Framework web moderno y rápido
- **Qdrant**: Base de datos vectorial especializada
- **Sentence Transformers**: Modelos de embeddings multilingües
- **PyPDF2**: Procesamiento de documentos PDF
- **Pydantic**: Validación de datos y configuración

### Frontend
- **React 19**: Biblioteca de interfaz de usuario
- **TypeScript**: Tipado estático para JavaScript
- **Tailwind CSS**: Framework de estilos utilitario
- **React Query**: Gestión de estado del servidor
- **Recharts**: Visualizaciones interactivas

### Base de Datos y ML
- **Qdrant**: Vector database con índices HNSW
- **Modelo de Embeddings**: `paraphrase-multilingual-MiniLM-L12-v2`
- **Dimensionalidad**: 384 dimensiones por vector
- **Distancia**: Coseno para similaridad semántica

## 🔧 Configuración Avanzada

### Variables de Entorno Importantes

#### Backend (.env)
```env
# Procesamiento
CHUNK_SIZE=1000              # Tamaño de fragmentos de texto
CHUNK_OVERLAP=200            # Solapamiento entre fragmentos
EMBEDDING_BATCH_SIZE=32      # Tamaño de lote para embeddings

# Base de datos
QDRANT_COLLECTION=komatsu_manuals
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Límites
MAX_FILE_SIZE=52428800       # 50MB máximo por PDF
DEFAULT_SEARCH_LIMIT=10      # Resultados por defecto
MAX_SEARCH_LIMIT=100         # Máximo resultados permitidos
```

#### Frontend (vite.config.ts)
```typescript
server: {
  proxy: {
    '^/(api|health|docs)': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

## 🔍 Casos de Uso Típicos

### Para Técnicos de Mantenimiento
- "¿Cada cuántas horas debo cambiar el filtro de aceite?"
- "Procedimiento para calibrar el sistema hidráulico"
- "Códigos de error del motor 6D125"

### Para Operadores
- "Controles de seguridad antes de arrancar"
- "¿Cómo ajustar la velocidad de trabajo?"
- "Procedimiento de parada de emergencia"

### Para Supervisores
- "Especificaciones técnicas para licitación"
- "Intervalos de mantenimiento preventivo"
- "Capacidades de carga según modelo"

## 🚦 Monitoreo del Sistema

### Health Checks Automáticos
```bash
# Verificar estado general
curl http://localhost:8000/health

# Estado de la base de datos vectorial
curl http://localhost:6333/health

# Métricas en tiempo real
curl http://localhost:8000/api/metrics/realtime
```

### Indicadores Clave (KPIs)
- **Disponibilidad del Sistema**: >99.5%
- **Latencia P95**: <2 segundos
- **Precisión@5**: >80%
- **Tasa de Éxito de Indexación**: >95%

## 🔒 Consideraciones de Seguridad

### Validaciones Implementadas
- **Tipos de archivo**: Solo PDFs permitidos
- **Tamaño máximo**: 50MB por archivo
- **Sanitización**: Nombres de archivo y metadatos
- **CORS**: Orígenes configurados específicamente

### Buenas Prácticas
- Variables sensibles en archivos `.env`
- Validación de entrada en todos los endpoints
- Límites de rate limiting (configurable)
- Logs de auditoría para uploads y búsquedas

## 📚 Documentación Adicional

### APIs y Referencias
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Qdrant Dashboard**: `http://localhost:6333/dashboard`

### Guías Específicas
- [Configuración del Backend](./backend/README.md)
- [Configuración del Frontend](./frontend/README.md)
- Documentación de la API REST completa en Swagger

## 🤝 Contribución y Desarrollo

### Estructura de Commits
```
feat: nueva funcionalidad
fix: corrección de bug
docs: actualización de documentación
style: cambios de formato
refactor: refactorización de código
test: adición de tests
```

### Flujo de Desarrollo
1. Fork del repositorio
2. Crear rama para feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit de cambios: `git commit -m 'feat: agregar nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## 🔧 Troubleshooting

### Problemas Comunes

#### Backend no inicia
```bash
# Verificar Python y dependencias
python --version
pip list | grep fastapi

# Verificar Qdrant
docker ps | grep qdrant
curl http://localhost:6333/health
```

#### Frontend no carga estilos
```bash
# Limpiar cache y reinstalar
rm -rf node_modules package-lock.json
npm install
npm run dev
```

#### Búsquedas sin resultados
1. Verificar que hay documentos indexados: `GET /api/documents/`
2. Revisar estado de la colección Qdrant
3. Probar con diferentes estrategias de búsqueda
4. Verificar logs del backend para errores

#### Performance lenta
- Reducir `EMBEDDING_BATCH_SIZE` si hay problemas de memoria
- Aumentar `CACHE_TTL` para consultas frecuentes
- Verificar que Qdrant tenga índices creados
- Monitorear métricas de latencia

## 📞 Soporte

### Logs y Debugging
```bash
# Backend logs
tail -f app.log

# Frontend console
# Abrir DevTools > Console

# Qdrant logs
docker logs <qdrant_container_id>
```

### Información del Sistema
- **Versión**: 1.0.0
- **Licencia**: MIT
- **Soporte**: Consultar documentación técnica y issues en GitHub

---

**AskYourManual** - Haciendo la información técnica más accesible a través de la inteligencia artificial.