import React, { useState, useEffect } from "react";
import { Search, Clock, Loader2 } from "lucide-react";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { useSuggestions } from "@/hooks";
import { useSearchHistory } from "@/hooks";
import type { SearchStrategy } from "@/types";

interface SearchBarProps {
  onSearch: (query: string, strategy: SearchStrategy) => void;
  loading?: boolean;
  placeholder?: string;
}

export function SearchBar({
  onSearch,
  loading = false,
  placeholder = "Buscar en manuales Komatsu...",
}: SearchBarProps) {
  const [query, setQuery] = useState("");
  const [strategy, setStrategy] = useState<SearchStrategy>("semantic");
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [showHistory, setShowHistory] = useState(false);

  const { data: suggestions } = useSuggestions(query, query.length > 2);
  const { getHistory, addToHistory } = useSearchHistory();
  const history = getHistory();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      addToHistory(query.trim());
      onSearch(query.trim(), strategy);
      setShowSuggestions(false);
      setShowHistory(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
    addToHistory(suggestion);
    onSearch(suggestion, strategy);
    setShowSuggestions(false);
  };

  const handleHistoryClick = (historyItem: string) => {
    setQuery(historyItem);
    onSearch(historyItem, strategy);
    setShowHistory(false);
  };

  useEffect(() => {
    setShowSuggestions(
      (suggestions?.suggestions?.length ?? 0) > 0 && query.length > 2
    );
  }, [suggestions, query]);

  return (
    <div className="relative">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="relative">
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => setShowHistory(history.length > 0 && !query)}
            placeholder={placeholder}
            leftIcon={<Search className="h-5 w-5 text-gray-400" />}
            rightIcon={
              loading ? (
                <Loader2 className="h-5 w-5 text-gray-400 animate-spin" />
              ) : (
                <Button
                  type="submit"
                  size="sm"
                  disabled={!query.trim() || loading}
                >
                  Buscar
                </Button>
              )
            }
            className="pr-20"
          />

          {/* Sugerencias */}
          {showSuggestions && (
            <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-md shadow-lg max-h-60 overflow-auto">
              <div className="p-2 text-xs font-medium text-gray-500 border-b">
                Sugerencias
              </div>
              {suggestions?.suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestionClick(suggestion.query)}
                  className="w-full text-left px-3 py-2 hover:bg-gray-50 flex items-center justify-between"
                >
                  <span>{suggestion.query}</span>
                  <span className="text-xs text-gray-400">
                    {suggestion.frequency}
                  </span>
                </button>
              ))}
            </div>
          )}

          {/* Historial */}
          {showHistory && !showSuggestions && (
            <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-md shadow-lg max-h-60 overflow-auto">
              <div className="p-2 text-xs font-medium text-gray-500 border-b flex items-center">
                <Clock className="h-3 w-3 mr-1" />
                Búsquedas recientes
              </div>
              {history.map((item, index) => (
                <button
                  key={index}
                  onClick={() => handleHistoryClick(item)}
                  className="w-full text-left px-3 py-2 hover:bg-gray-50"
                >
                  {item}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Estrategia de búsqueda */}
        <div className="flex items-center space-x-4">
          <span className="text-sm font-medium text-gray-700">Estrategia:</span>
          {(["semantic", "hybrid", "keyword"] as SearchStrategy[]).map((s) => (
            <label key={s} className="flex items-center">
              <input
                type="radio"
                value={s}
                checked={strategy === s}
                onChange={(e) => setStrategy(e.target.value as SearchStrategy)}
                className="mr-2"
              />
              <span className="text-sm text-gray-600 capitalize">{s}</span>
            </label>
          ))}
        </div>
      </form>
    </div>
  );
}
