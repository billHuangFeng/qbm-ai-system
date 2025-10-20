"use client";

import React from 'react';
import { Card } from "@/components/ui/card";

export interface SankeyNode { id: string; name: string; }
export interface SankeyLink { source: string; target: string; value: number; }

export interface ValueChainSankeyProps { nodes: SankeyNode[]; links: SankeyLink[]; }

// Simple horizontal staged layout: columns represent stages along the value chain
const columns = [
  '投入资源','生产','产品特性','产品价值','客户体验','销售','销售收入','成本开支'
];

export function ValueChainSankey({ nodes, links }: ValueChainSankeyProps) {
  // group nodes by column name if it matches; otherwise put in first/last
  const byName = new Map(nodes.map(n => [n.name, n]));
  const colX: Record<string, number> = {} as any;
  const width = 980;
  const height = 420;
  const left = 80, right = 40;
  const colW = (width - left - right) / (columns.length - 1);
  columns.forEach((c, i) => colX[c] = left + i * colW);

  const nodePos = new Map<string, { x: number; y: number }>();
  columns.forEach((c, cIdx) => {
    const colNodes = nodes.filter(n => n.name === c);
    colNodes.forEach((n, idx) => {
      nodePos.set(n.id, { x: colX[c], y: 60 + idx * 80 });
    });
  });

  const nodeMap = new Map(nodes.map(n => [n.id, n]));
  const valueMax = Math.max(1, ...links.map(l => l.value));

  return (
    <Card className="p-4">
      <div className="text-sm text-gray-500 mb-2">价值链桑基图（占位简版）</div>
      <svg width={width} height={height} className="w-full h-auto">
        {/* columns titles */}
        {columns.map((c, i) => (
          <text key={c} x={left + i * colW} y={24} textAnchor="middle" fontSize={12} fill="#6b7280">{c}</text>
        ))}

        {/* links */}
        {links.map((l, idx) => {
          const sPos = nodePos.get(l.source);
          const tPos = nodePos.get(l.target);
          if (!sPos || !tPos) return null;
          const thickness = Math.max(2, (l.value / valueMax) * 16);
          const midX = (sPos.x + tPos.x) / 2;
          const path = `M ${sPos.x} ${sPos.y} C ${midX} ${sPos.y}, ${midX} ${tPos.y}, ${tPos.x} ${tPos.y}`;
          const isLoss = l.value < valueMax * 0.5;
          const color = isLoss ? '#f87171' : '#60a5fa';
          return (
            <path key={idx} d={path} stroke={color} strokeOpacity={0.6} strokeWidth={thickness} fill="none" />
          );
        })}

        {/* nodes */}
        {nodes.map(n => {
          const p = nodePos.get(n.id);
          if (!p) return null;
          return (
            <g key={n.id}>
              <rect x={p.x - 40} y={p.y - 14} width={80} height={28} rx={6} ry={6} fill="#111827" opacity={0.9} />
              <text x={p.x} y={p.y + 4} textAnchor="middle" fontSize={12} fill="#ffffff">{n.name}</text>
            </g>
          );
        })}
      </svg>
    </Card>
  );
}

export function mockSankeyData() {
  const nodes: SankeyNode[] = columns.map((c, i) => ({ id: `n${i}`, name: c }));
  const id = (name: string) => nodes.find(n => n.name === name)!.id;
  const links: SankeyLink[] = [
    { source: id('投入资源'), target: id('生产'), value: 100 },
    { source: id('生产'), target: id('产品特性'), value: 85 },
    { source: id('产品特性'), target: id('产品价值'), value: 82 },
    { source: id('产品价值'), target: id('客户体验'), value: 78 },
    { source: id('客户体验'), target: id('销售'), value: 68 },
    { source: id('销售'), target: id('销售收入'), value: 66 },
    { source: id('投入资源'), target: id('成本开支'), value: 100 }
  ];
  return { nodes, links };
}
