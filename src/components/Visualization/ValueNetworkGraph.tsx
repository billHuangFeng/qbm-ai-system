"use client";

import React from 'react';
import { Card } from "@/components/ui/card";

export interface NetworkNode {
  id: string;
  type: 'customer' | 'employee' | 'partner' | 'enterprise';
  name: string;
  valueReceived: number;
  valueGiven: number;
}

export interface NetworkLink {
  source: string;
  target: string;
  value: number;
}

export interface ValueNetworkGraphProps {
  nodes: NetworkNode[];
  links: NetworkLink[];
}

export function ValueNetworkGraph(props: ValueNetworkGraphProps) {
  // Placeholder layout: place nodes in four columns by type
  const groups: Record<string, NetworkNode[]> = {
    customer: [], employee: [], partner: [], enterprise: []
  };
  props.nodes.forEach(n => groups[n.type].push(n));

  const colX = {
    customer: 100,
    employee: 350,
    partner: 600,
    enterprise: 850
  } as const;

  const nodePositions = new Map<string, { x: number; y: number }>();
  (Object.keys(groups) as Array<keyof typeof groups>).forEach((key) => {
    const list = groups[key];
    list.forEach((n, idx) => {
      nodePositions.set(n.id, { x: colX[key as keyof typeof colX], y: 80 + idx * 90 });
    });
  });

  const radius = (n: NetworkNode) => Math.max(10, Math.min(28, Math.sqrt((n.valueReceived + n.valueGiven) / 10)));

  return (
    <Card className="p-4">
      <div className="text-sm text-gray-500 mb-2">价值分配网络（占位简版）</div>
      <svg width={980} height={420} className="w-full h-auto">
        {/* Links */}
        {props.links.map((l, idx) => {
          const s = nodePositions.get(l.source);
          const t = nodePositions.get(l.target);
          if (!s || !t) return null;
          const strokeWidth = Math.max(1, Math.min(8, l.value / 20));
          return (
            <g key={idx}>
              <line x1={s.x} y1={s.y} x2={t.x} y2={t.y} stroke="#9ca3af" strokeWidth={strokeWidth} opacity={0.7} />
            </g>
          );
        })}

        {/* Nodes */}
        {props.nodes.map((n) => {
          const p = nodePositions.get(n.id)!;
          const color = n.type === 'customer' ? '#3b82f6' : n.type === 'employee' ? '#10b981' : n.type === 'partner' ? '#f59e0b' : '#8b5cf6';
          return (
            <g key={n.id}>
              <circle cx={p.x} cy={p.y} r={radius(n)} fill={color} opacity={0.9} />
              <text x={p.x} y={p.y - (radius(n) + 8)} textAnchor="middle" fontSize={12} fill="#111827">{n.name}</text>
            </g>
          );
        })}
      </svg>
    </Card>
  );
}

export function mockValueNetwork() {
  const nodes: NetworkNode[] = [
    { id: 'c1', type: 'customer', name: '客户A', valueReceived: 120, valueGiven: 80 },
    { id: 'c2', type: 'customer', name: '客户B', valueReceived: 90, valueGiven: 60 },
    { id: 'e1', type: 'employee', name: '员工', valueReceived: 70, valueGiven: 110 },
    { id: 'p1', type: 'partner', name: '合作伙伴', valueReceived: 60, valueGiven: 130 },
    { id: 'co', type: 'enterprise', name: '企业', valueReceived: 300, valueGiven: 250 }
  ];
  const links: NetworkLink[] = [
    { source: 'co', target: 'c1', value: 120 },
    { source: 'co', target: 'c2', value: 90 },
    { source: 'e1', target: 'co', value: 110 },
    { source: 'p1', target: 'co', value: 130 },
    { source: 'c1', target: 'co', value: 80 },
    { source: 'c2', target: 'co', value: 60 }
  ];
  return { nodes, links };
}




