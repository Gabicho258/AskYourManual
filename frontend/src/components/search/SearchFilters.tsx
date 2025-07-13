import React from "react";
import { Filter, X } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Card } from "@/components/ui/Card";

interface SearchFiltersProps {
  isOpen: boolean;
  onToggle: () => void;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  onFiltersChange: (filters: any) => void;
  documents: string[];
}

export function SearchFilters({
  isOpen,
  onToggle,
  onFiltersChange,
  documents,
}: SearchFiltersProps) {
  const [selectedDocument, setSelectedDocument] = React.useState("");
  const [limit, setLimit] = React.useState(10);
  const [includeMetadata, setIncludeMetadata] = React.useState(false);

  const handleApplyFilters = () => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const filters: any = {};

    if (selectedDocument) {
      filters.pdf_name = selectedDocument;
    }

    onFiltersChange({
      filters,
      limit,
      include_metadata: includeMetadata,
    });
  };

  const handleClearFilters = () => {
    setSelectedDocument("");
    setLimit(10);
    setIncludeMetadata(false);
    onFiltersChange({
      filters: {},
      limit: 10,
      include_metadata: false,
    });
  };

  if (!isOpen) {
    return (
      <Button
        variant="outline"
        onClick={onToggle}
        className="flex items-center"
      >
        <Filter className="h-4 w-4 mr-2" />
        Filtros
      </Button>
    );
  }

  return (
    <Card className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-medium flex items-center">
          <Filter className="h-4 w-4 mr-2" />
          Filtros de búsqueda
        </h3>
        <Button variant="outline" size="sm" onClick={onToggle}>
          <X className="h-4 w-4" />
        </Button>
      </div>

      <div className="space-y-4">
        {/* Documento específico */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Documento específico
          </label>
          <select
            value={selectedDocument}
            onChange={(e) => setSelectedDocument(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">Todos los documentos</option>
            {documents.map((doc) => (
              <option key={doc} value={doc}>
                {doc}
              </option>
            ))}
          </select>
        </div>

        {/* Límite de resultados */}
        <div>
          <Input
            type="number"
            label="Límite de resultados"
            value={limit}
            onChange={(e) => setLimit(parseInt(e.target.value) || 10)}
            min={1}
            max={100}
          />
        </div>

        {/* Incluir metadata */}
        <div className="flex items-center">
          <input
            type="checkbox"
            id="metadata"
            checked={includeMetadata}
            onChange={(e) => setIncludeMetadata(e.target.checked)}
            className="mr-2"
          />
          <label htmlFor="metadata" className="text-sm text-gray-700">
            Incluir metadatos
          </label>
        </div>

        <div className="flex space-x-2">
          <Button onClick={handleApplyFilters} size="sm">
            Aplicar filtros
          </Button>
          <Button variant="outline" onClick={handleClearFilters} size="sm">
            Limpiar
          </Button>
        </div>
      </div>
    </Card>
  );
}
