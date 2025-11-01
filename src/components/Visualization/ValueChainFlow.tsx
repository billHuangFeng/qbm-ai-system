"use client";

import React from 'react';
import { Card } from "@/components/ui/card";

export interface ChainNode {
  id: string;
  name: string;
  metricName: string;
  metricValue: number; // 0-1 或百分比数
  target: number;      // 目标阈值（0-1）
}

export interface ValueChainFlowProps {
  nodes: ChainNode[];
}

export function ValueChainFlow({ nodes }: ValueChainFlowProps) {
  return (
    <div className="w-full overflow-x-auto">
      <div className="flex items-center gap-10">
        {nodes.map((n, idx) => {
          const isBottleneck = n.metricValue < n.target;
          const pct = Math.round(n.metricValue * 100);
          return (
            <div key={n.id} className="relative">
              <Card className={`p-4 w-48 text-center border-2 ${isBottleneck ? 'border-red-500 animate-pulse' : 'border-green-500'}`}>
                <div className="font-semibold">{n.name}</div>
                <div className="text-2xl mt-2">{pct}%</div>
                <div className="text-xs text-gray-500 mt-1">{n.metricName}</div>
              </Card>
              {idx < nodes.length - 1 && (
                <div className="absolute right-[-36px] top-1/2 -translate-y-1/2 text-gray-600">→</div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export function mockChainFlow() {
  const nodes: ChainNode[] = [
    { id: 'prod', name: '生产', metricName: '生产效率', metricValue: 0.85, target: 0.90 },
    { id: 'feature', name: '产品特性', metricName: '价值特性系数', metricValue: 0.92, target: 0.90 },
    { id: 'value', name: '产品价值', metricName: '传播效率', metricValue: 0.78, target: 0.85 },
    { id: 'cx', name: '客户体验', metricName: '交付效率', metricValue: 0.88, target: 0.90 },
    { id: 'sales', name: '销售', metricName: '转化率', metricValue: 0.65, target: 0.70 }
  ];
  return { nodes };
}




