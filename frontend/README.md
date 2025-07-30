# Frontend - AskYourManual

Interfaz web moderna para el sistema de búsqueda semántica de manuales Komatsu desarrollada con React y TypeScript.

## 🚀 Tecnologías Principales

- **React 19** - Biblioteca de interfaz de usuario
- **TypeScript 5.8** - Tipado estático para JavaScript
- **Vite 7.0** - Herramienta de build ultrarrápida
- **Tailwind CSS 4.1** - Framework de CSS utilitario
- **React Query 5.8** - Gestión de estado del servidor y cache
- **Axios** - Cliente HTTP para APIs
- **Recharts** - Gráficos y visualizaciones interactivas

## 📁 Estructura del Proyecto

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/                # Componentes base reutilizables
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Badge.tsx
│   │   │   ├── Modal.tsx
│   │   │   └── LoadingSpinner.tsx
│   │   ├── search/            # Componentes de búsqueda
│   │   │   ├── SearchBar.tsx
│   │   │   ├── SearchResults.tsx
│   │   │   └── SearchFilters.tsx
│   │   └── layout/            # Componentes de layout
│   │       ├── Header.tsx
│   │       ├── Sidebar.tsx
│   │       └── Layout.tsx
│   ├── pages/                 # Páginas principales
│   │   ├── SearchPage.tsx     # Búsqueda semántica
│   │   ├── DocumentsPage.tsx  # Gestión de documentos
│   │   ├── MetricsPage.tsx    # Dashboard de métricas
│   │   └── SettingsPage.tsx   # Configuración del sistema
│   ├── services/              # Servicios y APIs
│   │   └── api.ts
│   ├── hooks/                 # Custom hooks
│   │   └── index.ts
│   ├── types/                 # Definiciones TypeScript
│   │   └── index.ts
│   ├── App.tsx               # Componente principal
│   ├── main.tsx              # Punto de entrada
│   └── index.css             # Estilos globales
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

## ⚙️ Configuración e Instalación

### 1. Requisitos Previos
- Node.js 18+ 
- npm o yarn
- Backend corriendo en `http://localhost:8000`

### 2. Instalación

```bash
# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev

# Construir para producción
npm run build

```

### 3. Verificación

La aplicación estará disponible en:
- **Desarrollo**: `http://localhost:3000`
- **Documentación del backend**: `http://localhost:8000/docs`

## 🎯 Funcionalidades Principales

### 🔍 Página de Búsqueda
- **Barra de búsqueda inteligente** con autocompletado
- **Sugerencias dinámicas** basadas en historial
- **Tres estrategias de búsqueda**:
  - Semántica: Para consultas conceptuales
  - Híbrida: Balance entre precisión y recall
  - Keyword: Búsqueda exacta de términos
- **Filtros avanzados** por documento 
- **Resultados con scoring** de relevancia visual
- **Historial persistente** en localStorage

### 📄 Página de Documentos
- **Drag & Drop** para subir PDFs
- **Vista en tiempo real** del estado de procesamiento
- **Gestión completa** de documentos:
  - Eliminar documentos indexed
  - Reprocesar documentos con errores
- **Estados visuales**: pending, processing, completed, failed

### 📊 Página de Métricas
- **Dashboard completo** con visualizaciones interactivas
- **Métricas de latencia**: distribución de tiempos de respuesta
- **Gráficos de precisión/recall** por valor K
- **Patrones de uso**: búsquedas por hora del día
- **Métricas de calidad semántica** del sistema
- **Alertas en tiempo real** para problemas del sistema
- **Estadísticas de uso**: consultas frecuentes, usuarios únicos

### ⚙️ Página de Configuración
- **Monitoreo del sistema**: estado de servicios y conexiones
- **Gestión de caché**: limpieza y optimización
- **Exportación de métricas**: JSON y CSV con filtros de fecha
- **Información del sistema**: versiones y configuración
- **Herramientas de administración**: limpieza de datos


## 🔄 Gestión de Estado


### Custom Hooks Principales
- **useSearch**: Búsqueda semántica con cache
- **useDocuments**: Gestión de documentos PDF
- **usePerformanceMetrics**: Métricas del sistema
- **useSystemHealth**: Estado de servicios
- **useSearchHistory**: Historial local de búsquedas

### Cache Strategy
- **Queries con TTL**: 30 segundos para datos dinámicos
- **Invalidación automática**: Actualización tras mutaciones
- **Cache persistente**: Historial de búsquedas en localStorage
- **Optimistic updates**: UI responsive durante operaciones

## 🔌 Integración con Backend

### Configuración de Proxy
```typescript
// vite.config.ts
server: {
  port: 3000,
  proxy: {
    '^/(api|health|docs|redoc)': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

### Servicios API
- **searchApi**: Búsqueda semántica y sugerencias
- **documentsApi**: Upload, gestión y procesamiento de PDFs
- **metricsApi**: Estadísticas y exportación de datos
- **systemApi**: Health checks y información del sistema

### Error Handling
- **Interceptores de Axios**: Manejo centralizado de errores
- **Toast notifications**: Feedback inmediato al usuario
- **Retry automático**: Reintentos en fallos de red
- **Fallbacks**: Estados de error informativos

## 📊 Visualizaciones de Datos

### Recharts Components
- **BarChart**: Distribución de latencias y patrones de uso
- **LineChart**: Precisión/Recall por K
- **PieChart**: Distribución de estrategias de búsqueda
- **ResponsiveContainer**: Gráficos adaptativos al contenido

### Métricas Visualizadas
- **Latencia por percentiles**: P50, P90, P95, P99
- **Calidad semántica**: Coherencia, diversidad, estabilidad
- **Patrones temporales**: Cantidad de búsquedas por hora 
- **Uso del sistema**: Consultas frecuentes y tendencias
