// src/App.tsx
import { useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "react-hot-toast";
import { Layout } from "@/components/layout/Layout";
import { SearchPage } from "@/pages/SearchPage";
import { DocumentsPage } from "@/pages/DocumentsPage";
import { MetricsPage } from "@/pages/MetricsPage";
import { SettingsPage } from "@/pages/SettingsPage";

// Crear cliente de React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30000, // 30 segundos
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 1,
    },
  },
});

function App() {
  const [currentView, setCurrentView] = useState("search");

  const renderCurrentView = () => {
    switch (currentView) {
      case "search":
        return <SearchPage />;
      case "documents":
        return <DocumentsPage />;
      case "metrics":
        return <MetricsPage />;
      case "settings":
        return <SettingsPage />;
      default:
        return <SearchPage />;
    }
  };

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gray-50">
        <Layout
          currentView={currentView}
          onViewChange={setCurrentView}
          showSidebar={true}
        >
          {renderCurrentView()}
        </Layout>

        {/* Notificaciones toast */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: "#363636",
              color: "#fff",
            },
            success: {
              duration: 3000,
              style: {
                background: "#10B981",
              },
            },
            error: {
              duration: 5000,
              style: {
                background: "#EF4444",
              },
            },
          }}
        />
      </div>
    </QueryClientProvider>
  );
}

export default App;
