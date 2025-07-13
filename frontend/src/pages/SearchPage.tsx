import { useState } from "react";
import { SearchBar } from "@/components/search/SearchBar";
import { SearchResults } from "@/components/search/SearchResults";
import { SearchFilters } from "@/components/search/SearchFilters";
import { useSearch, useDocuments } from "@/hooks";
import { Card } from "@/components/ui/Card";
import type { SearchStrategy, SearchResponse } from "@/types";

export function SearchPage() {
  const [searchResponse, setSearchResponse] = useState<SearchResponse | null>(
    null
  );
  const [showFilters, setShowFilters] = useState(false);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [currentFilters, setCurrentFilters] = useState<any>({});

  const searchMutation = useSearch();
  const { data: documentsData } = useDocuments();

  const handleSearch = async (query: string, strategy: SearchStrategy) => {
    try {
      const response = await searchMutation.mutateAsync({
        query,
        strategy,
        limit: currentFilters.limit || 10,
        filters: currentFilters.filters || {},
        include_metadata: currentFilters.include_metadata || false,
      });
      setSearchResponse(response);
    } catch (error) {
      console.error("Error en búsqueda:", error);
    }
  };

  const documentNames =
    documentsData?.documents.map((doc) => doc.filename) || [];

  return (
    <div className="space-y-6 ">
      {/* Barra de búsqueda */}
      <Card>
        <SearchBar onSearch={handleSearch} loading={searchMutation.isPending} />
      </Card>
      {/* Filtros */}
      <SearchFilters
        isOpen={showFilters}
        onToggle={() => setShowFilters(!showFilters)}
        onFiltersChange={setCurrentFilters}
        documents={documentNames}
      />
      {/* Resultados */}
      <SearchResults
        searchResponse={searchResponse}
        loading={searchMutation.isPending}
      />
    </div>
  );
}
