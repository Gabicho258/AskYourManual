import axios, { AxiosError } from "axios";
import type {
  SearchRequest,
  SearchResponse,
  Document,
  SearchSuggestionsResponse,
  PerformanceMetrics,
  UploadResponse,
  ApiError,
} from "@/types";

const api = axios.create({
  baseURL: "/api",
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor para manejar errores
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    const errorMessage =
      error.response?.data?.detail || error.message || "Error desconocido";
    console.error("API Error:", errorMessage);
    throw new Error(errorMessage);
  }
);

export const searchApi = {
  // Búsqueda principal
  search: async (request: SearchRequest): Promise<SearchResponse> => {
    const { data } = await api.post<SearchResponse>("/search/", request);
    return data;
  },

  // Búsqueda por lotes
  batchSearch: async (
    queries: string[],
    limit = 10,
    strategy: SearchRequest["strategy"] = "semantic"
  ) => {
    const { data } = await api.post("/search/batch", {
      queries,
      limit,
      strategy,
    });
    return data;
  },

  // Obtener sugerencias
  getSuggestions: async (
    query: string,
    limit = 5
  ): Promise<SearchSuggestionsResponse> => {
    const { data } = await api.get<SearchSuggestionsResponse>(
      "/search/suggestions",
      {
        params: { query, limit },
      }
    );
    return data;
  },

  // Estadísticas de búsqueda
  getStats: async () => {
    const { data } = await api.get("/search/stats");
    return data;
  },

  // Limpiar caché
  clearCache: async () => {
    const { data } = await api.delete("/search/cache");
    return data;
  },
};

export const documentsApi = {
  // Subir documento
  upload: async (
    file: File,
    title?: string,
    description?: string
  ): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append("file", file);
    if (title) formData.append("title", title);
    if (description) formData.append("description", description);

    const { data } = await api.post<UploadResponse>(
      "/documents/upload",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
        timeout: 120000, // 2 minutos para uploads
      }
    );
    return data;
  },

  // Listar documentos
  list: async (): Promise<{ documents: Document[]; total: number }> => {
    const { data } = await api.get("/documents/");
    return data;
  },

  // Eliminar documento
  delete: async (filename: string) => {
    const { data } = await api.delete(`/documents/${filename}`);
    return data;
  },

  // Reprocesar documento
  reprocess: async (filename: string) => {
    const { data } = await api.post(`/documents/reprocess/${filename}`);
    return data;
  },
};

export const metricsApi = {
  // Métricas de rendimiento
  getPerformance: async (): Promise<PerformanceMetrics> => {
    const { data } = await api.get<PerformanceMetrics>("/metrics/performance");
    return data;
  },

  // Métricas en tiempo real
  getRealtime: async () => {
    const { data } = await api.get("/metrics/realtime");
    return data;
  },

  // Exportar métricas
  export: async (config: {
    start_date?: string;
    end_date?: string;
    metric_types?: string[];
    format?: "json" | "csv";
    include_raw_data?: boolean;
  }) => {
    const { data } = await api.post("/metrics/export", config);
    return data;
  },

  // Verificar alertas
  getAlerts: async () => {
    const { data } = await api.get("/metrics/alerts");
    return data;
  },

  // Limpiar métricas
  clear: async () => {
    const { data } = await api.delete("/metrics/");
    return data;
  },
};

export const systemApi = {
  // Health check
  health: async () => {
    const { data } = await api.get("/health", { baseURL: "" });
    console.log(data);
    return data;
  },

  // Info del sistema
  info: async () => {
    const { data } = await api.get("/", { baseURL: "" });
    return data;
  },
};

export default api;
