/**
 * Code Structure Graph - Cytoscape.js 代码结构图组件
 *
 * 使用 Cytoscape.js 渲染可交互的代码结构图。
 * 这是 AIFlow 可视化的核心组件。
 */

import React, { useEffect, useRef, useState } from 'react';
import cytoscape, { Core, NodeSingular, EdgeSingular } from 'cytoscape';
import dagre from 'cytoscape-dagre';
import { useAnalysisStore } from '../../stores/analysisStore';
import { useVisualizationStore } from '../../stores/visualizationStore';
import type { CodeNode, CodeEdge } from '../../types/protocol';
import './CodeStructureGraph.css';

// 注册布局算法
cytoscape.use(dagre);

interface CodeStructureGraphProps {
  width?: string | number;
  height?: string | number;
}

export const CodeStructureGraph: React.FC<CodeStructureGraphProps> = ({
  width = '100%',
  height = '100%',
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);

  // 状态管理
  const analysisData = useAnalysisStore((state) => state.analysisData);
  const selectedNodeId = useAnalysisStore((state) => state.selectedNodeId);
  const selectNode = useAnalysisStore((state) => state.selectNode);
  const highlightedNodeIds = useAnalysisStore((state) => state.highlightedNodeIds);

  const layoutType = useVisualizationStore((state) => state.layoutType);
  const theme = useVisualizationStore((state) => state.theme);

  const [isInitialized, setIsInitialized] = useState(false);

  // 初始化 Cytoscape
  useEffect(() => {
    if (!containerRef.current || !analysisData) return;

    const cy = cytoscape({
      container: containerRef.current,
      elements: [],
      style: getCytoscapeStyles(theme),
      layout: {
        name: 'preset',
      },
      minZoom: 0.1,
      maxZoom: 5,
      wheelSensitivity: 0.2,
    });

    cyRef.current = cy;
    setIsInitialized(true);

    // 清理函数
    return () => {
      cy.destroy();
      cyRef.current = null;
    };
  }, [containerRef.current]);

  // 加载数据
  useEffect(() => {
    if (!cyRef.current || !analysisData || !isInitialized) return;

    const cy = cyRef.current;

    // 清空现有元素
    cy.elements().remove();

    // 添加节点
    const nodes = analysisData.code_structure?.nodes || [];
    nodes.forEach((node) => {
      cy.add({
        group: 'nodes',
        data: {
          id: node.id,
          label: node.label,
          stereotype: node.stereotype,
          parent: node.parent || undefined,
          ...node,
        },
      });
    });

    // 添加边
    const edges = analysisData.code_structure?.edges || [];
    edges.forEach((edge) => {
      cy.add({
        group: 'edges',
        data: {
          id: edge.id,
          source: edge.source,
          target: edge.target,
          relationship: edge.relationship,
          label: edge.label || '',
          ...edge,
        },
      });
    });

    // 应用布局
    applyLayout(cy, layoutType);

    // 绑定事件
    bindEvents(cy);

  }, [analysisData, isInitialized]);

  // 监听布局变化
  useEffect(() => {
    if (!cyRef.current) return;
    applyLayout(cyRef.current, layoutType);
  }, [layoutType]);

  // 监听主题变化
  useEffect(() => {
    if (!cyRef.current) return;
    cyRef.current.style(getCytoscapeStyles(theme));
  }, [theme]);

  // 监听选中节点变化
  useEffect(() => {
    if (!cyRef.current) return;

    const cy = cyRef.current;

    // 清除所有选中状态
    cy.nodes().removeClass('selected');

    // 添加选中状态
    if (selectedNodeId) {
      const node = cy.getElementById(selectedNodeId);
      node.addClass('selected');

      // 平滑移动到选中节点
      cy.animate({
        center: { eles: node },
        zoom: 1.5,
      }, {
        duration: 300,
      });
    }
  }, [selectedNodeId]);

  // 监听高亮节点变化
  useEffect(() => {
    if (!cyRef.current) return;

    const cy = cyRef.current;

    // 清除所有高亮状态
    cy.nodes().removeClass('highlighted');

    // 添加高亮状态
    highlightedNodeIds.forEach((nodeId) => {
      cy.getElementById(nodeId).addClass('highlighted');
    });
  }, [highlightedNodeIds]);

  // 绑定事件处理
  const bindEvents = (cy: Core) => {
    // 节点点击事件
    cy.on('tap', 'node', (event) => {
      const node = event.target;
      const nodeId = node.data('id');
      selectNode(nodeId);
    });

    // 背景点击事件（取消选择）
    cy.on('tap', (event) => {
      if (event.target === cy) {
        selectNode(null);
      }
    });

    // 节点双击展开/折叠
    cy.on('dbltap', 'node', (event) => {
      const node = event.target;
      toggleNodeExpansion(node);
    });

    // 节点悬停事件
    cy.on('mouseover', 'node', (event) => {
      const node = event.target;
      node.addClass('hover');
      document.body.style.cursor = 'pointer';
    });

    cy.on('mouseout', 'node', (event) => {
      const node = event.target;
      node.removeClass('hover');
      document.body.style.cursor = 'default';
    });
  };

  // 应用布局
  const applyLayout = (cy: Core, layout: string) => {
    const layoutOptions = getLayoutOptions(layout);
    cy.layout(layoutOptions).run();
  };

  // 切换节点展开/折叠
  const toggleNodeExpansion = (node: NodeSingular) => {
    const children = node.children();

    if (children.length > 0) {
      const isHidden = children.first().style('display') === 'none';

      if (isHidden) {
        // 展开
        children.style('display', 'element');
        node.removeClass('collapsed');
      } else {
        // 折叠
        children.style('display', 'none');
        node.addClass('collapsed');
      }

      // 重新应用布局
      applyLayout(cyRef.current!, layoutType);
    }
  };

  return (
    <div
      className="code-structure-graph-container"
      style={{ width, height }}
    >
      <div
        ref={containerRef}
        className="code-structure-graph"
        style={{ width: '100%', height: '100%' }}
      />

      {/* 控制面板 */}
      <div className="graph-controls">
        <button onClick={() => cyRef.current?.fit()}>
          适应窗口
        </button>
        <button onClick={() => cyRef.current?.center()}>
          居中
        </button>
        <button onClick={() => cyRef.current?.zoom(cyRef.current.zoom() * 1.2)}>
          放大
        </button>
        <button onClick={() => cyRef.current?.zoom(cyRef.current.zoom() / 1.2)}>
          缩小
        </button>
      </div>

      {/* 图例 */}
      <div className="graph-legend">
        <div className="legend-item">
          <span className="legend-color system"></span>
          <span>系统</span>
        </div>
        <div className="legend-item">
          <span className="legend-color module"></span>
          <span>模块</span>
        </div>
        <div className="legend-item">
          <span className="legend-color class"></span>
          <span>类</span>
        </div>
        <div className="legend-item">
          <span className="legend-color function"></span>
          <span>函数</span>
        </div>
      </div>
    </div>
  );
};

// Cytoscape 样式配置
function getCytoscapeStyles(theme: 'light' | 'dark') {
  const isDark = theme === 'dark';

  return [
    {
      selector: 'node',
      style: {
        'label': 'data(label)',
        'text-valign': 'center',
        'text-halign': 'center',
        'font-size': '12px',
        'font-family': 'Arial, sans-serif',
        'color': isDark ? '#fff' : '#000',
        'background-color': '#6FB1FC',
        'border-width': 2,
        'border-color': '#4F8FC8',
        'width': 60,
        'height': 60,
        'text-wrap': 'wrap',
        'text-max-width': '100px',
      },
    },
    {
      selector: 'node[stereotype="system"]',
      style: {
        'background-color': '#FF6B6B',
        'border-color': '#C92A2A',
        'shape': 'rectangle',
      },
    },
    {
      selector: 'node[stereotype="module"]',
      style: {
        'background-color': '#4ECDC4',
        'border-color': '#2E8B89',
        'shape': 'roundrectangle',
      },
    },
    {
      selector: 'node[stereotype="class"]',
      style: {
        'background-color': '#FFE66D',
        'border-color': '#D4B942',
        'shape': 'ellipse',
      },
    },
    {
      selector: 'node[stereotype="function"]',
      style: {
        'background-color': '#A8E6CF',
        'border-color': '#7FB3A1',
        'shape': 'diamond',
      },
    },
    {
      selector: 'node.selected',
      style: {
        'border-width': 4,
        'border-color': '#FF4081',
        'overlay-opacity': 0.2,
        'overlay-color': '#FF4081',
      },
    },
    {
      selector: 'node.highlighted',
      style: {
        'border-width': 3,
        'border-color': '#FFA726',
      },
    },
    {
      selector: 'node.hover',
      style: {
        'overlay-opacity': 0.1,
        'overlay-color': '#333',
      },
    },
    {
      selector: 'node.collapsed',
      style: {
        'border-style': 'dashed',
      },
    },
    {
      selector: 'edge',
      style: {
        'width': 2,
        'line-color': isDark ? '#888' : '#ccc',
        'target-arrow-color': isDark ? '#888' : '#ccc',
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier',
        'label': 'data(label)',
        'font-size': '10px',
        'color': isDark ? '#aaa' : '#666',
        'text-rotation': 'autorotate',
      },
    },
    {
      selector: 'edge[relationship="calls"]',
      style: {
        'line-color': '#4CAF50',
        'target-arrow-color': '#4CAF50',
      },
    },
    {
      selector: 'edge[relationship="imports"]',
      style: {
        'line-color': '#2196F3',
        'target-arrow-color': '#2196F3',
      },
    },
    {
      selector: 'edge[relationship="extends"]',
      style: {
        'line-color': '#FF9800',
        'target-arrow-color': '#FF9800',
        'line-style': 'dashed',
      },
    },
  ];
}

// 布局选项配置
function getLayoutOptions(layout: string) {
  const commonOptions = {
    animate: true,
    animationDuration: 500,
    animationEasing: 'ease-out',
  };

  switch (layout) {
    case 'dagre':
      return {
        name: 'dagre',
        rankDir: 'TB',
        nodeSep: 50,
        rankSep: 100,
        ...commonOptions,
      };

    case 'cose':
      return {
        name: 'cose',
        idealEdgeLength: 100,
        nodeOverlap: 20,
        ...commonOptions,
      };

    case 'breadthfirst':
      return {
        name: 'breadthfirst',
        directed: true,
        spacingFactor: 1.5,
        ...commonOptions,
      };

    case 'circle':
      return {
        name: 'circle',
        spacingFactor: 1.5,
        ...commonOptions,
      };

    case 'grid':
      return {
        name: 'grid',
        rows: undefined,
        cols: undefined,
        ...commonOptions,
      };

    default:
      return {
        name: 'dagre',
        ...commonOptions,
      };
  }
}
