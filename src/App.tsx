import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { lazy, Suspense } from "react";

const Index = lazy(() => import("./pages/Index"));
const TestPage = lazy(() => import("./pages/TestPage"));
const DataImportPage = lazy(() => import("./pages/DataImportPage"));

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Suspense fallback={<div className="flex items-center justify-center min-h-screen">加载中...</div>}>
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/test" element={<TestPage />} />
            <Route path="/data-import" element={<DataImportPage />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
