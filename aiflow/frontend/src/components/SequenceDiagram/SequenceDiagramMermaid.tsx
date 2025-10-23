/**
 * SequenceDiagramMermaid 组件 - Mermaid实现版本
 *
 * 使用Mermaid自动渲染UML序列图
 * 对比D3手动实现：248行 → 60行 (-76% 代码)
 */

import { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';
import type { SequenceData } from '../../types/protocol';
import './SequenceDiagram.css';

interface SequenceDiagramMermaidProps {
  data: SequenceData;
  width?: number;
  height?: number;
}

export function SequenceDiagramMermaid({ data, height = 600 }: SequenceDiagramMermaidProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // 初始化Mermaid配置
    mermaid.initialize({
      startOnLoad: false,
      theme: 'dark',
      themeVariables: {
        primaryColor: '#667eea',
        primaryTextColor: '#fff',
        primaryBorderColor: '#764ba2',
        lineColor: '#94a3b8',
        secondaryColor: '#10b981',
        tertiaryColor: '#ef4444',
        background: '#1e1e2e',
        mainBkg: '#2d2d44',
        sequenceNumberColor: 'white',
      },
      sequence: {
        diagramMarginX: 50,
        diagramMarginY: 10,
        actorMargin: 80,
        width: 150,
        height: 65,
        boxMargin: 10,
        messageMargin: 35,
        mirrorActors: true,
        bottomMarginAdj: 1,
        useMaxWidth: true,
        rightAngles: false,
        showSequenceNumbers: false,
      },
    });
  }, []);

  useEffect(() => {
    if (!containerRef.current || !data) {
      return;
    }

    try {
      const { participants, messages } = data;

      // 生成Mermaid sequenceDiagram语法
      const mermaidCode = generateMermaidSequence(participants, messages);

      // 渲染Mermaid图表
      const uniqueId = `mermaid-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

      mermaid.render(uniqueId, mermaidCode).then(({ svg }) => {
        if (containerRef.current) {
          containerRef.current.innerHTML = svg;
          setError(null);
        }
      }).catch((err) => {
        console.error('Mermaid rendering error:', err);
        setError(`渲染失败: ${err.message}`);
      });

    } catch (err: any) {
      console.error('Mermaid generation error:', err);
      setError(`生成失败: ${err.message}`);
    }
  }, [data]);

  return (
    <div className="sequence-diagram-container">
      <div className="diagram-header">
        <h4>📊 时序图 (Mermaid版)</h4>
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
      {error ? (
        <div className="error-message" style={{ padding: '20px', color: '#ef4444' }}>
          {error}
        </div>
      ) : (
        <div
          ref={containerRef}
          className="sequence-diagram-mermaid"
          style={{
            width: '100%',
            minHeight: `${height}px`,
            overflow: 'auto'
          }}
        ></div>
      )}
    </div>
  );
}

// ============================================================================
// Mermaid语法生成器
// ============================================================================

function generateMermaidSequence(
  participants: SequenceData['participants'],
  messages: SequenceData['messages']
): string {
  const lines: string[] = ['sequenceDiagram'];

  // 1. 声明参与者
  participants.forEach(p => {
    const actorType = p.type === 'actor' ? 'actor' : 'participant';
    lines.push(`    ${actorType} ${sanitizeMermaidId(p.id)} as ${sanitizeMermaidLabel(p.name)}`);
  });

  lines.push(''); // 空行分隔

  // 2. 生成消息序列
  const sortedMessages = [...messages].sort((a, b) => a.order - b.order);

  sortedMessages.forEach(msg => {
    const from = sanitizeMermaidId(msg.from);
    const to = sanitizeMermaidId(msg.to);
    const label = sanitizeMermaidLabel(msg.label);

    // 根据消息类型选择箭头样式
    const arrow = getArrowStyle(msg.type);

    // 并发组支持
    if (msg.concurrent_group) {
      lines.push(`    Note over ${from},${to}: ⚡ 并发组 ${msg.concurrent_group}`);
    }

    lines.push(`    ${from}${arrow}${to}: ${label}`);
  });

  return lines.join('\n');
}

/**
 * 获取Mermaid箭头样式
 */
function getArrowStyle(type: SequenceData['messages'][0]['type']): string {
  switch (type) {
    case 'call':
      return '->>';      // 实心箭头（同步调用）
    case 'async':
      return '-)>>';     // 开放箭头（异步调用）
    case 'return':
      return '-->>'; // 虚线箭头（返回）
    case 'create':
      return '-->>';     // 虚线创建
    case 'destroy':
      return '-x';       // 销毁标记
    default:
      return '->>';
  }
}

/**
 * 清理Mermaid ID（移除特殊字符）
 */
function sanitizeMermaidId(id: string): string {
  return id.replace(/[^a-zA-Z0-9_]/g, '_');
}

/**
 * 清理Mermaid标签（转义特殊字符）
 */
function sanitizeMermaidLabel(label: string): string {
  // 移除可能破坏Mermaid语法的字符
  return label
    .replace(/"/g, "'")
    .replace(/\n/g, ' ')
    .replace(/[<>]/g, '')
    .trim();
}
