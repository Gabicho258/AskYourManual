import React from "react";
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";

interface LayoutProps {
  children: React.ReactNode;
  currentView: string;
  onViewChange: (view: string) => void;
  showSidebar?: boolean;
}

export function Layout({
  children,
  currentView,
  onViewChange,
  showSidebar = true,
}: LayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header currentView={currentView} onViewChange={onViewChange} />
      <div className="flex h-[calc(100vh-4rem)]">
        {showSidebar && <Sidebar onViewChange={onViewChange} />}
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-7xl mx-auto p-6">{children}</div>
        </main>
      </div>
    </div>
  );
}
