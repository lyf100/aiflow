/**
 * Flowchart Viewer - D3.js 流程图可视化组件
 *
 * 使用 D3.js 渲染执行轨迹的流程图格式。
 * 支持 fork（并发分叉）和 join（并发汇合）节点。
 */

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { useAnalysisStore } from '../../stores/analysisStore';
import { useVisualizationStore } from '../../stores/visualizationStore';
import './FlowchartViewer.css';

interface FlowchartStep {
  id: string;
  label: string;
  type: 'start' | 'end' | 'process' | 'decision' | 'fork' | 'join';
}

interface FlowchartConnection {
  id: string;
  source: string;
  target: string;
  type: 'control_flow' | 'data_flow';
  label?: string;
}

interface FlowchartData {
  steps: FlowchartStep[];
  connections: FlowchartConnection[];
}

export const FlowchartViewer: React.FC = () => {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // 状态管理
  const selectedTraceId = useAnalysisStore((state) => state.selectedTraceId);
  const analysisData = useAnalysisStore((state) => state.analysisData);
  const theme = useVisualizationStore((state) => state.theme);

  // 当前步骤（用于动画）
  const currentStep = useVisualizationStore((state) => state.currentStep);
  const animationState = useVisualizationStore((state) => state.animationState);

  useEffect(() => {
    if (!svgRef.current || !containerRef.current || !selectedTraceId) return;

    // 获取流程图数据
    const trace = analysisData?.execution_trace?.traceable_units?.find(
      (t) => t.id === selectedTraceId
    );

    if (!trace) return;

    const flowchartTrace = trace.traces?.find((t) => t.format === 'flowchart');
    if (!flowchartTrace) return;

    const data = flowchartTrace.data as unknown as FlowchartData;

    // 渲染流程图
    renderFlowchart(svgRef.current, containerRef.current, data, theme);
  }, [selectedTraceId, analysisData, theme]);

  // 更新动画状态
  useEffect(() => {
    if (!svgRef.current || animationState === 'idle') return;

    updateAnimation(svgRef.current, currentStep, animationState);
  }, [currentStep, animationState]);

  if (!selectedTraceId) {
    return (
      <div className="flowchart-viewer-empty">
        <p>请先选择一个执行轨迹</p>
      </div>
    );
  }

  return (
    <div className="flowchart-viewer" ref={containerRef}>
      <svg ref={svgRef} className="flowchart-svg"></svg>
    </div>
  );
};

// 渲染流程图
function renderFlowchart(
  svg: SVGSVGElement,
  container: HTMLDivElement,
  data: FlowchartData,
  theme: 'light' | 'dark'
) {
  const width = container.clientWidth;
  const height = container.clientHeight;

  // 清空 SVG
  d3.select(svg).selectAll('*').remove();

  // 创建 SVG 容器
  const svgSelection = d3
    .select(svg)
    .attr('width', width)
    .attr('height', height)
    .attr('viewBox', [0, 0, width, height]);

  // 创建分组
  const g = svgSelection
    .append('g')
    .attr('class', 'flowchart-container')
    .attr('transform', 'translate(50, 50)');

  // 缩放和拖拽
  const zoom = d3.zoom<SVGSVGElement, unknown>()
    .scaleExtent([0.5, 3])
    .on('zoom', (event) => {
      g.attr('transform', event.transform);
    });

  svgSelection.call(zoom as any);

  // 布局计算
  const layout = calculateLayout(data, width - 100, height - 100);

  // 绘制连接线
  const connections = g
    .selectAll('.connection')
    .data(data.connections)
    .join('g')
    .attr('class', 'connection');

  connections.each(function (d) {
    const source = layout.nodes.get(d.source);
    const target = layout.nodes.get(d.target);

    if (!source || !target) return;

    const path = generateConnectionPath(source, target);
    const connection = d3.select(this);

    // 绘制路径
    connection
      .append('path')
      .attr('d', path)
      .attr('class', `connection-path connection-path--${d.type}`)
      .attr('fill', 'none')
      .attr('stroke', d.type === 'data_flow' ? '#4CAF50' : '#2196F3')
      .attr('stroke-width', 2)
      .attr('marker-end', 'url(#arrowhead)');

    // 添加标签
    if (d.label) {
      const midPoint = getMidPoint(source, target);
      connection
        .append('text')
        .attr('x', midPoint.x)
        .attr('y', midPoint.y - 5)
        .attr('class', 'connection-label')
        .attr('text-anchor', 'middle')
        .text(d.label);
    }
  });

  // 定义箭头标记
  svgSelection
    .append('defs')
    .append('marker')
    .attr('id', 'arrowhead')
    .attr('viewBox', '0 0 10 10')
    .attr('refX', 8)
    .attr('refY', 5)
    .attr('markerWidth', 6)
    .attr('markerHeight', 6)
    .attr('orient', 'auto')
    .append('path')
    .attr('d', 'M 0 0 L 10 5 L 0 10 z')
    .attr('fill', theme === 'dark' ? '#fff' : '#333');

  // 绘制步骤节点
  const steps = g
    .selectAll('.step')
    .data(data.steps)
    .join('g')
    .attr('class', (d) => `step step--${d.type}`)
    .attr('transform', (d) => {
      const pos = layout.nodes.get(d.id);
      return pos ? `translate(${pos.x}, ${pos.y})` : '';
    })
    .attr('data-step-id', (d) => d.id);

  // 绘制节点形状
  steps.each(function (d) {
    const step = d3.select(this);
    const shape = getStepShape(d.type);

    step
      .append('path')
      .attr('d', shape.path)
      .attr('class', 'step-shape')
      .attr('fill', shape.color)
      .attr('stroke', theme === 'dark' ? '#fff' : '#333')
      .attr('stroke-width', 2);

    // 添加标签
    step
      .append('text')
      .attr('class', 'step-label')
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'central')
      .text(d.label);
  });

  // 添加交互
  steps
    .on('mouseenter', function () {
      d3.select(this).select('.step-shape').attr('opacity', 0.8);
    })
    .on('mouseleave', function () {
      d3.select(this).select('.step-shape').attr('opacity', 1);
    });
}

// 计算布局
function calculateLayout(
  data: FlowchartData,
  width: number,
  height: number
): { nodes: Map<string, { x: number; y: number }> } {
  const nodes = new Map<string, { x: number; y: number }>();

  // 简单的层级布局
  const levels = new Map<string, number>();
  const startNodes = data.steps.filter((s) => s.type === 'start');

  // BFS 计算层级
  const queue = [...startNodes];
  startNodes.forEach((s) => levels.set(s.id, 0));

  while (queue.length > 0) {
    const current = queue.shift()!;
    const currentLevel = levels.get(current.id)!;

    // 找到所有后继节点
    const outgoingConnections = data.connections.filter(
      (c) => c.source === current.id
    );

    outgoingConnections.forEach((conn) => {
      if (!levels.has(conn.target)) {
        levels.set(conn.target, currentLevel + 1);
        const targetStep = data.steps.find((s) => s.id === conn.target);
        if (targetStep) {
          queue.push(targetStep);
        }
      }
    });
  }

  // 计算每层的节点
  const levelGroups = new Map<number, string[]>();
  levels.forEach((level, nodeId) => {
    if (!levelGroups.has(level)) {
      levelGroups.set(level, []);
    }
    levelGroups.get(level)!.push(nodeId);
  });

  // 分配位置
  const levelWidth = width / (levelGroups.size + 1);

  levelGroups.forEach((nodeIds, level) => {
    const levelHeight = height / (nodeIds.length + 1);

    nodeIds.forEach((nodeId, index) => {
      nodes.set(nodeId, {
        x: levelWidth * (level + 1),
        y: levelHeight * (index + 1),
      });
    });
  });

  return { nodes };
}

// 生成连接路径
function generateConnectionPath(
  source: { x: number; y: number },
  target: { x: number; y: number }
): string {
  const dx = target.x - source.x;
  const dy = target.y - source.y;

  // 贝塞尔曲线
  const controlX = source.x + dx * 0.5;

  return `M ${source.x} ${source.y} Q ${controlX} ${source.y}, ${controlX} ${source.y + dy * 0.5} T ${target.x} ${target.y}`;
}

// 获取中点
function getMidPoint(
  source: { x: number; y: number },
  target: { x: number; y: number }
): { x: number; y: number } {
  return {
    x: (source.x + target.x) / 2,
    y: (source.y + target.y) / 2,
  };
}

// 获取步骤形状
function getStepShape(
  type: string
): { path: string; color: string } {
  const size = 80;
  const halfSize = size / 2;

  switch (type) {
    case 'start':
    case 'end':
      // 圆角矩形
      return {
        path: `M ${-halfSize} 0 A ${halfSize} ${halfSize / 2} 0 0 1 ${halfSize} 0 A ${halfSize} ${halfSize / 2} 0 0 1 ${-halfSize} 0`,
        color: type === 'start' ? '#4CAF50' : '#F44336',
      };

    case 'decision':
      // 菱形
      return {
        path: `M 0 ${-halfSize} L ${halfSize} 0 L 0 ${halfSize} L ${-halfSize} 0 Z`,
        color: '#FFC107',
      };

    case 'fork':
    case 'join':
      // 六边形
      return {
        path: `M ${-halfSize} ${-halfSize / 2} L ${-halfSize} ${halfSize / 2} L 0 ${halfSize} L ${halfSize} ${halfSize / 2} L ${halfSize} ${-halfSize / 2} L 0 ${-halfSize} Z`,
        color: type === 'fork' ? '#9C27B0' : '#673AB7',
      };

    case 'process':
    default:
      // 矩形
      return {
        path: `M ${-halfSize} ${-halfSize / 2} L ${halfSize} ${-halfSize / 2} L ${halfSize} ${halfSize / 2} L ${-halfSize} ${halfSize / 2} Z`,
        color: '#2196F3',
      };
  }
}

// 更新动画
function updateAnimation(
  svg: SVGSVGElement,
  currentStep: number,
  state: string
) {
  const svgSelection = d3.select(svg);

  // 高亮当前步骤
  svgSelection
    .selectAll('.step')
    .classed('step--active', (d: any, i) => i === currentStep);

  // 如果正在播放，添加脉冲动画
  if (state === 'playing') {
    svgSelection
      .selectAll('.step--active .step-shape')
      .transition()
      .duration(500)
      .attr('stroke-width', 4)
      .transition()
      .duration(500)
      .attr('stroke-width', 2);
  }
}
