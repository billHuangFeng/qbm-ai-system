"use client";

import React, { useState, useRef, useCallback } from 'react';
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { X, Edit3, Eye, RotateCcw } from "lucide-react";

// 节点类型：五层自下而上 + 毛利节点
export type NodeType = 'investment' | 'cost' | 'resource' | 'asset' | 'capability' | 'process' | 'value' | 'revenue' | 'margin';

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
  linkType?: 'normal' | 'horizontal' | 'feedback' | 'revenue-to-cost' | 'l-shape'; // 连接类型
}

export interface ValueNetworkGraphProps {
  nodes: NetworkNode[];
  links: NetworkLink[];
}

// 层级配置：自下而上（颜色参考用户提供图片）
const LEVEL_CONFIG = {
  1: { y: 700, label: '基础支撑层', icon: '🏗️', color: '#8B6914' }, // 底部 - 棕褐色
  2: { y: 600, label: '能力支撑层', icon: '⚙️', color: '#4CAF50' }, // 绿色
  3: { y: 500, label: '流程转化层', icon: '🔄', color: '#2196F3' }, // 蓝色
  4: { y: 380, label: '价值产出层', icon: '💎', color: '#9C27B0' }, // 紫色 - 产品特性+内在价值
  5: { y: 260, label: '价值传递层', icon: '🎁', color: '#E91E63' }, // 粉红 - 客户感知+体验价值
  6: { y: 140, label: '目标收益层', icon: '🎯', color: '#FFB300' }, // 顶部 - 橙黄色
} as const;

// 根据效率动态计算箭头样式
const getArrowStyle = (efficiency: number) => {
  const width = Math.max(1, Math.min(6, efficiency * 6)); // 效率 0-100% 映射到宽度 1-6
  let color = '#FF5252'; // 更亮的红色（弱）
  let opacity = 0.65;
  
  if (efficiency >= 0.8) {
    color = '#00E676'; // 更亮的绿色（强）
    opacity = 0.95;
  } else if (efficiency >= 0.5) {
    color = '#FFD700'; // 更亮的黄色（中）
    opacity = 0.8;
  }
  
  return { color, width, opacity };
};

// 节点颜色映射
const NODE_COLORS: Record<NodeType, string> = {
  investment: '#FFD700',
  cost: '#FF6B6B',
  resource: '#795548', // 棕色，代表原材料/资源
  asset: '#4CAF50',
  capability: '#66BB6A',
  process: '#2196F3',
  value: '#9C27B0',
  revenue: '#FF6F00', // 深橙色，在橙黄色背景上更清晰
  margin: '#FF8F00', // 毛利节点（深橙色）
};

export function ValueNetworkGraph(props: ValueNetworkGraphProps) {
  const { nodes, links } = props;
  const [selectedNode, setSelectedNode] = useState<NetworkNode | null>(null);
  const [selectedLink, setSelectedLink] = useState<NetworkLink | null>(null);
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);
  const [isEditMode, setIsEditMode] = useState(false);
  const [customPositions, setCustomPositions] = useState<Map<string, { x: number; y: number }>>(new Map());
  const [draggingNodeId, setDraggingNodeId] = useState<string | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);
  
  // 按层级分组节点
  const nodesByLevel = nodes.reduce((acc, node) => {
    if (!acc[node.level]) acc[node.level] = [];
    acc[node.level].push(node);
    return acc;
  }, {} as Record<number, NetworkNode[]>);

  // 计算节点位置（第6层分为收益组和毛利组，第1层成本放左侧）
  const svgWidth = 1200; // 优化宽度适配屏幕
  const svgHeight = 800; // 优化高度以容纳更多层级和U型回流路径
  const nodePositions = new Map<string, { x: number; y: number }>();
  
  Object.entries(nodesByLevel).forEach(([level, levelNodes]) => {
    const levelNum = parseInt(level);
    const y = LEVEL_CONFIG[levelNum as keyof typeof LEVEL_CONFIG].y;
    
    if (levelNum === 6) {
      // 第6层特殊处理：收益在左，毛利在右
      const revenueNodes = levelNodes.filter(n => n.type === 'revenue');
      const marginNodes = levelNodes.filter(n => n.type === 'margin');
      
      const revenueSpacing = (svgWidth * 0.4) / (revenueNodes.length + 1);
      revenueNodes.forEach((node, idx) => {
        nodePositions.set(node.id, { x: revenueSpacing * (idx + 1) + 100, y });
      });
      
      const marginSpacing = (svgWidth * 0.4) / (marginNodes.length + 1);
      marginNodes.forEach((node, idx) => {
        nodePositions.set(node.id, { x: svgWidth * 0.6 + marginSpacing * (idx + 1), y });
      });
    } else if (levelNum === 1) {
      // 第1层特殊处理：成本在左侧，投资在右侧
      const costNodes = levelNodes.filter(n => n.type === 'cost');
      const investmentNodes = levelNodes.filter(n => n.type === 'investment');
      
      // 成本节点放在左侧（x = 150）
      costNodes.forEach((node) => {
        nodePositions.set(node.id, { x: 150, y });
      });
      
      // 投资节点放在右侧（x = svgWidth - 150）
      investmentNodes.forEach((node) => {
        nodePositions.set(node.id, { x: svgWidth - 150, y });
      });
    } else {
      // 其他层级均匀分布
      const spacing = Math.min(150, (svgWidth - 200) / (levelNodes.length + 1));
      const startX = (svgWidth - (levelNodes.length - 1) * spacing) / 2;
      
      levelNodes.forEach((node, idx) => {
        nodePositions.set(node.id, { x: startX + idx * spacing, y });
      });
    }
  });

  // 计算节点半径
  const getRadius = (node: NetworkNode) => {
    const baseRadius = 24;
    const scale = Math.sqrt(Math.abs(node.value)) / 100;
    return Math.max(18, Math.min(36, baseRadius + scale * 10));
  };

  // 绘制向上箭头
  const drawArrow = (x1: number, y1: number, x2: number, y2: number, color: string, width: number) => {
    const midY = (y1 + y2) / 2;
    return (
      <path
        d={`M ${x1} ${y1} C ${x1} ${midY}, ${x2} ${midY}, ${x2} ${y2}`}
        stroke={color}
        strokeWidth={width}
        fill="none"
        markerEnd="url(#arrowhead)"
      />
    );
  };

  // 绘制水平连接线（同层收益到毛利）
  const drawHorizontalLine = (x1: number, y1: number, x2: number, y2: number, color: string, width: number) => {
    return (
      <path
        d={`M ${x1} ${y1} L ${x2} ${y2}`}
        stroke={color}
        strokeWidth={width}
        fill="none"
        markerEnd="url(#arrowhead)"
      />
    );
  };

  // 绘制L型箭头（投资到能力/资产，避免视觉重叠）
  const drawLShapeArrow = (x1: number, y1: number, x2: number, y2: number, color: string, width: number) => {
    // 计算中间转折点：先向上走70%的距离，然后水平移动，最后向上到目标
    const verticalDistance = y1 - y2;
    const midY = y1 - verticalDistance * 0.7;
    
    return (
      <path
        d={`M ${x1} ${y1} L ${x1} ${midY} L ${x2} ${midY} L ${x2} ${y2}`}
        stroke={color}
        strokeWidth={width}
        fill="none"
        markerEnd="url(#arrowhead)"
      />
    );
  };

  // 绘制毛利回流箭头（U型路径：毛利顶部→上→右→下→左→投资底部）
  const drawFeedbackArrow = (x1: number, y1: number, x2: number, y2: number) => {
    const cornerRadius = 12;
    const topY = 30; // 顶部水平线高度
    const rightEdge = svgWidth - 30; // 右侧边缘
    const bottomY = svgHeight - 30; // 底部水平线高度
    const nodeRadius = 30; // 节点半径
    
    // U型路径：毛利顶部 → 向上到顶部 → 向右到右边缘 → 向下到底部 → 向左到投资下方 → 向上接入投资底部
    const pathData = `
      M ${x1} ${y1 - nodeRadius}
      L ${x1} ${topY + cornerRadius}
      Q ${x1} ${topY}, ${x1 + cornerRadius} ${topY}
      L ${rightEdge - cornerRadius} ${topY}
      Q ${rightEdge} ${topY}, ${rightEdge} ${topY + cornerRadius}
      L ${rightEdge} ${bottomY - cornerRadius}
      Q ${rightEdge} ${bottomY}, ${rightEdge - cornerRadius} ${bottomY}
      L ${x2 + cornerRadius} ${bottomY}
      Q ${x2} ${bottomY}, ${x2} ${bottomY - cornerRadius}
      L ${x2} ${y2 + nodeRadius}
    `;
    
    return (
      <>
        <path
          d={pathData}
          stroke="#FFD700"
          strokeWidth={2.5}
          strokeDasharray="8,4"
          fill="none"
          markerEnd="url(#arrowhead-feedback)"
          opacity={0.85}
        />
        <text
          x={rightEdge - 15}
          y={(topY + bottomY) / 2}
          textAnchor="start"
          className="text-xs fill-yellow-600 font-medium pointer-events-none"
          style={{ writingMode: 'vertical-rl' }}
        >
          💰 毛利回流
        </text>
      </>
    );
  };

  // 绘制收入到成本的反馈箭头（U型路径：收入顶部→上→左→下→右→成本底部）
  const drawRevenueToCostArrow = (x1: number, y1: number, x2: number, y2: number) => {
    const cornerRadius = 12;
    const topY = 30; // 顶部水平线高度
    const leftEdge = 30; // 左侧边缘
    const bottomY = svgHeight - 30; // 底部水平线高度
    const nodeRadius = 30; // 节点半径
    
    // U型路径：收入顶部 → 向上到顶部 → 向左到左边缘 → 向下到底部 → 向右到成本下方 → 向上接入成本底部
    const pathData = `
      M ${x1} ${y1 - nodeRadius}
      L ${x1} ${topY + cornerRadius}
      Q ${x1} ${topY}, ${x1 - cornerRadius} ${topY}
      L ${leftEdge + cornerRadius} ${topY}
      Q ${leftEdge} ${topY}, ${leftEdge} ${topY + cornerRadius}
      L ${leftEdge} ${bottomY - cornerRadius}
      Q ${leftEdge} ${bottomY}, ${leftEdge + cornerRadius} ${bottomY}
      L ${x2 - cornerRadius} ${bottomY}
      Q ${x2} ${bottomY}, ${x2} ${bottomY - cornerRadius}
      L ${x2} ${y2 + nodeRadius}
    `;
    
    return (
      <>
        <path
          d={pathData}
          stroke="#FF6B6B"
          strokeWidth={2.5}
          strokeDasharray="8,4"
          fill="none"
          markerEnd="url(#arrowhead-cost)"
          opacity={0.85}
        />
        <text
          x={leftEdge + 15}
          y={(topY + bottomY) / 2}
          textAnchor="start"
          className="text-xs fill-red-600 font-medium pointer-events-none"
          style={{ writingMode: 'vertical-rl' }}
        >
          💸 成本投入
        </text>
      </>
    );
  };

  // 获取相关连接（用于悬停高亮）
  const getRelatedLinks = (nodeId: string | null) => {
    if (!nodeId) return new Set<string>();
    const related = new Set<string>();
    links.forEach(link => {
      if (link.source === nodeId || link.target === nodeId) {
        related.add(`${link.source}-${link.target}`);
      }
    });
    return related;
  };

  const relatedLinks = getRelatedLinks(hoveredNodeId);

  // 获取节点最终位置（优先使用自定义位置）
  const getFinalPosition = useCallback((nodeId: string) => {
    return customPositions.get(nodeId) || nodePositions.get(nodeId) || { x: 0, y: 0 };
  }, [customPositions, nodePositions]);

  // 处理拖拽开始
  const handleMouseDown = useCallback((e: React.MouseEvent, node: NetworkNode) => {
    if (!isEditMode) return;
    
    e.stopPropagation();
    setDraggingNodeId(node.id);
    
    const svgElement = svgRef.current;
    if (!svgElement) return;

    const startClientX = e.clientX;
    const currentPos = getFinalPosition(node.id);
    const initialX = currentPos.x;
    const nodeLevel = node.level;

    const handleMouseMove = (moveEvent: MouseEvent) => {
      const deltaX = moveEvent.clientX - startClientX;
      let newX = initialX + deltaX;
      
      // 边界限制：50 到 svgWidth-50
      newX = Math.max(50, Math.min(svgWidth - 50, newX));
      
      // 更新位置（Y轴保持不变）
      setCustomPositions(prev => {
        const newMap = new Map(prev);
        newMap.set(node.id, {
          x: newX,
          y: currentPos.y // Y轴锁定
        });
        return newMap;
      });
    };

    const handleMouseUp = () => {
      setDraggingNodeId(null);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);
  }, [isEditMode, getFinalPosition, svgWidth]);

  // 重置布局
  const handleResetLayout = useCallback(() => {
    setCustomPositions(new Map());
  }, []);

  return (
    <div className="flex gap-4">
      <Card className="flex-1 p-6">
        <div className="mb-4 flex items-start justify-between">
          <div>
            <h3 className="text-lg font-semibold text-foreground">价值链网络图（自下而上支撑关系）</h3>
            <p className="text-sm text-muted-foreground mt-1">
              底层基础支撑上层目标，箭头方向表示支撑流向。毛利回流形成闭环支撑投资。
              {isEditMode && <span className="text-primary font-medium ml-2">🎨 拖拽节点可调整同层级位置</span>}
            </p>
          </div>
          
          {/* 工具栏 */}
          <div className="flex gap-2">
            <Button 
              variant={isEditMode ? "default" : "outline"}
              size="sm"
              onClick={() => setIsEditMode(!isEditMode)}
            >
              {isEditMode ? (
                <>
                  <Edit3 className="w-4 h-4 mr-1" />
                  编辑模式
                </>
              ) : (
                <>
                  <Eye className="w-4 h-4 mr-1" />
                  查看模式
                </>
              )}
            </Button>
            
            <Button 
              variant="outline" 
              size="sm"
              onClick={handleResetLayout}
              disabled={customPositions.size === 0}
            >
              <RotateCcw className="w-4 h-4 mr-1" />
              重置布局
            </Button>
          </div>
        </div>
        
        <div className="w-full flex items-center justify-center">
          <svg ref={svgRef} viewBox="0 0 1200 800" className="w-full h-auto max-h-[calc(100vh-180px)]" preserveAspectRatio="xMidYMid meet">
        <defs>
          <marker
            id="arrowhead"
            markerWidth="10"
            markerHeight="10"
            refX="9"
            refY="3"
            orient="auto"
            markerUnits="strokeWidth"
          >
            <path d="M0,0 L0,6 L9,3 z" fill="currentColor" />
          </marker>
          <marker
            id="arrowhead-feedback"
            markerWidth="12"
            markerHeight="12"
            refX="10"
            refY="3"
            orient="auto"
            markerUnits="strokeWidth"
          >
            <path d="M0,0 L0,6 L10,3 z" fill="#FFD700" />
          </marker>
          <marker
            id="arrowhead-cost"
            markerWidth="12"
            markerHeight="12"
            refX="10"
            refY="3"
            orient="auto"
            markerUnits="strokeWidth"
          >
            <path d="M0,0 L0,6 L10,3 z" fill="#FF6B6B" />
          </marker>
        </defs>

        {/* 全幅色带背景（无文字标签）*/}
        {Object.entries(LEVEL_CONFIG).map(([level, config]) => (
          <rect
            key={`level-bg-${level}`}
            x={0}
            y={config.y - 55}
            width={svgWidth}
            height={110}
            fill={config.color}
            opacity={0.15}
            rx={0}
          />
        ))}

        {/* 支撑关系连接线 */}
        {links.map((link, idx) => {
          const source = getFinalPosition(link.source);
          const target = getFinalPosition(link.target);
          if (!source || !target) return null;

          const efficiency = link.efficiency || 0.7;
          const style = getArrowStyle(efficiency);
          const linkKey = `${link.source}-${link.target}`;
          const isRelated = !hoveredNodeId || relatedLinks.has(linkKey);
          const isSelected = selectedLink?.source === link.source && selectedLink?.target === link.target;

          // 判断连接类型
          const isFeedback = link.linkType === 'feedback';
          const isRevenueToCost = link.linkType === 'revenue-to-cost';
          const isHorizontal = link.linkType === 'horizontal';
          const isLShape = link.linkType === 'l-shape';

          return (
            <g
              key={`link-${idx}`}
              opacity={isSelected ? 1 : (isRelated ? style.opacity : 0.15)}
              className="cursor-pointer"
              onClick={(e) => {
                e.stopPropagation();
                setSelectedLink(link);
                setSelectedNode(null);
              }}
            >
              {isFeedback ? (
                // 毛利回流到投资（右侧门字形虚线）
                drawFeedbackArrow(source.x, source.y, target.x, target.y)
              ) : isRevenueToCost ? (
                // 收入到成本（左侧门字形虚线）
                drawRevenueToCostArrow(source.x, source.y, target.x, target.y)
              ) : isHorizontal ? (
                // 同层水平连接（收益到毛利）
                drawHorizontalLine(source.x, source.y, target.x, target.y, style.color, style.width)
              ) : isLShape ? (
                // L型箭头（投资到能力/资产，避免视觉重叠）
                drawLShapeArrow(source.x, source.y, target.x, target.y, style.color, style.width)
              ) : (
                // 普通向上箭头
                drawArrow(source.x, source.y, target.x, target.y, style.color, style.width)
              )}
              
              {/* 效率标签（普通箭头和L型箭头显示）*/}
              {!isFeedback && !isRevenueToCost && !isHorizontal && (
                <>
                  <rect
                    x={(source.x + target.x) / 2 - 18}
                    y={(source.y + target.y) / 2 - 9}
                    width={36}
                    height={18}
                    fill="white"
                    opacity={0.95}
                    rx={4}
                  />
                  <text
                    x={(source.x + target.x) / 2}
                    y={(source.y + target.y) / 2 + 4}
                    fontSize={11}
                    fill={style.color}
                    textAnchor="middle"
                    fontWeight="700"
                  >
                    {(link.efficiency * 100).toFixed(0)}%
                  </text>
                </>
              )}
            </g>
          );
        })}

        {/* 节点 */}
        {nodes.map((node) => {
          const pos = getFinalPosition(node.id);
          if (!pos) return null;
          
          const radius = getRadius(node);
          const color = NODE_COLORS[node.type];
          const isSelected = selectedNode?.id === node.id;
          const isHovered = hoveredNodeId === node.id;
          const isDragging = draggingNodeId === node.id;
          
          return (
            <g 
              key={node.id}
              className={isEditMode ? 'cursor-grab active:cursor-grabbing' : 'cursor-pointer'}
              onClick={(e) => {
                if (!isEditMode) {
                  e.stopPropagation();
                  setSelectedNode(node);
                  setSelectedLink(null);
                }
              }}
              onMouseDown={(e) => handleMouseDown(e, node)}
              onMouseEnter={() => setHoveredNodeId(node.id)}
              onMouseLeave={() => setHoveredNodeId(null)}
              style={{ 
                transition: isDragging ? 'none' : 'all 0.2s ease',
                opacity: isDragging ? 0.7 : 1
              }}
            >
              {/* 节点圆圈 */}
              <circle
                cx={pos.x}
                cy={pos.y}
                r={radius}
                fill={color}
                opacity={isSelected || isHovered ? 1 : (hoveredNodeId ? 0.3 : 0.9)}
                stroke="#fff"
                strokeWidth={isSelected ? 4 : 3}
                style={{ 
                  transition: isDragging ? 'none' : 'all 0.2s ease',
                  filter: isDragging ? 'drop-shadow(0 8px 16px rgba(0,0,0,0.3))' : 
                          isHovered ? 'drop-shadow(0 4px 8px rgba(0,0,0,0.2))' : 'none'
                }}
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
        </div>

        {/* 紧凑图例 */}
        <div className="mt-4 flex items-center justify-center gap-6 text-xs text-muted-foreground">
          <div className="flex items-center gap-1.5">
            <div className="w-6 h-1 bg-[#00E676]"></div>
            <span>强 ≥80%</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-6 h-0.5 bg-[#FFD700]"></div>
            <span>中 50-80%</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-6 h-px bg-[#FF5252]"></div>
            <span>弱 &lt;50%</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-6 h-px bg-[#FFD700] opacity-80" style={{ borderTop: '2px dashed #FFD700' }}></div>
            <span>毛利回流</span>
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
                  <span className="capitalize">
                    {selectedNode.type === 'margin' ? '毛利' : 
                     selectedNode.type === 'resource' ? '生产资源' : 
                     selectedNode.type}
                  </span>
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
                   selectedLink.efficiency >= 0.5 ? '⚠️ 中等效率，有优化空间' : 
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

// Mock 数据生成器（优化版：6个流程完整，毛利回流）
export function mockValueNetworkData() {
  const nodes: NetworkNode[] = [
    // 第1层：投资+成本（底部）
    { id: 'inv1', type: 'investment', name: '投资', value: 1000, unit: '万', changeRate: -10, level: 1 },
    { id: 'cost1', type: 'cost', name: '成本', value: 500, unit: '万', changeRate: -5, level: 1 },
    
    // 第2层：生产资源 + 6个流程的资产+能力（每个流程对应1个资产+1个能力）
    { id: 'resource1', type: 'resource', name: '生产资源', value: 450, unit: '万', level: 2 },
    { id: 'asset1', type: 'asset', name: '生产资产', value: 200, unit: '万', level: 2 },
    { id: 'cap1', type: 'capability', name: '生产能力', value: 180, unit: '万', level: 2 },
    { id: 'asset2', type: 'asset', name: '播传资产', value: 150, unit: '万', level: 2 },
    { id: 'cap2', type: 'capability', name: '播传能力', value: 140, unit: '万', level: 2 },
    { id: 'asset3', type: 'asset', name: '首单资产', value: 120, unit: '万', level: 2 },
    { id: 'cap3', type: 'capability', name: '首单能力', value: 110, unit: '万', level: 2 },
    { id: 'asset4', type: 'asset', name: '交付资产', value: 100, unit: '万', level: 2 },
    { id: 'cap4', type: 'capability', name: '交付能力', value: 90, unit: '万', level: 2 },
    { id: 'asset5', type: 'asset', name: '追销资产', value: 80, unit: '万', level: 2 },
    { id: 'cap5', type: 'capability', name: '追销能力', value: 75, unit: '万', level: 2 },
    { id: 'asset6', type: 'asset', name: '复购资产', value: 90, unit: '万', level: 2 },
    { id: 'cap6', type: 'capability', name: '复购能力', value: 85, unit: '万', level: 2 },
    
    // 第3层：6个核心流程
    { id: 'proc1', type: 'process', name: '生产流程', value: 0.08, unit: '', level: 3 },
    { id: 'proc2', type: 'process', name: '播传流程', value: 0.06, unit: '', level: 3 },
    { id: 'proc3', type: 'process', name: '首单流程', value: 0.25, unit: '', changeRate: 5, level: 3 },
    { id: 'proc4', type: 'process', name: '交付流程', value: 0.05, unit: '', level: 3 },
    { id: 'proc5', type: 'process', name: '追销流程', value: 0.15, unit: '', level: 3 },
    { id: 'proc6', type: 'process', name: '复购流程', value: 0.20, unit: '', level: 3 },
    
    // 第4层：价值产出层（产品特性+内在价值）
    { id: 'val1', type: 'value', name: '产品特性', value: 600, unit: '元', level: 4 },
    { id: 'val2', type: 'value', name: '产品内在价值', value: 741, unit: '分', level: 4 },
    
    // 第5层：价值传递层（客户感知+体验价值）
    { id: 'val3', type: 'value', name: '客户感知价值', value: 1000, unit: '元', changeRate: -5, level: 5 },
    { id: 'val4', type: 'value', name: '客户体验价值', value: 746, unit: '分', level: 5 },
    
    // 第6层：收益 + 毛利（顶部）
    { id: 'rev1', type: 'revenue', name: '首单收入', value: 100, unit: '万', changeRate: 15, level: 6 },
    { id: 'rev2', type: 'revenue', name: '追销收入', value: 80, unit: '万', changeRate: 20, level: 6 },
    { id: 'rev3', type: 'revenue', name: '复购收入', value: 120, unit: '万', changeRate: 10, level: 6 },
    { id: 'margin1', type: 'margin', name: '首单毛利', value: 60, unit: '万', changeRate: 12, level: 6 },
    { id: 'margin2', type: 'margin', name: '追销毛利', value: 50, unit: '万', changeRate: 18, level: 6 },
    { id: 'margin3', type: 'margin', name: '复购毛利', value: 70, unit: '万', changeRate: 8, level: 6 },
  ];

  const links: NetworkLink[] = [
    // 第1层 → 第2层：投资支撑所有资产+能力（12条L型箭头，避免视觉重叠），成本转化为生产资源（1条）
    { source: 'inv1', target: 'asset1', value: 200, strength: 'strong', efficiency: 0.85, linkType: 'l-shape' },
    { source: 'inv1', target: 'cap1', value: 180, strength: 'strong', efficiency: 0.82, linkType: 'l-shape' },
    { source: 'inv1', target: 'asset2', value: 150, strength: 'strong', efficiency: 0.78, linkType: 'l-shape' },
    { source: 'inv1', target: 'cap2', value: 140, strength: 'medium', efficiency: 0.75, linkType: 'l-shape' },
    { source: 'inv1', target: 'asset3', value: 120, strength: 'medium', efficiency: 0.70, linkType: 'l-shape' },
    { source: 'inv1', target: 'cap3', value: 110, strength: 'medium', efficiency: 0.68, linkType: 'l-shape' },
    { source: 'inv1', target: 'asset4', value: 100, strength: 'medium', efficiency: 0.65, linkType: 'l-shape' },
    { source: 'inv1', target: 'cap4', value: 90, strength: 'medium', efficiency: 0.62, linkType: 'l-shape' },
    { source: 'inv1', target: 'asset5', value: 80, strength: 'medium', efficiency: 0.60, linkType: 'l-shape' },
    { source: 'inv1', target: 'cap5', value: 75, strength: 'medium', efficiency: 0.58, linkType: 'l-shape' },
    { source: 'inv1', target: 'asset6', value: 90, strength: 'strong', efficiency: 0.72, linkType: 'l-shape' },
    { source: 'inv1', target: 'cap6', value: 85, strength: 'medium', efficiency: 0.70, linkType: 'l-shape' },
    
    // 成本转化为生产资源
    { source: 'cost1', target: 'resource1', value: 450, strength: 'strong', efficiency: 0.90, linkType: 'normal' },
    
    // 第2层 → 第3层：生产资源流入生产流程，每个流程对应1个资产+1个能力（13条）
    { source: 'resource1', target: 'proc1', value: 0.08, strength: 'strong', efficiency: 0.85, linkType: 'normal' },
    { source: 'asset1', target: 'proc1', value: 0.08, strength: 'strong', efficiency: 0.92, linkType: 'normal' },
    { source: 'cap1', target: 'proc1', value: 0.08, strength: 'strong', efficiency: 0.90, linkType: 'normal' },
    { source: 'asset2', target: 'proc2', value: 0.06, strength: 'strong', efficiency: 0.85, linkType: 'normal' },
    { source: 'cap2', target: 'proc2', value: 0.06, strength: 'medium', efficiency: 0.78, linkType: 'normal' },
    { source: 'asset3', target: 'proc3', value: 0.25, strength: 'strong', efficiency: 0.88, linkType: 'normal' },
    { source: 'cap3', target: 'proc3', value: 0.25, strength: 'strong', efficiency: 0.85, linkType: 'normal' },
    { source: 'asset4', target: 'proc4', value: 0.05, strength: 'medium', efficiency: 0.72, linkType: 'normal' },
    { source: 'cap4', target: 'proc4', value: 0.05, strength: 'medium', efficiency: 0.70, linkType: 'normal' },
    { source: 'asset5', target: 'proc5', value: 0.15, strength: 'strong', efficiency: 0.80, linkType: 'normal' },
    { source: 'cap5', target: 'proc5', value: 0.15, strength: 'medium', efficiency: 0.75, linkType: 'normal' },
    { source: 'asset6', target: 'proc6', value: 0.20, strength: 'strong', efficiency: 0.82, linkType: 'normal' },
    { source: 'cap6', target: 'proc6', value: 0.20, strength: 'strong', efficiency: 0.78, linkType: 'normal' },
    
    // 第3层 → 第4层：流程转化为价值产出（产品特性+内在价值）
    { source: 'proc1', target: 'val1', value: 600, strength: 'strong', efficiency: 0.90, linkType: 'normal' },
    { source: 'proc1', target: 'val2', value: 741, strength: 'strong', efficiency: 0.88, linkType: 'normal' },
    
    // 第4层 → 第5层：价值产出转化为价值传递（客户感知+体验）
    { source: 'val1', target: 'val3', value: 1000, strength: 'strong', efficiency: 0.85, linkType: 'normal' },
    { source: 'val2', target: 'val3', value: 1000, strength: 'strong', efficiency: 0.88, linkType: 'normal' },
    { source: 'val2', target: 'val4', value: 746, strength: 'medium', efficiency: 0.75, linkType: 'normal' },
    
    // 第3层 → 第5层：部分流程直接影响客户感知/体验
    { source: 'proc2', target: 'val3', value: 1000, strength: 'strong', efficiency: 0.85, linkType: 'normal' },
    { source: 'proc3', target: 'val3', value: 1000, strength: 'strong', efficiency: 0.92, linkType: 'normal' },
    { source: 'proc4', target: 'val4', value: 746, strength: 'medium', efficiency: 0.75, linkType: 'normal' },
    { source: 'proc5', target: 'val3', value: 1000, strength: 'strong', efficiency: 0.82, linkType: 'normal' },
    { source: 'proc6', target: 'val4', value: 746, strength: 'strong', efficiency: 0.80, linkType: 'normal' },
    
    // 第5层 → 第6层：价值传递转化为收益
    { source: 'val3', target: 'rev1', value: 100, strength: 'strong', efficiency: 0.90, linkType: 'normal' },
    { source: 'val3', target: 'rev2', value: 80, strength: 'strong', efficiency: 0.85, linkType: 'normal' },
    { source: 'val4', target: 'rev2', value: 80, strength: 'medium', efficiency: 0.78, linkType: 'normal' },
    { source: 'val4', target: 'rev3', value: 120, strength: 'strong', efficiency: 0.82, linkType: 'normal' },
    
    // 第6层同层：收益 → 毛利（水平连接）
    { source: 'rev1', target: 'margin1', value: 60, strength: 'strong', efficiency: 0.60, linkType: 'horizontal' },
    { source: 'rev2', target: 'margin2', value: 50, strength: 'strong', efficiency: 0.625, linkType: 'horizontal' },
    { source: 'rev3', target: 'margin3', value: 70, strength: 'strong', efficiency: 0.583, linkType: 'horizontal' },
    
    // 特殊：毛利回流到投资（右侧门字形虚线闭环）
    { source: 'margin1', target: 'inv1', value: 60, strength: 'strong', efficiency: 1, linkType: 'feedback' },
    { source: 'margin2', target: 'inv1', value: 50, strength: 'strong', efficiency: 1, linkType: 'feedback' },
    { source: 'margin3', target: 'inv1', value: 70, strength: 'strong', efficiency: 1, linkType: 'feedback' },
    
    // 特殊：收入到成本的反馈（左侧门字形虚线）
    { source: 'rev1', target: 'cost1', value: 40, strength: 'medium', efficiency: 1, linkType: 'revenue-to-cost' },
    { source: 'rev2', target: 'cost1', value: 30, strength: 'medium', efficiency: 1, linkType: 'revenue-to-cost' },
    { source: 'rev3', target: 'cost1', value: 50, strength: 'medium', efficiency: 1, linkType: 'revenue-to-cost' },
  ];

  return { nodes, links };
}
