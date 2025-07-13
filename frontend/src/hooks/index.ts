import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import { searchApi, documentsApi, metricsApi, systemApi } from "@/services/api";
import type { SearchRequest } from "@/types";

// Hook para búsqueda
export function useSearch() {
  return useMutation({
    mutationFn: (request: SearchRequest) => searchApi.search(request),
    onError: (error: Error) => {
      toast.error(`Error en búsqueda: ${error.message}`);
    },
  });
}

// Hook para sugerencias
export function useSuggestions(query: string, enabled = true) {
  return useQuery({
    queryKey: ["suggestions", query],
    queryFn: () => searchApi.getSuggestions(query),
    enabled: enabled && query.length > 0,
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
}

// Hook para estadísticas de búsqueda
export function useSearchStats() {
  return useQuery({
    queryKey: ["search-stats"],
    queryFn: searchApi.getStats,
    refetchInterval: 30000, // Actualizar cada 30 segundos
  });
}

// Hook para documentos
export function useDocuments() {
  return useQuery({
    queryKey: ["documents"],
    queryFn: documentsApi.list,
    refetchInterval: 10000, // Actualizar cada 10 segundos
  });
}

// Hook para subir documento
export function useUploadDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      file,
      title,
      description,
    }: {
      file: File;
      title?: string;
      description?: string;
    }) => documentsApi.upload(file, title, description),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
      if (data.status === "completed") {
        toast.success(`Documento ${data.filename} procesado correctamente`);
      } else if (data.status === "failed") {
        toast.error(`Error procesando ${data.filename}: ${data.error}`);
      } else {
        toast.success(`Documento ${data.filename} subido, procesando...`);
      }
    },
    onError: (error: Error) => {
      toast.error(`Error subiendo documento: ${error.message}`);
    },
  });
}

// Hook para eliminar documento
export function useDeleteDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (filename: string) => documentsApi.delete(filename),
    onSuccess: (_, filename) => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
      toast.success(`Documento ${filename} eliminado`);
    },
    onError: (error: Error) => {
      toast.error(`Error eliminando documento: ${error.message}`);
    },
  });
}

// Hook para reprocesar documento
export function useReprocessDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (filename: string) => documentsApi.reprocess(filename),
    onSuccess: (_, filename) => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
      toast.success(`Reprocesando documento ${filename}`);
    },
    onError: (error: Error) => {
      toast.error(`Error reprocesando documento: ${error.message}`);
    },
  });
}

// Hook para métricas de rendimiento
export function usePerformanceMetrics() {
  return useQuery({
    queryKey: ["performance-metrics"],
    queryFn: metricsApi.getPerformance,
    refetchInterval: 60000, // Actualizar cada minuto
  });
}

// Hook para métricas en tiempo real
export function useRealtimeMetrics() {
  return useQuery({
    queryKey: ["realtime-metrics"],
    queryFn: metricsApi.getRealtime,
    refetchInterval: 10000, // Actualizar cada 10 segundos
  });
}

// Hook para alertas
export function useAlerts() {
  return useQuery({
    queryKey: ["alerts"],
    queryFn: metricsApi.getAlerts,
    refetchInterval: 30000, // Actualizar cada 30 segundos
  });
}

// Hook para health check
export function useSystemHealth() {
  return useQuery({
    queryKey: ["system-health"],
    queryFn: systemApi.health,
    refetchInterval: 30000, // Actualizar cada 30 segundos
    retry: 3,
  });
}

// Hook para info del sistema
export function useSystemInfo() {
  return useQuery({
    queryKey: ["system-info"],
    queryFn: systemApi.info,
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
}

// Hook para limpiar caché
export function useClearCache() {
  return useMutation({
    mutationFn: searchApi.clearCache,
    onSuccess: () => {
      toast.success("Caché limpiado correctamente");
    },
    onError: (error: Error) => {
      toast.error(`Error limpiando caché: ${error.message}`);
    },
  });
}

// Hook personalizado para búsqueda con historial
export function useSearchHistory() {
  const getHistory = (): string[] => {
    try {
      return JSON.parse(localStorage.getItem("search-history") || "[]");
    } catch {
      return [];
    }
  };

  const addToHistory = (query: string) => {
    try {
      const history = getHistory();
      const newHistory = [query, ...history.filter((q) => q !== query)].slice(
        0,
        10
      );
      localStorage.setItem("search-history", JSON.stringify(newHistory));
    } catch (error) {
      console.warn("No se pudo guardar en el historial:", error);
    }
  };

  const clearHistory = () => {
    try {
      localStorage.removeItem("search-history");
    } catch (error) {
      console.warn("No se pudo limpiar el historial:", error);
    }
  };

  return { getHistory, addToHistory, clearHistory };
}
