import { usePerformanceMetrics, useRealtimeMetrics, useAlerts } from "@/hooks";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from "recharts";
import { Clock, Target, Users, AlertTriangle, Activity } from "lucide-react";

export function MetricsPage() {
  const { data: performance, isLoading: loadingPerformance } =
    usePerformanceMetrics();
  const { data: realtime, isLoading: loadingRealtime } = useRealtimeMetrics();
  const { data: alerts } = useAlerts();

  if (loadingPerformance || loadingRealtime) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const latencyData = performance?.latency
    ? [
        { name: "Media", value: performance.latency.mean * 1000 },
        { name: "Mediana", value: performance.latency.median * 1000 },
        { name: "P90", value: performance.latency.p90 * 1000 },
        { name: "P95", value: performance.latency.p95 * 1000 },
        { name: "P99", value: performance.latency.p99 * 1000 },
      ]
    : [];

  const precisionData = performance?.precision_recall
    ? Object.entries(performance.precision_recall.precision_at_k).map(
        ([k, value]) => ({
          k: `@${k}`,
          precision: (value * 100).toFixed(1),
          recall: (
            (performance.precision_recall.recall_at_k[parseInt(k)] || 0) * 100
          ).toFixed(1),
        })
      )
    : [];

  const searchPatternsData = realtime?.last_24_hours
    ? Object.entries(realtime.last_24_hours.search_patterns || {}).map(
        ([hour, count]) => ({
          hour,
          searches: count,
        })
      )
    : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Métricas del Sistema
        </h1>
        <p className="text-gray-600">
          Monitoreo de rendimiento y estadísticas de uso
        </p>
      </div>

      {/* Alertas */}
      {alerts?.alerts && alerts.alerts.length > 0 && (
        <Card>
          <div className="flex items-center space-x-2 mb-4">
            <AlertTriangle className="h-5 w-5 text-red-600" />
            <h2 className="text-lg font-semibold text-gray-900">
              Alertas Activas
            </h2>
          </div>
          <div className="space-y-2">
            {alerts.alerts.map(
              (alert: { message: string; severity: string }, index: number) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 bg-red-50 rounded-lg"
                >
                  <span className="text-red-800">{alert.message}</span>
                  <Badge variant="error">{alert.severity}</Badge>
                </div>
              )
            )}
          </div>
        </Card>
      )}

      {/* Métricas en tiempo real */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <div className="flex items-center space-x-3">
            <Activity className="h-8 w-8 text-blue-600" />
            <div>
              <p className="text-sm text-gray-600">Última hora</p>
              <p className="text-2xl font-bold text-gray-900">
                {realtime?.last_hour?.total_searches || 0}
              </p>
              <p className="text-xs text-gray-500">búsquedas</p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center space-x-3">
            <Clock className="h-8 w-8 text-green-600" />
            <div>
              <p className="text-sm text-gray-600">Latencia promedio</p>
              <p className="text-2xl font-bold text-gray-900">
                {realtime?.last_hour?.avg_latency
                  ? `${(realtime.last_hour.avg_latency * 1000).toFixed(0)}ms`
                  : "N/A"}
              </p>
              <p className="text-xs text-gray-500">última hora</p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center space-x-3">
            <Users className="h-8 w-8 text-purple-600" />
            <div>
              <p className="text-sm text-gray-600">Consultas únicas</p>
              <p className="text-2xl font-bold text-gray-900">
                {realtime?.last_24_hours?.unique_queries || 0}
              </p>
              <p className="text-xs text-gray-500">últimas 24h</p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center space-x-3">
            <Target className="h-8 w-8 text-orange-600" />
            <div>
              <p className="text-sm text-gray-600">Resultados promedio</p>
              <p className="text-2xl font-bold text-gray-900">
                {realtime?.last_hour?.avg_results?.toFixed(1) || "N/A"}
              </p>
              <p className="text-xs text-gray-500">por búsqueda</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Latencia */}
        <Card>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Distribución de Latencia
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={latencyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip formatter={(value) => [`${value}ms`, "Latencia"]} />
                <Bar dataKey="value" fill="#3B82F6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Precisión y Recall */}
        <Card>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Precisión y Recall por K
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={precisionData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="k" />
                <YAxis />
                <Tooltip formatter={(value) => [`${value}%`]} />
                <Line
                  type="monotone"
                  dataKey="precision"
                  stroke="#10B981"
                  name="Precisión"
                />
                <Line
                  type="monotone"
                  dataKey="recall"
                  stroke="#F59E0B"
                  name="Recall"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Patrones de búsqueda */}
      {searchPatternsData.length > 0 && (
        <Card>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Patrones de Búsqueda (24h)
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={searchPatternsData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" />
                <YAxis />
                <Tooltip formatter={(value) => [`${value}`, "Búsquedas"]} />
                <Bar dataKey="searches" fill="#8B5CF6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      )}

      {/* Métricas de calidad */}
      {performance?.quality && (
        <Card>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Métricas de Calidad
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">
                {(performance.quality.semantic_coherence * 100).toFixed(0)}%
              </p>
              <p className="text-sm text-gray-600">Coherencia Semántica</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">
                {(performance.quality.diversity * 100).toFixed(0)}%
              </p>
              <p className="text-sm text-gray-600">Diversidad</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">
                {(performance.quality.stability * 100).toFixed(0)}%
              </p>
              <p className="text-sm text-gray-600">Estabilidad</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-orange-600">
                {(performance.quality.coverage * 100).toFixed(0)}%
              </p>
              <p className="text-sm text-gray-600">Cobertura</p>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
