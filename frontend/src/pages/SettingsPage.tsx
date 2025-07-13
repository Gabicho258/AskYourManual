import { useState } from "react";
import { Settings, Server, Database, Zap, Download } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Badge } from "@/components/ui/Badge";
import { useClearCache, useSystemHealth, useSystemInfo } from "@/hooks";
import { metricsApi } from "@/services/api";
import { toast } from "react-hot-toast";

export function SettingsPage() {
  const [exportConfig, setExportConfig] = useState({
    format: "json" as "json" | "csv",
    includeRawData: false,
    startDate: "",
    endDate: "",
  });

  const { data: health } = useSystemHealth();
  const { data: systemInfo } = useSystemInfo();
  const clearCacheMutation = useClearCache();

  const handleExportMetrics = async () => {
    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const config: any = {
        format: exportConfig.format,
        include_raw_data: exportConfig.includeRawData,
      };

      if (exportConfig.startDate) {
        config.start_date = exportConfig.startDate;
      }
      if (exportConfig.endDate) {
        config.end_date = exportConfig.endDate;
      }

      const data = await metricsApi.export(config);

      // Crear y descargar archivo
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: exportConfig.format === "json" ? "application/json" : "text/csv",
      });

      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `metrics-export-${new Date().toISOString().split("T")[0]}.${
        exportConfig.format
      }`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      toast.success("Métricas exportadas correctamente");
    } catch {
      toast.error("Error exportando métricas");
    }
  };

  const handleClearMetrics = async () => {
    try {
      await metricsApi.clear();
      toast.success("Métricas limpiadas correctamente");
    } catch {
      toast.error("Error limpiando métricas");
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Configuración</h1>
        <p className="text-gray-600">
          Configuración del sistema y herramientas de administración
        </p>
      </div>

      {/* Estado del sistema */}
      <Card>
        <div className="flex items-center space-x-2 mb-4">
          <Server className="h-5 w-5 text-blue-600" />
          <h2 className="text-lg font-semibold text-gray-900">
            Estado del Sistema
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Estado de la API:</span>
              <Badge
                variant={health?.status === "healthy" ? "success" : "error"}
              >
                {health?.status || "Desconocido"}
              </Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Versión:</span>
              <span className="font-medium">1.0.0</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Modo debug:</span>
              <Badge variant={systemInfo?.debug ? "warning" : "success"}>
                {systemInfo?.debug ? "Activado" : "Desactivado"}
              </Badge>
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Base de datos:</span>
              <Badge variant="success">Conectada</Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Cache:</span>
              <Badge variant="success">Activo</Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Orígenes CORS:</span>
              <span className="text-sm text-gray-500">
                {health?.cors_origins?.length || 0} configurados
              </span>
            </div>
          </div>
        </div>
      </Card>

      {/* Gestión de caché */}
      <Card>
        <div className="flex items-center space-x-2 mb-4">
          <Database className="h-5 w-5 text-green-600" />
          <h2 className="text-lg font-semibold text-gray-900">
            Gestión de Caché
          </h2>
        </div>

        <div className="space-y-4">
          <p className="text-gray-600">
            Limpiar el caché puede mejorar el rendimiento pero eliminará las
            consultas almacenadas.
          </p>

          <div className="flex space-x-3">
            <Button
              onClick={() => clearCacheMutation.mutate()}
              loading={clearCacheMutation.isPending}
              variant="outline"
            >
              Limpiar caché de búsqueda
            </Button>
          </div>
        </div>
      </Card>

      {/* Exportación de métricas */}
      <Card>
        <div className="flex items-center space-x-2 mb-4">
          <Download className="h-5 w-5 text-purple-600" />
          <h2 className="text-lg font-semibold text-gray-900">
            Exportar Métricas
          </h2>
        </div>

        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              type="date"
              label="Fecha de inicio"
              value={exportConfig.startDate}
              onChange={(e) =>
                setExportConfig({
                  ...exportConfig,
                  startDate: e.target.value,
                })
              }
            />

            <Input
              type="date"
              label="Fecha de fin"
              value={exportConfig.endDate}
              onChange={(e) =>
                setExportConfig({
                  ...exportConfig,
                  endDate: e.target.value,
                })
              }
            />
          </div>

          <div className="flex items-center space-x-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Formato de exportación
              </label>
              <div className="flex space-x-4">
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="json"
                    checked={exportConfig.format === "json"}
                    onChange={(e) =>
                      setExportConfig({
                        ...exportConfig,
                        format: e.target.value as "json" | "csv",
                      })
                    }
                    className="mr-2"
                  />
                  JSON
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="csv"
                    checked={exportConfig.format === "csv"}
                    onChange={(e) =>
                      setExportConfig({
                        ...exportConfig,
                        format: e.target.value as "json" | "csv",
                      })
                    }
                    className="mr-2"
                  />
                  CSV
                </label>
              </div>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="includeRawData"
                checked={exportConfig.includeRawData}
                onChange={(e) =>
                  setExportConfig({
                    ...exportConfig,
                    includeRawData: e.target.checked,
                  })
                }
                className="mr-2"
              />
              <label htmlFor="includeRawData" className="text-sm text-gray-700">
                Incluir datos sin procesar
              </label>
            </div>
          </div>

          <Button onClick={handleExportMetrics}>
            <Download className="h-4 w-4 mr-2" />
            Exportar métricas
          </Button>
        </div>
      </Card>

      {/* Gestión de datos */}
      <Card>
        <div className="flex items-center space-x-2 mb-4">
          <Zap className="h-5 w-5 text-red-600" />
          <h2 className="text-lg font-semibold text-gray-900">
            Gestión de Datos
          </h2>
        </div>

        <div className="space-y-4">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p className="text-yellow-800 text-sm">
              <strong>Atención:</strong> Estas acciones son irreversibles y
              pueden afectar el funcionamiento del sistema.
            </p>
          </div>

          <div className="flex space-x-3">
            <Button variant="danger" onClick={handleClearMetrics}>
              Limpiar todas las métricas
            </Button>
          </div>
        </div>
      </Card>

      {/* Información del sistema */}
      <Card>
        <div className="flex items-center space-x-2 mb-4">
          <Settings className="h-5 w-5 text-gray-600" />
          <h2 className="text-lg font-semibold text-gray-900">
            Información del Sistema
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-medium text-gray-900 mb-2">Backend</h3>
            <div className="space-y-1 text-sm">
              <p>
                <strong>Framework:</strong> FastAPI
              </p>
              <p>
                <strong>Base de datos:</strong> Qdrant
              </p>
              <p>
                <strong>Modelo de embeddings:</strong> Multilingual MiniLM
              </p>
              <p>
                <strong>Estrategias:</strong> Semántica, Híbrida, Keyword
              </p>
            </div>
          </div>

          <div>
            <h3 className="font-medium text-gray-900 mb-2">Frontend</h3>
            <div className="space-y-1 text-sm">
              <p>
                <strong>Framework:</strong> React + TypeScript
              </p>
              <p>
                <strong>Build tool:</strong> Vite
              </p>
              <p>
                <strong>Estilos:</strong> Tailwind CSS
              </p>
              <p>
                <strong>Estado:</strong> React Query
              </p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
