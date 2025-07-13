import { Search, FileText, BarChart3, Settings, Wrench } from "lucide-react";
import { useSystemHealth } from "@/hooks";
import { Badge } from "@/components/ui/Badge";

interface HeaderProps {
  currentView: string;
  onViewChange: (view: string) => void;
}

export function Header({ currentView, onViewChange }: HeaderProps) {
  const { data: health } = useSystemHealth();

  const navigation = [
    { id: "search", label: "Búsqueda", icon: Search },
    { id: "documents", label: "Documentos", icon: FileText },
    { id: "metrics", label: "Métricas", icon: BarChart3 },
    { id: "settings", label: "Configuración", icon: Settings },
  ];

  return (
    <header className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo y título */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Wrench className="h-8 w-8 text-komatsu-yellow" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  Komatsu Manual Search
                </h1>
                <p className="text-sm text-gray-600">
                  Sistema de búsqueda semántica
                </p>
              </div>
            </div>
          </div>

          {/* Navegación */}
          <nav className="flex space-x-1">
            {navigation.map((item) => {
              const Icon = item.icon;
              const isActive = currentView === item.id;

              return (
                <button
                  key={item.id}
                  onClick={() => onViewChange(item.id)}
                  className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-primary-100 text-primary-700"
                      : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                  }`}
                >
                  <Icon className="h-4 w-4 mr-2" />
                  {item.label}
                </button>
              );
            })}
          </nav>

          {/* Estado del sistema */}
          <div className="flex items-center space-x-3">
            <Badge variant={health?.status === "healthy" ? "success" : "error"}>
              {health?.status === "healthy" ? "Sistema OK" : "Sistema Error"}
            </Badge>
          </div>
        </div>
      </div>
    </header>
  );
}
