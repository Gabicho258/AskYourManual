import { FileText, Clock, Target } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import type { SearchResponse } from "@/types";

interface SearchResultsProps {
  searchResponse: SearchResponse | null;
  loading?: boolean;
}

export function SearchResults({ searchResponse, loading }: SearchResultsProps) {
  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-1/2 mb-4"></div>
            <div className="space-y-2">
              <div className="h-3 bg-gray-200 rounded"></div>
              <div className="h-3 bg-gray-200 rounded w-5/6"></div>
            </div>
          </Card>
        ))}
      </div>
    );
  }

  if (!searchResponse) {
    return (
      <div className="text-center py-12">
        <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          Busca en los manuales Komatsu
        </h3>
        <p className="text-gray-600">
          Introduce tu consulta para encontrar información específica en los
          documentos.
        </p>
      </div>
    );
  }

  if (searchResponse.total_results === 0) {
    return (
      <div className="text-center py-12">
        <Target className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          No se encontraron resultados
        </h3>
        <p className="text-gray-600">
          Intenta con otros términos o usa una estrategia de búsqueda diferente.
        </p>
      </div>
    );
  }

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return "success";
    if (score >= 0.6) return "warning";
    return "error";
  };

  return (
    <div className="space-y-6">
      {/* Información de la búsqueda */}
      <div className="flex items-center justify-between text-sm text-gray-600">
        <div className="flex items-center space-x-4">
          <span>
            <strong>{searchResponse.total_results}</strong> resultados
          </span>
          <span className="flex items-center">
            <Clock className="h-4 w-4 mr-1" />
            {(searchResponse.search_time * 1000).toFixed(0)}ms
          </span>
          <Badge variant="info">{searchResponse.strategy_used}</Badge>
        </div>
      </div>

      {/* Resultados */}
      <div className="space-y-4">
        {searchResponse.results.map((result, index) => (
          <Card
            key={result.chunk_id}
            className="hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center space-x-2">
                <FileText className="h-5 w-5 text-blue-600" />
                <h3 className="font-medium text-gray-900 truncate">
                  {result.pdf_name}
                </h3>
              </div>
              <Badge variant={getScoreColor(result.score)} size="sm">
                {(result.score * 100).toFixed(0)}%
              </Badge>
            </div>

            <p className="text-gray-700 leading-relaxed mb-3">
              {result.text.length > 400
                ? `${result.text.substring(0, 400)}...`
                : result.text}
            </p>

            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>Resultado #{index + 1}</span>
              <span>ID: {result.chunk_id.substring(0, 8)}...</span>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
