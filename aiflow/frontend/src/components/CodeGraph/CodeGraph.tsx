import { useEffect, useRef, useState } from 'react';
import cytoscape, { Core, ElementDefinition } from 'cytoscape';
import dagre from 'cytoscape-dagre';
import type { CodeNode, CodeEdge } from '../../types/protocol';
import './CodeGraph.css';

// 注册 dagre 布局
cytoscape.use(dagre);

interface CodeGraphProps {
  nodes: CodeNode[];
  edges: CodeEdge[];
  onNodeClick?: (nodeId: string) => void;
}

export function CodeGraph({ nodes, edges, onNodeClick }: CodeGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);

  useEffect(() => {
    if (!containerRef.current || nodes.length === 0) return;

    // 转换数据为 Cytoscape 格式
    const elements: ElementDefinition[] = [
      ...nodes.map(node => ({
        data: {
          id: node.id,
          label: node.name,
          type: node.type,
          stereotype: node.stereotype,
          parent: node.parent_class_id || undefined,
        },
      })),
      ...edges.map(edge => ({
        data: {
          id: edge.id,
          source: edge.source,
          target: edge.target,
          label: edge.type,
        },
      })),
    ];

    // 初始化 Cytoscape
    const cy = cytoscape({
      container: containerRef.current,
      elements,
      style: [
        {
          selector: 'node',
          style: {
            'label': 'data(label)',
            'text-valign': 'center',
            'text-halign': 'center',
            'background-color': '#667eea',
            'color': '#fff',
            'font-size': '18px',
            'font-weight': '600',
            'width': '120px',
            'height': '120px',
            'text-wrap': 'wrap',
            'text-max-width': '140px',
            'shape': 'roundrectangle',
          },
        },
        {
          selector: 'node[stereotype="system"]',
          style: {
            'background-color': '#667eea',
            'width': '150px',
            'height': '150px',
            'font-size': '22px',
            'font-weight': 'bold',
          },
        },
        {
          selector: 'node[stereotype="module"]',
          style: {
            'background-color': '#764ba2',
            'width': '130px',
            'height': '130px',
            'font-size': '20px',
          },
        },
        {
          selector: 'node[stereotype="component"]',
          style: {
            'background-color': '#f093fb',
            'width': '120px',
            'height': '120px',
            'font-size': '18px',
          },
        },
        {
          selector: 'node[stereotype="function"]',
          style: {
            'background-color': '#4facfe',
            'width': '100px',
            'height': '100px',
            'font-size': '16px',
          },
        },
        {
          selector: 'node:selected',
          style: {
            'border-width': '3px',
            'border-color': '#ffd700',
          },
        },
        {
          selector: 'edge',
          style: {
            'width': 3,
            'line-color': '#999',
            'target-arrow-color': '#999',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'label': 'data(label)',
            'font-size': '14px',
            'font-weight': '600',
            'color': '#333',
            'text-rotation': 'autorotate',
            'text-margin-y': -15,
            'text-background-color': '#fff',
            'text-background-opacity': 0.8,
            'text-background-padding': '4px',
          },
        },
        {
          selector: 'edge[label="calls"]',
          style: {
            'line-color': '#00d4ff',
            'target-arrow-color': '#00d4ff',
          },
        },
        {
          selector: 'edge[label="contains"]',
          style: {
            'line-color': '#a8a8a8',
            'target-arrow-color': '#a8a8a8',
            'line-style': 'dashed',
          },
        },
      ],
      layout: {
        name: 'dagre',
        rankDir: 'LR',
        nodeSep: 80,
        rankSep: 150,
        padding: 50,
      },
      minZoom: 0.1,
      maxZoom: 3,
      wheelSensitivity: 0.2,
    });

    // 节点点击事件
    cy.on('tap', 'node', (evt) => {
      const node = evt.target;
      const nodeId = node.id();
      setSelectedNode(nodeId);
      onNodeClick?.(nodeId);
    });

    // 背景点击取消选择
    cy.on('tap', (evt) => {
      if (evt.target === cy) {
        setSelectedNode(null);
      }
    });

    cyRef.current = cy;

    // 初始化时自动适应画布，显示所有内容
    setTimeout(() => {
      cy.fit(undefined, 50);
    }, 100);

    return () => {
      cy.destroy();
    };
  }, [nodes, edges, onNodeClick]);

  const handleFit = () => {
    cyRef.current?.fit(undefined, 50);
  };

  const handleCenter = () => {
    cyRef.current?.center();
  };

  const handleZoomIn = () => {
    cyRef.current?.zoom({
      level: (cyRef.current.zoom() || 1) * 1.2,
      renderedPosition: {
        x: containerRef.current!.offsetWidth / 2,
        y: containerRef.current!.offsetHeight / 2,
      },
    });
  };

  const handleZoomOut = () => {
    cyRef.current?.zoom({
      level: (cyRef.current.zoom() || 1) * 0.8,
      renderedPosition: {
        x: containerRef.current!.offsetWidth / 2,
        y: containerRef.current!.offsetHeight / 2,
      },
    });
  };

  return (
    <div className="code-graph-container">
      <div className="code-graph-controls">
        <button onClick={handleFit} title="适应画布">
          📐 适应
        </button>
        <button onClick={handleCenter} title="居中">
          🎯 居中
        </button>
        <button onClick={handleZoomIn} title="放大">
          ➕ 放大
        </button>
        <button onClick={handleZoomOut} title="缩小">
          ➖ 缩小
        </button>
        {selectedNode && (
          <span className="selected-info">
            已选择: {nodes.find(n => n.id === selectedNode)?.name}
          </span>
        )}
      </div>
      <div ref={containerRef} className="code-graph-canvas" />
    </div>
  );
}
