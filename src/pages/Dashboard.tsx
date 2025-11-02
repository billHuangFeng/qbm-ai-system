import React from 'react';
import { ValueNetworkGraph, mockValueNetworkData } from "@/components/Visualization/ValueNetworkGraph";

export default function Dashboard() {
  const network = mockValueNetworkData();

  return (
    <div className="min-h-screen max-h-screen bg-gray-50 p-4 flex flex-col overflow-hidden">
      <header className="mb-4 flex-shrink-0">
        <h1 className="text-2xl font-bold">BMOS 商业模式优化仪表盘</h1>
      </header>

      <section className="flex-1 flex items-center justify-center overflow-hidden">
        <div className="w-full h-full">
          <ValueNetworkGraph nodes={network.nodes} links={network.links} />
        </div>
      </section>
    </div>
  );
}
