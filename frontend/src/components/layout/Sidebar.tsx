import { useSearchStats, useSystemInfo } from "@/hooks";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Clock, TrendingUp, Database, Zap } from "lucide-react";

interface Props {
  onViewChange: (view: string) => void;
}
export function Sidebar({ onViewChange }: Props) {
  const { data: stats } = useSearchStats();
  const { data: systemInfo } = useSystemInfo();

  return (
    <aside className="w-64 bg-gray-50 border-r border-gray-200 h-full overflow-y-auto">
      <div className="p-4 space-y-4">
        {/* Estadísticas rápidas */}
        <Card>
          <h3 className="font-medium text-gray-900 mb-3 flex items-center">
            <TrendingUp className="h-4 w-4 mr-2" />
            Estadísticas
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Total búsquedas:</span>
              <span className="font-medium">{stats?.total_searches || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Tiempo promedio:</span>
              <span className="font-medium">
                {stats?.avg_search_time
                  ? `${(stats.avg_search_time * 1000).toFixed(0)}ms`
                  : "N/A"}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Resultados promedio:</span>
              <span className="font-medium">
                {stats?.avg_results_per_query?.toFixed(1) || "N/A"}
              </span>
            </div>
          </div>
        </Card>

        {/* Consultas frecuentes */}
        {stats?.most_common_queries && stats.most_common_queries.length > 0 && (
          <Card>
            <h3 className="font-medium text-gray-900 mb-3 flex items-center">
              <Clock className="h-4 w-4 mr-2" />
              Consultas frecuentes
            </h3>
            <div className="space-y-2">
              {stats.most_common_queries
                .slice(0, 5)
                .map(([query, count]: [string, number], index: number) => (
                  <div
                    key={index}
                    className="flex items-center justify-between text-sm"
                  >
                    <span className="text-gray-700 truncate flex-1 mr-2">
                      {query}
                    </span>
                    <Badge variant="default" size="sm">
                      {count}
                    </Badge>
                  </div>
                ))}
            </div>
          </Card>
        )}

        {/* Info del sistema */}
        <Card>
          <h3 className="font-medium text-gray-900 mb-3 flex items-center">
            <Database className="h-4 w-4 mr-2" />
            Sistema
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Estado:</span>
              <Badge variant="success" size="sm">
                {systemInfo?.status || "Activo"}
              </Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Versión:</span>
              <span className="font-medium text-xs">1.0.0</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Modo:</span>
              <span className="font-medium text-xs">
                {systemInfo?.debug ? "Debug" : "Producción"}
              </span>
            </div>
          </div>
        </Card>

        {/* Accesos rápidos */}
        <Card>
          <h3 className="font-medium text-gray-900 mb-3 flex items-center">
            <Zap className="h-4 w-4 mr-2" />
            Accesos rápidos
          </h3>
          <div className="space-y-2">
            <button className="w-full text-left text-sm text-gray-700  transition-colors">
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                className="hover:text-primary-600 hover:underline"
              >
                Ver documentación API
              </a>
            </button>
            <button
              className="w-full text-left text-sm text-gray-700 transition-colors cursor-pointer "
              onClick={() => onViewChange("settings")}
            >
              <span className="hover:text-primary-600 hover:underline">
                Limpiar caché de búsqueda
              </span>
            </button>
            <button
              className="w-full text-left text-sm text-gray-700 hover:text-primary-600 transition-colors cursor-pointer"
              onClick={() => onViewChange("metrics")}
            >
              <span className="hover:text-primary-600 hover:underline">
                Exportar métricas
              </span>
            </button>
          </div>
        </Card>
      </div>
    </aside>
  );
}
