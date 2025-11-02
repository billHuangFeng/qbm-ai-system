import React from 'react';
import { ValueNetworkGraph, mockValueNetworkData } from "@/components/Visualization/ValueNetworkGraph";

export default function Dashboard() {
  const network = mockValueNetworkData();

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <header className="mb-6">
        <h1 className="text-3xl font-bold">BMOS 商业模式优化仪表盘</h1>
      </header>

      <section className="w-full">
        <ValueNetworkGraph nodes={network.nodes} links={network.links} />
      </section>
    </div>
  );
}
