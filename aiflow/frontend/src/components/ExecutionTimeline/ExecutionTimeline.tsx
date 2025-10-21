import { useEffect, useRef } from 'react';
import { select } from 'd3-selection';
import { scaleLinear } from 'd3-scale';
import 'd3-transition'; // 添加transition支持
import './ExecutionTimeline.css';

interface TimelineStep {
  id: string;
  description: string;
  index: number;
  type: string;
}

interface ExecutionTimelineProps {
  steps: TimelineStep[];
  currentStepIndex: number;
  onStepClick?: (index: number) => void;
}

export function ExecutionTimeline({ steps, currentStepIndex, onStepClick }: ExecutionTimelineProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || steps.length === 0) {return;}

    // 清空现有内容
    select(svgRef.current).selectAll('*').remove();

    // 设置尺寸和边距
    const margin = { top: 20, right: 20, bottom: 30, left: 50 };
    const width = svgRef.current.clientWidth - margin.left - margin.right;
    const height = 100;

    const svg = select(svgRef.current)
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // X轴比例尺 - 基于步骤索引
    const xScale = scaleLinear()
      .domain([0, steps.length - 1])
      .range([0, width]);

    // 绘制时间轴线
    svg.append('line')
      .attr('x1', 0)
      .attr('y1', height / 2)
      .attr('x2', width)
      .attr('y2', height / 2)
      .attr('stroke', 'rgba(255, 255, 255, 0.3)')
      .attr('stroke-width', 2);

    // 绘制步骤节点
    const nodes = svg.selectAll('.timeline-node')
      .data(steps)
      .enter()
      .append('g')
      .attr('class', 'timeline-node')
      .attr('transform', (_d, i) => `translate(${xScale(i)},${height / 2})`)
      .style('cursor', 'pointer')
      .on('click', (_event, d) => {
        onStepClick?.(d.index);
      });

    // 节点圆圈
    nodes.append('circle')
      .attr('r', 8)
      .attr('fill', (_d, i) => {
        if (i === currentStepIndex) {return '#667eea';}
        if (i < currentStepIndex) {return '#48bb78';}
        return 'rgba(255, 255, 255, 0.3)';
      })
      .attr('stroke', (_d, i) => {
        if (i === currentStepIndex) {return '#764ba2';}
        return 'transparent';
      })
      .attr('stroke-width', 3)
      .transition()
      .duration(300)
      .attr('r', (_d, i) => i === currentStepIndex ? 12 : 8);

    // 节点标签
    nodes.append('text')
      .attr('y', -15)
      .attr('text-anchor', 'middle')
      .attr('fill', 'rgba(255, 255, 255, 0.9)')
      .attr('font-size', '12px')
      .text((_d, i) => `Step ${i + 1}`);

    // 当前步骤高亮
    if (currentStepIndex >= 0 && currentStepIndex < steps.length) {
      svg.append('line')
        .attr('x1', xScale(currentStepIndex))
        .attr('y1', 0)
        .attr('x2', xScale(currentStepIndex))
        .attr('y2', height)
        .attr('stroke', '#667eea')
        .attr('stroke-width', 2)
        .attr('stroke-dasharray', '5,5')
        .attr('opacity', 0.5);
    }

  }, [steps, currentStepIndex, onStepClick]);

  return (
    <div className="execution-timeline-container">
      <div className="timeline-header">
        <h4>📈 执行时间轴</h4>
        <span className="timeline-progress">
          {currentStepIndex + 1} / {steps.length}
        </span>
      </div>
      <svg ref={svgRef} className="timeline-svg"></svg>
    </div>
  );
}
