import React, { useEffect, useState } from 'react';
import { Card } from "@/components/ui/card";
import { ValueNetworkGraph, mockValueNetwork } from "@/components/Visualization/ValueNetworkGraph";
import { ValueChainFlow, mockChainFlow } from "@/components/Visualization/ValueChainFlow";
import { ValueChainSankey } from "@/components/Visualization/ValueChainSankey";
import { mockSankeyData } from "@/components/Visualization/ValueChainSankey";
import { fetchSankeyDataFallback } from "@/lib/valueChain";

export default function Dashboard() {
  const network = mockValueNetwork();
  const chain = mockChainFlow();
  const [sankey, setSankey] = useState(mockSankeyData());

  useEffect(() => {
    (async () => {
      const data = await fetchSankeyDataFallback(mockSankeyData());
      setSankey(data);
    })();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 p-6 space-y-8">
      <header className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">BMOS 商业模式优化仪表盘</h1>
      </header>

      <section>
        <h2 className="text-xl font-semibold mb-3">价值分配网络</h2>
        <ValueNetworkGraph nodes={network.nodes} links={network.links} />
      </section>

      <section>
        <h2 className="text-xl font-semibold mb-3">价值创造链路与瓶颈</h2>
        <Card className="p-4">
          <ValueChainFlow nodes={chain.nodes} />
        </Card>
      </section>

      <section>
        <h2 className="text-xl font-semibold mb-3">价值链桑基图</h2>
        <ValueChainSankey nodes={sankey.nodes} links={sankey.links} />
      </section>
    </div>
  );
}
