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
  onBack?: () => void;
}

export function CodeGraph({ nodes, edges, onNodeClick, onBack }: CodeGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [selectedNodeData, setSelectedNodeData] = useState<CodeNode | null>(null);

  // 🆕 获取选中节点的详细信息
  const getNodeDetails = (nodeId: string) => {
    const node = nodes.find(n => n.id === nodeId);
    if (!node) return null;

    // 查找相关的边
    const incomingEdges = edges.filter(e => e.target === nodeId);
    const outgoingEdges = edges.filter(e => e.source === nodeId);

    // 查找子节点 (contains关系)
    const childNodes = edges
      .filter(e => e.source === nodeId && e.type === 'contains')
      .map(e => nodes.find(n => n.id === e.target))
      .filter(Boolean) as CodeNode[];

    // 查找调用的节点 (calls关系)
    const calledNodes = edges
      .filter(e => e.source === nodeId && e.type === 'calls')
      .map(e => nodes.find(n => n.id === e.target))
      .filter(Boolean) as CodeNode[];

    // 查找依赖的节点 (depends_on关系)
    const dependsOnNodes = edges
      .filter(e => e.source === nodeId && e.type === 'depends_on')
      .map(e => nodes.find(n => n.id === e.target))
      .filter(Boolean) as CodeNode[];

    // 查找继承的节点 (inherits关系)
    const inheritsNodes = edges
      .filter(e => e.source === nodeId && e.type === 'inherits')
      .map(e => nodes.find(n => n.id === e.target))
      .filter(Boolean) as CodeNode[];

    // 查找被谁包含 (parent)
    const parentEdge = edges.find(e => e.target === nodeId && e.type === 'contains');
    const parentNode = parentEdge ? nodes.find(n => n.id === parentEdge.source) : null;

    // 查找被谁调用
    const calledByNodes = edges
      .filter(e => e.target === nodeId && e.type === 'calls')
      .map(e => nodes.find(n => n.id === e.source))
      .filter(Boolean) as CodeNode[];

    return {
      node,
      childNodes,
      calledNodes,
      dependsOnNodes,
      inheritsNodes,
      parentNode,
      calledByNodes,
      incomingEdges,
      outgoingEdges
    };
  };

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
          description: node.description || '', // 添加描述信息用于tooltip
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
            'font-weight': 600,  // 🔧 修复: 使用数字而非字符串
            'width': '120px',
            'height': '120px',
            'text-wrap': 'wrap',
            'text-max-width': '110px',
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
            'text-max-width': '140px',
          },
        },
        {
          selector: 'node[stereotype="module"]',
          style: {
            'background-color': '#764ba2',
            'width': '130px',
            'height': '130px',
            'font-size': '20px',
            'text-max-width': '120px',
          },
        },
        {
          selector: 'node[stereotype="component"]',
          style: {
            'background-color': '#f093fb',
            'width': '120px',
            'height': '120px',
            'font-size': '18px',
            'text-max-width': '110px',
          },
        },
        {
          selector: 'node[stereotype="function"]',
          style: {
            'background-color': '#4facfe',
            'width': '100px',
            'height': '100px',
            'font-size': '16px',
            'text-max-width': '90px',
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
            'font-weight': 600,  // 🔧 修复: 使用数字而非字符串
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
            'width': 2,
          },
        },
        {
          selector: 'edge[label="depends_on"]',
          style: {
            'line-color': '#ff9800',
            'target-arrow-color': '#ff9800',
            'line-style': 'solid',
            'width': 3,
            'target-arrow-shape': 'triangle-cross',
          },
        },
        {
          selector: 'edge[label="inherits"]',
          style: {
            'line-color': '#9c27b0',
            'target-arrow-color': '#9c27b0',
            'line-style': 'solid',
            'width': 4,
            'target-arrow-shape': 'triangle-tee',
            'curve-style': 'taxi',
          },
        },
      ],
      layout: {
        name: 'dagre',
        rankDir: 'LR',
        nodeSep: 80,
        rankSep: 150,
        padding: 50,
      } as any,  // 🔧 修复: dagre layout配置需要类型断言
      minZoom: 0.1,
      maxZoom: 3,
      wheelSensitivity: 0.2,
    });

    // 节点点击事件
    cy.on('tap', 'node', (evt) => {
      const node = evt.target;
      const nodeId = node.id();
      const nodeData = nodes.find(n => n.id === nodeId);
      setSelectedNode(nodeId);
      setSelectedNodeData(nodeData || null);
      onNodeClick?.(nodeId);
    });

    // 背景点击取消选择
    cy.on('tap', (evt) => {
      if (evt.target === cy) {
        setSelectedNode(null);
        setSelectedNodeData(null);
      }
    });

    // 创建tooltip元素
    let tooltip: HTMLDivElement | null = null;

    // 鼠标悬停显示节点描述
    cy.on('mouseover', 'node', (evt) => {
      const node = evt.target;
      const description = node.data('description');

      if (description) {
        // 创建tooltip
        if (!tooltip) {
          tooltip = document.createElement('div');
          tooltip.style.position = 'absolute';
          tooltip.style.backgroundColor = 'rgba(0, 0, 0, 0.85)';
          tooltip.style.color = '#fff';
          tooltip.style.padding = '8px 12px';
          tooltip.style.borderRadius = '6px';
          tooltip.style.fontSize = '14px';
          tooltip.style.maxWidth = '300px';
          tooltip.style.zIndex = '9999';
          tooltip.style.pointerEvents = 'none';
          tooltip.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.3)';
          document.body.appendChild(tooltip);
        }

        tooltip.textContent = description;
        tooltip.style.display = 'block';

        // 设置tooltip位置（跟随鼠标）
        const updateTooltipPosition = (e: MouseEvent) => {
          if (tooltip) {
            tooltip.style.left = `${e.clientX + 15}px`;
            tooltip.style.top = `${e.clientY + 15}px`;
          }
        };

        containerRef.current?.addEventListener('mousemove', updateTooltipPosition);
        node.data('tooltipHandler', updateTooltipPosition);
      }
    });

    // 鼠标移出隐藏tooltip
    cy.on('mouseout', 'node', (evt) => {
      if (tooltip) {
        tooltip.style.display = 'none';
        const handler = evt.target.data('tooltipHandler');
        if (handler) {
          containerRef.current?.removeEventListener('mousemove', handler);
        }
      }
    });

    cyRef.current = cy;

    // 初始化时自动适应画布，显示所有内容
    setTimeout(() => {
      cy.fit(undefined, 50);
    }, 100);

    return () => {
      // 清理tooltip元素
      if (tooltip && tooltip.parentNode) {
        tooltip.parentNode.removeChild(tooltip);
      }
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

  // 🆕 渲染详情面板
  const renderDetailsPanel = () => {
    if (!selectedNode || !selectedNodeData) return null;

    const details = getNodeDetails(selectedNode);
    if (!details) return null;

    const { node, childNodes, calledNodes, dependsOnNodes, inheritsNodes, parentNode, calledByNodes } = details;
    const metadata = node.metadata || {};

    return (
      <div className="details-panel">
        <div className="details-header">
          <h3>{node.name}</h3>
          <button className="close-details" onClick={() => setSelectedNode(null)}>✕</button>
        </div>

        <div className="details-content">
          {/* 基本信息 */}
          <div className="detail-section">
            <div className="section-title">📋 基本信息</div>
            <div className="detail-item">
              <span className="detail-label">类型:</span>
              <span className="detail-value type-badge" data-type={node.stereotype}>{node.stereotype}</span>
            </div>
            {node.id && (
              <div className="detail-item">
                <span className="detail-label">ID:</span>
                <span className="detail-value id-text">{node.id}</span>
              </div>
            )}
            {node.description && (
              <div className="detail-item description-item">
                <span className="detail-label">描述:</span>
                <span className="detail-value">{node.description}</span>
              </div>
            )}
          </div>

          {/* 文件信息 */}
          {(node.file_path || (node.directories && node.directories.length > 0)) && (
            <div className="detail-section">
              <div className="section-title">📄 文件组成</div>
              {node.file_path && (
                <div className="detail-item file-item">
                  <span className="detail-label">文件路径:</span>
                  <code className="file-path">{node.file_path}</code>
                  {node.line_number && (
                    <span className="line-number">:{node.line_number}</span>
                  )}
                </div>
              )}
              {node.directories && node.directories.length > 0 && (
                <div className="detail-item">
                  <span className="detail-label">包含目录:</span>
                  <div className="directories-list">
                    {node.directories.map((dir: string, idx: number) => (
                      <code key={idx} className="directory-item">{dir}</code>
                    ))}
                  </div>
                </div>
              )}
              {node.language && (
                <div className="detail-item">
                  <span className="detail-label">语言:</span>
                  <span className="detail-value">{node.language}</span>
                </div>
              )}
            </div>
          )}

          {/* Metadata信息 */}
          {Object.keys(metadata).length > 0 && (
            <div className="detail-section">
              <div className="section-title">🏷️ 元数据</div>
              {metadata.pattern && (
                <div className="detail-item">
                  <span className="detail-label">设计模式:</span>
                  <span className="detail-value">{metadata.pattern}</span>
                </div>
              )}
              {metadata.complexity !== undefined && (
                <div className="detail-item">
                  <span className="detail-label">复杂度:</span>
                  <span className={`detail-value complexity-badge ${
                    metadata.complexity > 0.7 ? 'high' : metadata.complexity > 0.4 ? 'medium' : 'low'
                  }`}>
                    {(metadata.complexity * 100).toFixed(0)}%
                  </span>
                </div>
              )}
              {metadata.is_critical_path && (
                <div className="detail-item">
                  <span className="detail-label">⚠️ 关键路径</span>
                </div>
              )}
              {metadata.is_async !== undefined && (
                <div className="detail-item">
                  <span className="detail-label">异步:</span>
                  <span className="detail-value">{metadata.is_async ? 'Yes' : 'No'}</span>
                </div>
              )}
            </div>
          )}

          {/* 包含关系 */}
          {parentNode && (
            <div className="detail-section">
              <div className="section-title">⬆️ 被包含于</div>
              <div className="relation-item" onClick={() => onNodeClick?.(parentNode.id)}>
                <span className="relation-icon">📦</span>
                <span className="relation-name">{parentNode.name}</span>
              </div>
            </div>
          )}

          {childNodes.length > 0 && (
            <div className="detail-section">
              <div className="section-title">⬇️ 包含 ({childNodes.length})</div>
              <div className="relations-list">
                {childNodes.map((child) => (
                  <div key={child.id} className="relation-item" onClick={() => onNodeClick?.(child.id)}>
                    <span className="relation-icon">📄</span>
                    <span className="relation-name">{child.name}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 调用关系 */}
          {calledNodes.length > 0 && (
            <div className="detail-section">
              <div className="section-title">📞 调用 ({calledNodes.length})</div>
              <div className="relations-list">
                {calledNodes.map((called) => (
                  <div key={called.id} className="relation-item" onClick={() => onNodeClick?.(called.id)}>
                    <span className="relation-icon">⚙️</span>
                    <span className="relation-name">{called.name}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {calledByNodes.length > 0 && (
            <div className="detail-section">
              <div className="section-title">📞 被调用 ({calledByNodes.length})</div>
              <div className="relations-list">
                {calledByNodes.map((caller) => (
                  <div key={caller.id} className="relation-item" onClick={() => onNodeClick?.(caller.id)}>
                    <span className="relation-icon">⚙️</span>
                    <span className="relation-name">{caller.name}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 依赖关系 */}
          {dependsOnNodes.length > 0 && (
            <div className="detail-section">
              <div className="section-title">🔗 依赖 ({dependsOnNodes.length})</div>
              <div className="relations-list">
                {dependsOnNodes.map((dep) => (
                  <div key={dep.id} className="relation-item" onClick={() => onNodeClick?.(dep.id)}>
                    <span className="relation-icon">📦</span>
                    <span className="relation-name">{dep.name}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 继承关系 */}
          {inheritsNodes.length > 0 && (
            <div className="detail-section">
              <div className="section-title">🔼 继承 ({inheritsNodes.length})</div>
              <div className="relations-list">
                {inheritsNodes.map((parent) => (
                  <div key={parent.id} className="relation-item" onClick={() => onNodeClick?.(parent.id)}>
                    <span className="relation-icon">🏛️</span>
                    <span className="relation-name">{parent.name}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="code-graph-container">
      <div className="code-graph-controls">
        {onBack && (
          <button onClick={onBack} title="返回主界面">
            ⬅️ 返回
          </button>
        )}
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
      {/* 🆕 关系类型图例 */}
      <div className="relationship-legend">
        <div className="legend-title">🔗 关系类型图例</div>
        <div className="legend-items">
          <div className="legend-item">
            <div className="legend-line calls-line"></div>
            <span className="legend-label">calls - 调用关系</span>
          </div>
          <div className="legend-item">
            <div className="legend-line contains-line"></div>
            <span className="legend-label">contains - 包含关系</span>
          </div>
          <div className="legend-item">
            <div className="legend-line depends-line"></div>
            <span className="legend-label">depends_on - 依赖关系</span>
          </div>
          <div className="legend-item">
            <div className="legend-line inherits-line"></div>
            <span className="legend-label">inherits - 继承关系</span>
          </div>
        </div>
      </div>

      <div className="code-graph-main">
        <div ref={containerRef} className="code-graph-canvas" />
        {/* 🆕 详情面板 */}
        {renderDetailsPanel()}
      </div>
    </div>
  );
}
