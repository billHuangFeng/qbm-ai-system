"use client";

import React, { useState } from 'react';
import { Card } from "@/components/ui/card";
import { X } from "lucide-react";

// 节点类型：五层自下而上
export type NodeType = 'investment' | 'cost' | 'asset' | 'capability' | 'process' | 'value' | 'revenue';

// 支撑强度
export type SupportStrength = 'strong' | 'medium' | 'weak';

export interface NetworkNode {
  id: string;
  type: NodeType;
  name: string;
  value: number;
  unit: string;
  changeRate?: number; // 变化率
  level: number; // 层级：1-5（底部到顶部）
}

export interface NetworkLink {
  source: string;
  target: string;
  value: number;
  strength: SupportStrength; // 支撑强度
  efficiency: number; // 支撑效率 0-1
}

export interface ValueNetworkGraphProps {
  nodes: NetworkNode[];
  links: NetworkLink[];
}

// 层级配置：自下而上
const LEVEL_CONFIG = {
  1: { y: 450, label: '基础支撑层', icon: '🏗️', color: '#FFD700' }, // 底部
  2: { y: 350, label: '能力支撑层', icon: '⚙️', color: '#4CAF50' },
  3: { y: 250, label: '流程转化层', icon: '🔄', color: '#2196F3' },
  4: { y: 150, label: '价值汇聚层', icon: '💎', color: '#9C27B0' },
  5: { y: 50, label: '目标收益层', icon: '🎯', color: '#FF9800' }, // 顶部
} as const;

// 支撑强度样式
const STRENGTH_STYLE = {
  strong: { width: 4, color: '#4CAF50', opacity: 0.8 },
  medium: { width: 2, color: '#FFC107', opacity: 0.7 },
  weak: { width: 1, color: '#F44336', opacity: 0.6 },
} as const;

// 节点颜色映射
const NODE_COLORS: Record<NodeType, string> = {
  investment: '#FFD700',
  cost: '#FF6B6B',
  asset: '#4CAF50',
  capability: '#66BB6A',
  process: '#2196F3',
  value: '#9C27B0',
  revenue: '#FF9800',
};

export function ValueNetworkGraph(props: ValueNetworkGraphProps) {
  const { nodes, links } = props;
  const [selectedNode, setSelectedNode] = useState<NetworkNode | null>(null);
  const [selectedLink, setSelectedLink] = useState<NetworkLink | null>(null);
  
  // 按层级分组节点
  const nodesByLevel = nodes.reduce((acc, node) => {
    if (!acc[node.level]) acc[node.level] = [];
    acc[node.level].push(node);
    return acc;
  }, {} as Record<number, NetworkNode[]>);

  // 计算节点位置
  const svgWidth = 1200;
  const svgHeight = 550;
  const nodePositions = new Map<string, { x: number; y: number }>();
  
  Object.entries(nodesByLevel).forEach(([level, levelNodes]) => {
    const levelNum = parseInt(level);
    const y = LEVEL_CONFIG[levelNum as keyof typeof LEVEL_CONFIG].y;
    const spacing = Math.min(150, svgWidth / (levelNodes.length + 1));
    const startX = (svgWidth - (levelNodes.length - 1) * spacing) / 2;
    
    levelNodes.forEach((node, idx) => {
      nodePositions.set(node.id, { x: startX + idx * spacing, y });
    });
  });

  // 计算节点半径
  const getRadius = (node: NetworkNode) => {
    const baseRadius = 24;
    const scale = Math.sqrt(Math.abs(node.value)) / 100;
    return Math.max(18, Math.min(36, baseRadius + scale * 10));
  };

  // 绘制向上箭头
  const drawArrow = (x1: number, y1: number, x2: number, y2: number, color: string, width: number) => {
    const angle = Math.atan2(y2 - y1, x2 - x1);
    const arrowSize = 8;
    const arrowX = x2 - Math.cos(angle) * (getRadius(nodes.find(n => nodePositions.get(n.id)?.x === x2 && nodePositions.get(n.id)?.y === y2)!) || 20);
    const arrowY = y2 - Math.sin(angle) * (getRadius(nodes.find(n => nodePositions.get(n.id)?.x === x2 && nodePositions.get(n.id)?.y === y2)!) || 20);
    
    return (
      <>
        <line
          x1={x1}
          y1={y1}
          x2={arrowX}
          y2={arrowY}
          stroke={color}
          strokeWidth={width}
          markerEnd="url(#arrowhead)"
        />
        <polygon
          points={`${arrowX},${arrowY} ${arrowX - arrowSize * Math.cos(angle - Math.PI / 6)},${arrowY - arrowSize * Math.sin(angle - Math.PI / 6)} ${arrowX - arrowSize * Math.cos(angle + Math.PI / 6)},${arrowY - arrowSize * Math.sin(angle + Math.PI / 6)}`}
          fill={color}
        />
      </>
    );
  };

  return (
    <div className="flex gap-4">
      <Card className="flex-1 p-6">
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-foreground">价值链网络图（自下而上支撑关系）</h3>
          <p className="text-sm text-muted-foreground mt-1">底层基础支撑上层目标，箭头方向表示支撑流向。点击节点或连接线查看详情。</p>
        </div>
        
        <svg width={svgWidth} height={svgHeight} className="w-full h-auto" style={{ maxHeight: '70vh' }}>
        <defs>
          <marker
            id="arrowhead"
            markerWidth="10"
            markerHeight="10"
            refX="5"
            refY="5"
            orient="auto"
          >
            <polygon points="0,0 10,5 0,10" fill="currentColor" />
          </marker>
        </defs>

        {/* 层级背景和标签 */}
        {Object.entries(LEVEL_CONFIG).map(([level, config]) => (
          <g key={`level-${level}`}>
            <rect
              x={0}
              y={config.y - 30}
              width={svgWidth}
              height={80}
              fill={config.color}
              opacity={0.05}
              rx={8}
            />
            <text
              x={20}
              y={config.y - 10}
              fontSize={12}
              fontWeight="600"
              fill={config.color}
            >
              {config.icon} {config.label}
            </text>
          </g>
        ))}

        {/* 支撑关系连接线（向上箭头）*/}
        {links.map((link, idx) => {
          const source = nodePositions.get(link.source);
          const target = nodePositions.get(link.target);
          if (!source || !target) return null;
          
          const style = STRENGTH_STYLE[link.strength];
          
          const isSelected = selectedLink?.source === link.source && selectedLink?.target === link.target;
          
          return (
            <g 
              key={`link-${idx}`} 
              opacity={isSelected ? 1 : style.opacity}
              className="cursor-pointer"
              onClick={(e) => {
                e.stopPropagation();
                setSelectedLink(link);
                setSelectedNode(null);
              }}
            >
              {drawArrow(source.x, source.y, target.x, target.y, style.color, style.width)}
              {/* 效率标签 */}
              <text
                x={(source.x + target.x) / 2}
                y={(source.y + target.y) / 2}
                fontSize={10}
                fill={style.color}
                textAnchor="middle"
                fontWeight="500"
              >
                {(link.efficiency * 100).toFixed(0)}%
              </text>
              {isSelected && (
                <circle
                  cx={(source.x + target.x) / 2}
                  cy={(source.y + target.y) / 2}
                  r={15}
                  fill="none"
                  stroke={style.color}
                  strokeWidth={2}
                  opacity={0.5}
                />
              )}
            </g>
          );
        })}

        {/* 节点 */}
        {nodes.map((node) => {
          const pos = nodePositions.get(node.id);
          if (!pos) return null;
          
          const radius = getRadius(node);
          const color = NODE_COLORS[node.type];
          const isSelected = selectedNode?.id === node.id;
          
          return (
            <g 
              key={node.id}
              className="cursor-pointer"
              onClick={(e) => {
                e.stopPropagation();
                setSelectedNode(node);
                setSelectedLink(null);
              }}
            >
              {/* 节点圆圈 */}
              <circle
                cx={pos.x}
                cy={pos.y}
                r={radius}
                fill={color}
                opacity={isSelected ? 1 : 0.85}
                stroke={isSelected ? "#fff" : "#fff"}
                strokeWidth={isSelected ? 3 : 2}
              />
              
              {/* 节点名称 */}
              <text
                x={pos.x}
                y={pos.y - radius - 8}
                textAnchor="middle"
                fontSize={11}
                fontWeight="600"
                fill="currentColor"
              >
                {node.name}
              </text>
              
              {/* 节点值 */}
              <text
                x={pos.x}
                y={pos.y + 4}
                textAnchor="middle"
                fontSize={10}
                fontWeight="500"
                fill="#fff"
              >
                {node.value}{node.unit}
              </text>
              
              {/* 变化率 */}
              {node.changeRate !== undefined && (
                <text
                  x={pos.x}
                  y={pos.y + radius + 16}
                  textAnchor="middle"
                  fontSize={9}
                  fill={node.changeRate >= 0 ? '#4CAF50' : '#F44336'}
                  fontWeight="600"
                >
                  {node.changeRate > 0 ? '↑' : '↓'}{Math.abs(node.changeRate)}%
                </text>
              )}
            </g>
          );
        })}
        </svg>

        {/* 紧凑图例 */}
        <div className="mt-4 flex items-center justify-center gap-6 text-xs text-muted-foreground">
          <div className="flex items-center gap-1.5">
            <div className="w-6 h-1 bg-[#4CAF50]"></div>
            <span>强</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-6 h-0.5 bg-[#FFC107]"></div>
            <span>中</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-6 h-px bg-[#F44336]"></div>
            <span>弱</span>
          </div>
        </div>
      </Card>

      {/* 详情面板 */}
      {(selectedNode || selectedLink) && (
        <Card className="w-80 p-4">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-semibold text-foreground">详细信息</h4>
            <button
              onClick={() => {
                setSelectedNode(null);
                setSelectedLink(null);
              }}
              className="p-1 hover:bg-accent rounded"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {selectedNode && (
            <div className="space-y-3">
              <div>
                <div className="text-xs text-muted-foreground mb-1">节点名称</div>
                <div className="font-medium">{selectedNode.name}</div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground mb-1">节点类型</div>
                <div className="inline-flex items-center gap-2">
                  <div 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: NODE_COLORS[selectedNode.type] }}
                  />
                  <span className="capitalize">{selectedNode.type}</span>
                </div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground mb-1">层级</div>
                <div>{LEVEL_CONFIG[selectedNode.level as keyof typeof LEVEL_CONFIG].icon} {LEVEL_CONFIG[selectedNode.level as keyof typeof LEVEL_CONFIG].label}</div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground mb-1">数值</div>
                <div className="text-lg font-semibold">{selectedNode.value}{selectedNode.unit}</div>
              </div>
              {selectedNode.changeRate !== undefined && (
                <div>
                  <div className="text-xs text-muted-foreground mb-1">变化率</div>
                  <div className={selectedNode.changeRate >= 0 ? 'text-green-600' : 'text-red-600'}>
                    {selectedNode.changeRate > 0 ? '↑' : '↓'}{Math.abs(selectedNode.changeRate)}%
                  </div>
                </div>
              )}
              <div>
                <div className="text-xs text-muted-foreground mb-1">支撑关系</div>
                <div className="text-sm space-y-1">
                  <div>输入: {links.filter(l => l.target === selectedNode.id).length} 个</div>
                  <div>输出: {links.filter(l => l.source === selectedNode.id).length} 个</div>
                </div>
              </div>
            </div>
          )}

          {selectedLink && (
            <div className="space-y-3">
              <div>
                <div className="text-xs text-muted-foreground mb-1">支撑关系</div>
                <div className="font-medium">
                  {nodes.find(n => n.id === selectedLink.source)?.name} → {nodes.find(n => n.id === selectedLink.target)?.name}
                </div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground mb-1">支撑强度</div>
                <div className="inline-flex items-center gap-2">
                  <div 
                    className="w-8 h-1 rounded" 
                    style={{ backgroundColor: STRENGTH_STYLE[selectedLink.strength].color }}
                  />
                  <span className="capitalize">
                    {selectedLink.strength === 'strong' ? '强支撑' : selectedLink.strength === 'medium' ? '中支撑' : '弱支撑'}
                  </span>
                </div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground mb-1">支撑效率</div>
                <div className="text-lg font-semibold">{(selectedLink.efficiency * 100).toFixed(1)}%</div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground mb-1">传递价值</div>
                <div className="text-lg font-semibold">{selectedLink.value}</div>
              </div>
              <div className="pt-2 border-t">
                <div className="text-xs text-muted-foreground mb-2">效率分析</div>
                <div className="text-sm">
                  {selectedLink.efficiency >= 0.8 ? '✅ 高效支撑，保持优势' : 
                   selectedLink.efficiency >= 0.6 ? '⚠️ 中等效率，有优化空间' : 
                   '🔴 效率较低，需要改进'}
                </div>
              </div>
            </div>
          )}
        </Card>
      )}
    </div>
  );
}

// Mock 数据生成器（完整版）
export function mockValueNetworkData() {
  const nodes: NetworkNode[] = [
    // 第1层：投资+成本（底部）
    { id: 'inv1', type: 'investment', name: '投资', value: 1000, unit: '万', changeRate: -10, level: 1 },
    { id: 'cost1', type: 'cost', name: '成本', value: 500, unit: '万', changeRate: -5, level: 1 },
    
    // 第2层：资产+能力（每个流程对应的资产和能力）
    { id: 'asset1', type: 'asset', name: '生产资产', value: 200, unit: '万', level: 2 },
    { id: 'cap1', type: 'capability', name: '生产能力', value: 180, unit: '万', level: 2 },
    { id: 'asset2', type: 'asset', name: '播传资产', value: 150, unit: '万', level: 2 },
    { id: 'cap2', type: 'capability', name: '播传能力', value: 140, unit: '万', level: 2 },
    { id: 'asset3', type: 'asset', name: '首单资产', value: 120, unit: '万', level: 2 },
    { id: 'cap3', type: 'capability', name: '首单能力', value: 110, unit: '万', level: 2 },
    { id: 'asset4', type: 'asset', name: '交付资产', value: 100, unit: '万', level: 2 },
    { id: 'cap4', type: 'capability', name: '交付能力', value: 90, unit: '万', level: 2 },
    
    // 第3层：流程（4个核心流程）
    { id: 'proc1', type: 'process', name: '生产流程', value: 0.08, unit: '', level: 3 },
    { id: 'proc2', type: 'process', name: '播传流程', value: 0.06, unit: '', level: 3 },
    { id: 'proc3', type: 'process', name: '首单流程', value: 0.25, unit: '', changeRate: 5, level: 3 },
    { id: 'proc4', type: 'process', name: '交付流程', value: 0.05, unit: '', level: 3 },
    
    // 第4层：价值要素
    { id: 'val1', type: 'value', name: '产品特性', value: 600, unit: '元', level: 4 },
    { id: 'val2', type: 'value', name: '产品内在', value: 741, unit: '分', level: 4 },
    { id: 'val3', type: 'value', name: '客户感知', value: 1000, unit: '元', changeRate: -5, level: 4 },
    { id: 'val4', type: 'value', name: '客户体验', value: 746, unit: '分', level: 4 },
    
    // 第5层：收益（顶部）
    { id: 'rev1', type: 'revenue', name: '首单收入', value: 100, unit: '万', changeRate: 15, level: 5 },
    { id: 'rev2', type: 'revenue', name: '追销收入', value: 80, unit: '万', changeRate: 20, level: 5 },
    { id: 'rev3', type: 'revenue', name: '复购收入', value: 120, unit: '万', changeRate: 10, level: 5 },
  ];

  const links: NetworkLink[] = [
    // 第1层 → 第2层（投资成本支撑资产+能力）
    { source: 'inv1', target: 'asset1', value: 200, strength: 'strong', efficiency: 0.85 },
    { source: 'inv1', target: 'cap1', value: 180, strength: 'strong', efficiency: 0.82 },
    { source: 'inv1', target: 'asset2', value: 150, strength: 'medium', efficiency: 0.75 },
    { source: 'inv1', target: 'cap2', value: 140, strength: 'medium', efficiency: 0.70 },
    { source: 'cost1', target: 'asset3', value: 120, strength: 'strong', efficiency: 0.80 },
    { source: 'cost1', target: 'cap3', value: 110, strength: 'strong', efficiency: 0.78 },
    { source: 'cost1', target: 'asset4', value: 100, strength: 'strong', efficiency: 0.90 },
    { source: 'cost1', target: 'cap4', value: 90, strength: 'strong', efficiency: 0.88 },
    
    // 第2层 → 第3层（资产+能力支撑流程，确保每个流程都有对应的资产和能力）
    { source: 'asset1', target: 'proc1', value: 80, strength: 'strong', efficiency: 0.85 },
    { source: 'cap1', target: 'proc1', value: 75, strength: 'strong', efficiency: 0.80 },
    { source: 'asset2', target: 'proc2', value: 70, strength: 'medium', efficiency: 0.65 },
    { source: 'cap2', target: 'proc2', value: 65, strength: 'weak', efficiency: 0.40 },
    { source: 'asset3', target: 'proc3', value: 60, strength: 'medium', efficiency: 0.68 },
    { source: 'cap3', target: 'proc3', value: 55, strength: 'medium', efficiency: 0.65 },
    { source: 'asset4', target: 'proc4', value: 50, strength: 'strong', efficiency: 0.90 },
    { source: 'cap4', target: 'proc4', value: 45, strength: 'strong', efficiency: 0.88 },
    
    // 第3层 → 第4层（流程支撑价值要素）
    { source: 'proc1', target: 'val1', value: 600, strength: 'strong', efficiency: 0.82 },
    { source: 'proc1', target: 'val2', value: 741, strength: 'strong', efficiency: 0.80 },
    { source: 'proc2', target: 'val3', value: 1000, strength: 'medium', efficiency: 0.55 },
    { source: 'proc3', target: 'val3', value: 1000, strength: 'medium', efficiency: 0.68 },
    { source: 'proc4', target: 'val4', value: 746, strength: 'strong', efficiency: 0.90 },
    
    // 第4层 → 第5层（价值要素转化为收益）
    { source: 'val1', target: 'rev1', value: 100, strength: 'strong', efficiency: 0.92 },
    { source: 'val2', target: 'rev1', value: 100, strength: 'strong', efficiency: 0.88 },
    { source: 'val3', target: 'rev1', value: 100, strength: 'weak', efficiency: 0.45 },
    { source: 'val3', target: 'rev2', value: 80, strength: 'medium', efficiency: 0.70 },
    { source: 'val4', target: 'rev2', value: 80, strength: 'strong', efficiency: 0.85 },
    { source: 'val4', target: 'rev3', value: 120, strength: 'strong', efficiency: 0.95 },
  ];

  return { nodes, links };
}





