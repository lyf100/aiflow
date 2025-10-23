/**
 * SequenceDiagram 组件
 *
 * 使用 D3.js 渲染 UML 时序图
 * 支持同步/异步消息、并发组可视化
 */

import { useEffect, useRef } from 'react';
import { select } from 'd3-selection';
import type { SequenceData } from '../../types/protocol';  // 🔧 修复: 使用type导入
import './SequenceDiagram.css';

interface SequenceDiagramProps {
  data: SequenceData;
  width?: number;
  height?: number;
}

export function SequenceDiagram({ data, width = 800, height = 600 }: SequenceDiagramProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || !data) {return;}

    // 清空之前的内容
    select(svgRef.current).selectAll('*').remove();

    renderSequenceDiagram(svgRef.current, data, width, height);
  }, [data, width, height]);

  return (
    <div className="sequence-diagram-container">
      <div className="diagram-header">
        <h4>📊 时序图</h4>
        <div className="legend">
          <div className="legend-item">
            <div className="legend-symbol sync-arrow"></div>
            <span>同步调用</span>
          </div>
          <div className="legend-item">
            <div className="legend-symbol async-arrow"></div>
            <span>异步调用</span>
          </div>
          <div className="legend-item">
            <div className="legend-symbol return-arrow"></div>
            <span>返回</span>
          </div>
        </div>
      </div>
      <svg ref={svgRef} className="sequence-diagram-svg"></svg>
    </div>
  );
}

// ============================================================================
// D3.js 渲染逻辑
// ============================================================================

function renderSequenceDiagram(
  svg: SVGSVGElement,
  data: SequenceData,
  width: number,
  height: number
) {
  const { participants, messages } = data;

  // 配置
  const margin = { top: 80, right: 40, bottom: 40, left: 40 };
  const participantWidth = 120;
  const participantHeight = 50;
  const messageSpacing = 60;
  const lifelineTopMargin = 30;

  // 计算布局
  const participantSpacing = (width - margin.left - margin.right) / participants.length;
  const sortedMessages = [...messages].sort((a, b) => a.order - b.order);

  // 创建 SVG 根元素
  const g = select(svg)
    .attr('width', width)
    .attr('height', Math.max(height, sortedMessages.length * messageSpacing + margin.top + margin.bottom + 100))
    .append('g')
    .attr('transform', `translate(${margin.left}, ${margin.top})`);

  // 1. 绘制参与者
  const participantData = participants.map((p, i) => ({
    ...p,
    x: i * participantSpacing + participantSpacing / 2,
    y: 0
  }));

  const participantGroups = g.selectAll('.participant')
    .data(participantData)
    .enter()
    .append('g')
    .attr('class', 'participant')
    .attr('transform', d => `translate(${d.x}, ${d.y})`);

  // 参与者矩形框
  participantGroups.append('rect')
    .attr('class', d => `participant-box ${d.type}`)
    .attr('x', -participantWidth / 2)
    .attr('y', 0)
    .attr('width', participantWidth)
    .attr('height', participantHeight)
    .attr('rx', 8);

  // 参与者名称
  participantGroups.append('text')
    .attr('class', 'participant-name')
    .attr('text-anchor', 'middle')
    .attr('x', 0)
    .attr('y', participantHeight / 2 + 5)
    .text(d => d.name);

  // 2. 绘制生命线
  const maxMessageY = sortedMessages.length * messageSpacing + lifelineTopMargin;

  participantGroups.append('line')
    .attr('class', 'lifeline')
    .attr('x1', 0)
    .attr('y1', participantHeight + lifelineTopMargin)
    .attr('x2', 0)
    .attr('y2', maxMessageY);

  // 3. 绘制消息
  const participantMap = new Map(participantData.map(p => [p.id, p]));

  sortedMessages.forEach((msg, index) => {
    const fromParticipant = participantMap.get(msg.from);
    const toParticipant = participantMap.get(msg.to);

    if (!fromParticipant || !toParticipant) {return;}

    const y = participantHeight + lifelineTopMargin + (index + 1) * messageSpacing;

    // 消息线
    const messageGroup = g.append('g')
      .attr('class', `message message-${msg.type}${msg.concurrent_group ? ' concurrent' : ''}`);

    // 根据消息类型选择样式
    const isAsync = msg.type === 'async';
    const isReturn = msg.type === 'return';
    const lineClass = isAsync ? 'async-line' : (isReturn ? 'return-line' : 'call-line');

    messageGroup.append('line')
      .attr('class', lineClass)
      .attr('x1', fromParticipant.x)
      .attr('y1', y)
      .attr('x2', toParticipant.x)
      .attr('y2', y)
      .attr('stroke-dasharray', isAsync || isReturn ? '5,5' : '0')
      .attr('marker-end', `url(#arrow-${msg.type})`);

    // 消息标签
    const labelX = (fromParticipant.x + toParticipant.x) / 2;
    const labelY = y - 5;

    messageGroup.append('text')
      .attr('class', 'message-label')
      .attr('text-anchor', 'middle')
      .attr('x', labelX)
      .attr('y', labelY)
      .text(msg.label);

    // 并发组标记
    if (msg.concurrent_group) {
      messageGroup.append('text')
        .attr('class', 'concurrent-badge')
        .attr('text-anchor', 'middle')
        .attr('x', labelX)
        .attr('y', y + 15)
        .text(`⚡ 并发组 ${msg.concurrent_group}`);
    }
  });

  // 4. 定义箭头标记
  const defs = select(svg).append('defs');

  // 同步调用箭头 (实心)
  defs.append('marker')
    .attr('id', 'arrow-call')
    .attr('viewBox', '0 0 10 10')
    .attr('refX', 9)
    .attr('refY', 5)
    .attr('markerWidth', 6)
    .attr('markerHeight', 6)
    .attr('orient', 'auto')
    .append('path')
    .attr('d', 'M 0 0 L 10 5 L 0 10 z')
    .attr('fill', '#3b82f6');

  // 异步调用箭头 (实心，不同颜色)
  defs.append('marker')
    .attr('id', 'arrow-async')
    .attr('viewBox', '0 0 10 10')
    .attr('refX', 9)
    .attr('refY', 5)
    .attr('markerWidth', 6)
    .attr('markerHeight', 6)
    .attr('orient', 'auto')
    .append('path')
    .attr('d', 'M 0 0 L 10 5 L 0 10 z')
    .attr('fill', '#10b981');

  // 返回箭头 (空心)
  defs.append('marker')
    .attr('id', 'arrow-return')
    .attr('viewBox', '0 0 10 10')
    .attr('refX', 9)
    .attr('refY', 5)
    .attr('markerWidth', 6)
    .attr('markerHeight', 6)
    .attr('orient', 'auto')
    .append('path')
    .attr('d', 'M 0 0 L 10 5 L 0 10 z')
    .attr('fill', 'none')
    .attr('stroke', '#94a3b8')
    .attr('stroke-width', 1.5);

  // create 和 destroy 箭头
  defs.append('marker')
    .attr('id', 'arrow-create')
    .attr('viewBox', '0 0 10 10')
    .attr('refX', 9)
    .attr('refY', 5)
    .attr('markerWidth', 6)
    .attr('markerHeight', 6)
    .attr('orient', 'auto')
    .append('path')
    .attr('d', 'M 0 0 L 10 5 L 0 10 z')
    .attr('fill', '#8b5cf6');

  defs.append('marker')
    .attr('id', 'arrow-destroy')
    .attr('viewBox', '0 0 10 10')
    .attr('refX', 9)
    .attr('refY', 5)
    .attr('markerWidth', 6)
    .attr('markerHeight', 6)
    .attr('orient', 'auto')
    .append('path')
    .attr('d', 'M 0 0 L 10 5 L 0 10')
    .attr('fill', 'none')
    .attr('stroke', '#ef4444')
    .attr('stroke-width', 2);
}
