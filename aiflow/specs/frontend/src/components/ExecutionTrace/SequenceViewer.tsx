/**
 * Sequence Viewer - D3.js 序列图可视化组件
 *
 * 使用 D3.js 渲染执行轨迹的序列图格式。
 * 展示不同参与者（组件、模块）之间的消息传递和方法调用。
 */

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { useAnalysisStore } from '../../stores/analysisStore';
import { useVisualizationStore } from '../../stores/visualizationStore';
import './SequenceViewer.css';

interface SequenceParticipant {
  id: string;
  name: string;
  type: 'component' | 'module' | 'service' | 'external';
}

interface SequenceMessage {
  id: string;
  from: string; // participant id
  to: string; // participant id
  type: 'call' | 'return' | 'async' | 'create' | 'destroy';
  label: string;
  activationStart?: boolean; // 开始激活
  activationEnd?: boolean; // 结束激活
}

interface SequenceData {
  participants: SequenceParticipant[];
  messages: SequenceMessage[];
}

export const SequenceViewer: React.FC = () => {
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

    // 获取序列图数据
    const trace = analysisData?.execution_trace?.traceable_units?.find(
      (t) => t.id === selectedTraceId
    );

    if (!trace) return;

    const sequenceTrace = trace.traces?.find((t) => t.format === 'sequence');
    if (!sequenceTrace) return;

    const data = sequenceTrace.data as unknown as SequenceData;

    // 渲染序列图
    renderSequence(svgRef.current, containerRef.current, data, theme);
  }, [selectedTraceId, analysisData, theme]);

  // 更新动画状态
  useEffect(() => {
    if (!svgRef.current || animationState === 'idle') return;

    updateAnimation(svgRef.current, currentStep, animationState);
  }, [currentStep, animationState]);

  if (!selectedTraceId) {
    return (
      <div className="sequence-viewer-empty">
        <p>请先选择一个执行轨迹</p>
      </div>
    );
  }

  return (
    <div className="sequence-viewer" ref={containerRef}>
      <svg ref={svgRef} className="sequence-svg"></svg>
    </div>
  );
};

// 渲染序列图
function renderSequence(
  svg: SVGSVGElement,
  container: HTMLDivElement,
  data: SequenceData,
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
    .attr('class', 'sequence-container')
    .attr('transform', 'translate(50, 50)');

  // 缩放和拖拽
  const zoom = d3.zoom<SVGSVGElement, unknown>()
    .scaleExtent([0.5, 3])
    .on('zoom', (event) => {
      g.attr('transform', event.transform);
    });

  svgSelection.call(zoom as any);

  // 布局计算
  const layout = calculateSequenceLayout(data, width - 100, height - 100);

  // 绘制参与者头部
  const participantHeaders = g
    .selectAll('.participant-header')
    .data(data.participants)
    .join('g')
    .attr('class', 'participant-header')
    .attr('transform', (d) => {
      const pos = layout.participants.get(d.id);
      return pos ? `translate(${pos.x}, 0)` : '';
    });

  participantHeaders
    .append('rect')
    .attr('x', -60)
    .attr('y', 0)
    .attr('width', 120)
    .attr('height', 50)
    .attr('class', (d) => `participant-box participant-box--${d.type}`)
    .attr('fill', (d) => getParticipantColor(d.type))
    .attr('stroke', theme === 'dark' ? '#fff' : '#333')
    .attr('stroke-width', 2)
    .attr('rx', 5);

  participantHeaders
    .append('text')
    .attr('class', 'participant-name')
    .attr('text-anchor', 'middle')
    .attr('dominant-baseline', 'central')
    .attr('y', 25)
    .text((d) => d.name);

  // 绘制生命线（虚线）
  const lifelines = g
    .selectAll('.lifeline')
    .data(data.participants)
    .join('line')
    .attr('class', 'lifeline')
    .attr('x1', (d) => layout.participants.get(d.id)?.x || 0)
    .attr('y1', 60)
    .attr('x2', (d) => layout.participants.get(d.id)?.x || 0)
    .attr('y2', layout.maxY)
    .attr('stroke', theme === 'dark' ? '#555' : '#ccc')
    .attr('stroke-width', 2)
    .attr('stroke-dasharray', '5,5');

  // 绘制激活框（activation boxes）
  const activations = g
    .selectAll('.activation')
    .data(layout.activations)
    .join('rect')
    .attr('class', 'activation')
    .attr('x', (d) => (layout.participants.get(d.participantId)?.x || 0) - 8)
    .attr('y', (d) => d.startY)
    .attr('width', 16)
    .attr('height', (d) => d.endY - d.startY)
    .attr('fill', theme === 'dark' ? '#4A5568' : '#E2E8F0')
    .attr('stroke', theme === 'dark' ? '#718096' : '#CBD5E0')
    .attr('stroke-width', 1);

  // 定义箭头标记
  const defs = svgSelection.append('defs');

  // 实线箭头（调用）
  defs.append('marker')
    .attr('id', 'arrowhead-call')
    .attr('viewBox', '0 0 10 10')
    .attr('refX', 10)
    .attr('refY', 5)
    .attr('markerWidth', 6)
    .attr('markerHeight', 6)
    .attr('orient', 'auto')
    .append('path')
    .attr('d', 'M 0 0 L 10 5 L 0 10 z')
    .attr('fill', '#2196F3');

  // 虚线箭头（返回）
  defs.append('marker')
    .attr('id', 'arrowhead-return')
    .attr('viewBox', '0 0 10 10')
    .attr('refX', 10)
    .attr('refY', 5)
    .attr('markerWidth', 6)
    .attr('markerHeight', 6)
    .attr('orient', 'auto')
    .append('path')
    .attr('d', 'M 0 0 L 10 5 L 0 10 z')
    .attr('fill', '#666');

  // 绘制消息（箭头）
  const messages = g
    .selectAll('.message')
    .data(data.messages)
    .join('g')
    .attr('class', 'message')
    .attr('data-message-id', (d) => d.id);

  messages.each(function (d, i) {
    const message = d3.select(this);
    const fromPos = layout.participants.get(d.from);
    const toPos = layout.participants.get(d.to);

    if (!fromPos || !toPos) return;

    const y = 80 + i * 60;
    const isSelfCall = d.from === d.to;

    if (isSelfCall) {
      // 自调用（弧形）
      const arcWidth = 40;
      const arcHeight = 30;

      message
        .append('path')
        .attr('class', `message-line message-line--${d.type}`)
        .attr('d', `M ${fromPos.x} ${y}
                    L ${fromPos.x + arcWidth} ${y}
                    L ${fromPos.x + arcWidth} ${y + arcHeight}
                    L ${fromPos.x} ${y + arcHeight}`)
        .attr('fill', 'none')
        .attr('stroke', getMessageColor(d.type))
        .attr('stroke-width', 2)
        .attr('stroke-dasharray', d.type === 'return' ? '5,5' : '0')
        .attr('marker-end', `url(#arrowhead-${d.type === 'return' ? 'return' : 'call'})`);

      // 标签
      message
        .append('text')
        .attr('x', fromPos.x + arcWidth + 5)
        .attr('y', y + arcHeight / 2)
        .attr('class', 'message-label')
        .attr('text-anchor', 'start')
        .text(d.label);
    } else {
      // 普通消息（水平线）
      const isReverse = fromPos.x > toPos.x;

      message
        .append('line')
        .attr('class', `message-line message-line--${d.type}`)
        .attr('x1', fromPos.x)
        .attr('y1', y)
        .attr('x2', toPos.x)
        .attr('y2', y)
        .attr('stroke', getMessageColor(d.type))
        .attr('stroke-width', 2)
        .attr('stroke-dasharray', d.type === 'return' ? '5,5' : '0')
        .attr('marker-end', `url(#arrowhead-${d.type === 'return' ? 'return' : 'call'})`);

      // 标签（放在线的上方）
      message
        .append('text')
        .attr('x', (fromPos.x + toPos.x) / 2)
        .attr('y', y - 5)
        .attr('class', 'message-label')
        .attr('text-anchor', 'middle')
        .text(d.label);
    }
  });

  // 添加交互
  messages
    .on('mouseenter', function () {
      d3.select(this).select('.message-line').attr('stroke-width', 3);
    })
    .on('mouseleave', function () {
      d3.select(this).select('.message-line').attr('stroke-width', 2);
    });
}

// 计算序列图布局
function calculateSequenceLayout(
  data: SequenceData,
  width: number,
  height: number
): {
  participants: Map<string, { x: number }>;
  activations: Array<{ participantId: string; startY: number; endY: number }>;
  maxY: number;
} {
  const participants = new Map<string, { x: number }>();

  // 水平分布参与者
  const spacing = width / (data.participants.length + 1);
  data.participants.forEach((p, i) => {
    participants.set(p.id, { x: spacing * (i + 1) });
  });

  // 计算激活框
  const activations: Array<{ participantId: string; startY: number; endY: number }> = [];
  const activeStack = new Map<string, number>(); // participantId -> startY

  data.messages.forEach((msg, i) => {
    const y = 80 + i * 60;

    if (msg.activationStart) {
      activeStack.set(msg.to, y);
    }

    if (msg.activationEnd) {
      const startY = activeStack.get(msg.from);
      if (startY !== undefined) {
        activations.push({
          participantId: msg.from,
          startY,
          endY: y,
        });
        activeStack.delete(msg.from);
      }
    }
  });

  // 计算最大 Y 坐标
  const maxY = 80 + data.messages.length * 60 + 40;

  return { participants, activations, maxY };
}

// 获取参与者颜色
function getParticipantColor(type: string): string {
  switch (type) {
    case 'component':
      return '#4ECDC4';
    case 'module':
      return '#667eea';
    case 'service':
      return '#FFE66D';
    case 'external':
      return '#FF6B6B';
    default:
      return '#95A5A6';
  }
}

// 获取消息颜色
function getMessageColor(type: string): string {
  switch (type) {
    case 'call':
      return '#2196F3';
    case 'return':
      return '#666666';
    case 'async':
      return '#9C27B0';
    case 'create':
      return '#4CAF50';
    case 'destroy':
      return '#F44336';
    default:
      return '#333333';
  }
}

// 更新动画
function updateAnimation(
  svg: SVGSVGElement,
  currentStep: number,
  state: string
) {
  const svgSelection = d3.select(svg);

  // 高亮当前消息
  svgSelection
    .selectAll('.message')
    .classed('message--active', (d: any, i) => i === currentStep);

  // 如果正在播放，添加脉冲动画
  if (state === 'playing') {
    svgSelection
      .selectAll('.message--active .message-line')
      .transition()
      .duration(500)
      .attr('stroke-width', 4)
      .transition()
      .duration(500)
      .attr('stroke-width', 2);
  }
}
