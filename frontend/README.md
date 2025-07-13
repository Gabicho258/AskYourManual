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

# Vista previa del build
npm run preview
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
- **Filtros avanzados** por documento y metadatos
- **Resultados con scoring** de relevancia visual
- **Historial persistente** en localStorage

### 📄 Página de Documentos
- **Drag & Drop** para subir PDFs
- **Vista en tiempo real** del estado de procesamiento
- **Gestión completa** de documentos:
  - Subir con título y descripción
  - Eliminar documentos indexed
  - Reprocesar documentos con errores
- **Información detallada**: tamaño, chunks, tiempo de procesamiento
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

## 🛠️ Componentes UI Reutilizables

### Componentes Base
- **Button**: Variantes (primary, secondary, outline, danger) con loading states
- **Input**: Con iconos, validación y estados de error
- **Card**: Contenedor estándar con padding y sombras
- **Badge**: Indicadores de estado con variantes de color
- **Modal**: Diálogos modales responsive
- **LoadingSpinner**: Indicadores de carga en diferentes tamaños

### Características Avanzadas
- **Responsive Design**: Mobile-first con breakpoints adaptativos
- **Loading States**: Skeleton UI y spinners en todas las operaciones
- **Error Handling**: Toast notifications y error boundaries
- **TypeScript**: Tipado completo para mejor DX y menos bugs
- **Accessibility**: Estructura semántica y navegación por teclado

## 🔄 Gestión de Estado

### React Query Configuration
```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30000,        // 30 segundos
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 1,
    },
  },
});
```

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

## 🎨 Sistema de Diseño

### Paleta de Colores
```css
/* Colores primarios */
primary: {
  50: '#eff6ff',
  500: '#3b82f6',
  600: '#2563eb',
  700: '#1d4ed8',
}

/* Colores Komatsu */
komatsu: {
  yellow: '#FFD700',
  orange: '#FF6B35', 
  gray: '#2C3E50',
}
```

### Tipografía
- **Fuente principal**: Inter (Google Fonts)
- **Tamaños**: Sistema escalable (sm, md, lg, xl)
- **Pesos**: 400 (normal), 500 (medium), 600 (semibold), 700 (bold)

### Espaciado y Layout
- **Grid responsive**: 1-4 columnas según pantalla
- **Espaciado consistente**: Múltiplos de 4px
- **Componentes flexibles**: Adaptación automática al contenido

## 📱 Responsive Design

### Breakpoints
- **sm**: 640px - Móviles grandes
- **md**: 768px - Tablets
- **lg**: 1024px - Laptops
- **xl**: 1280px - Desktops

### Adaptaciones Móviles
- **Sidebar colapsable** en pantallas pequeñas
- **Grid adaptativo** de documentos y métricas
- **Touch-friendly** buttons y controles
- **Navegación optimizada** para móviles

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
- **Patrones temporales**: Búsquedas por hora del día
- **Uso del sistema**: Consultas frecuentes y tendencias

## 🚀 Optimización de Performance

### Bundle Optimization
- **Code splitting**: Lazy loading de páginas
- **Tree shaking**: Eliminación de código no usado
- **Asset optimization**: Compresión de imágenes y recursos
- **Caching strategy**: Headers HTTP apropiados

### Runtime Performance
- **React Query**: Cache inteligente de API calls
- **Debounced search**: Evita requests excesivos
- **Virtual scrolling**: Para listas grandes de documentos
- **Memoization**: Componentes optimizados con React.memo

## 🔧 Desarrollo y Testing

### Scripts Disponibles
```bash
# Desarrollo con hot reload
npm run dev

# Build optimizado para producción
npm run build

# Linting con ESLint
npm run lint

# Preview del build de producción
npm run preview
```

### Configuración de TypeScript
- **Strict mode**: Tipado estricto habilitado
- **Path mapping**: Imports absolutos con @/
- **Type checking**: Validación en build time
- **IntelliSense**: Autocompletado completo en IDEs

## 📈 Monitoreo de Performance

### Métricas del Frontend
- **Core Web Vitals**: LCP, FID, CLS
- **Bundle size**: Tamaño optimizado de assets
- **Load time**: Tiempo de carga inicial
- **API response time**: Latencia de requests

### Tools de Análisis
- **Vite bundle analyzer**: Análisis del tamaño del bundle
- **React DevTools**: Profiling de componentes
- **Network tab**: Monitoreo de requests
- **Lighthouse**: Auditorías de performance y accessibility