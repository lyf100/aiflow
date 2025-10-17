import { useState } from 'react';
import type { CodeNode } from '../../types/protocol';
import './TreeView.css';

interface TreeNode {
  id: string;
  name: string;
  type: 'system' | 'module' | 'component' | 'function';
  children: TreeNode[];
  nodeData: CodeNode;
}

interface TreeViewProps {
  nodes: CodeNode[];
  onNodeClick?: (nodeId: string) => void;
}

export function TreeView({ nodes, onNodeClick }: TreeViewProps) {
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set(['root']));
  const [selectedNode, setSelectedNode] = useState<string | null>(null);

  // 构建树形结构
  const buildTree = (): TreeNode | null => {
    const systemNode = nodes.find(n => n.stereotype === 'system');
    if (!systemNode) return null;

    const tree: TreeNode = {
      id: systemNode.id,
      name: systemNode.name,
      type: 'system',
      children: [],
      nodeData: systemNode
    };

    // 获取所有模块
    const moduleNodes = nodes.filter(n => n.stereotype === 'module');

    moduleNodes.forEach(moduleNode => {
      const moduleTreeNode: TreeNode = {
        id: moduleNode.id,
        name: moduleNode.name,
        type: 'module',
        children: [],
        nodeData: moduleNode
      };

      // 获取该模块下的组件
      const componentNodes = nodes.filter(n =>
        n.stereotype === 'component' &&
        nodes.some(edge => edge.source === moduleNode.id && edge.target === n.id)
      );

      componentNodes.forEach(componentNode => {
        const componentTreeNode: TreeNode = {
          id: componentNode.id,
          name: componentNode.name,
          type: 'component',
          children: [],
          nodeData: componentNode
        };

        // 获取该组件下的函数
        const functionNodes = nodes.filter(n =>
          n.stereotype === 'function' &&
          n.parent_class_id === componentNode.id
        );

        functionNodes.forEach(functionNode => {
          componentTreeNode.children.push({
            id: functionNode.id,
            name: functionNode.name,
            type: 'function',
            children: [],
            nodeData: functionNode
          });
        });

        // 只有有子节点或者本身有意义时才添加
        if (componentTreeNode.children.length > 0 || componentNode.name) {
          moduleTreeNode.children.push(componentTreeNode);
        }
      });

      if (moduleTreeNode.children.length > 0) {
        tree.children.push(moduleTreeNode);
      }
    });

    return tree;
  };

  const toggleNode = (nodeId: string) => {
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(nodeId)) {
      newExpanded.delete(nodeId);
    } else {
      newExpanded.add(nodeId);
    }
    setExpandedNodes(newExpanded);
  };

  const handleNodeClick = (node: TreeNode) => {
    setSelectedNode(node.id);
    onNodeClick?.(node.id);
  };

  const renderTreeNode = (node: TreeNode, depth: number = 0): JSX.Element => {
    const isExpanded = expandedNodes.has(node.id);
    const hasChildren = node.children.length > 0;
    const isSelected = selectedNode === node.id;

    const iconMap = {
      system: '🏢',
      module: '📦',
      component: '📄',
      function: '⚙️'
    };

    // 🆕 生成完整详细信息 - 根据节点类型展示不同的文件组成信息
    const renderDetails = () => {
      const metadata = node.nodeData.metadata || {};
      const details: JSX.Element[] = [];

      if (node.type === 'system') {
        // System节点：显示项目统计
        details.push(
          <div key="system-info" className="node-info-section">
            <div className="info-label">📊 项目统计</div>
            <div className="info-value">
              {metadata.total_packages && `${metadata.total_packages} 个包 | `}
              {metadata.core_packages && `${metadata.core_packages} 核心包`}
            </div>
            {metadata.architecture_style && (
              <div className="info-value">架构: {metadata.architecture_style}</div>
            )}
          </div>
        );
      } else if (node.type === 'module') {
        // Module节点：显示目录和包含的文件
        const directories = node.nodeData.directories || [];
        details.push(
          <div key="module-dirs" className="node-info-section">
            <div className="info-label">📁 包含目录</div>
            {directories.length > 0 ? (
              directories.map((dir, idx) => (
                <div key={idx} className="info-value directory-item">
                  <code>{dir}</code>
                </div>
              ))
            ) : (
              <div className="info-value empty">无目录信息</div>
            )}
          </div>
        );

        if (metadata.business_domain) {
          details.push(
            <div key="domain" className="node-info-section">
              <div className="info-label">🏷️ 业务领域</div>
              <div className="info-value">{metadata.business_domain}</div>
            </div>
          );
        }

        if (metadata.complexity !== undefined) {
          details.push(
            <div key="complexity" className="node-info-section">
              <div className="info-label">📈 复杂度</div>
              <div className="info-value complexity-badge" data-level={
                metadata.complexity > 0.7 ? 'high' : metadata.complexity > 0.4 ? 'medium' : 'low'
              }>
                {(metadata.complexity * 100).toFixed(0)}%
              </div>
            </div>
          );
        }
      } else if (node.type === 'component') {
        // Component节点：显示文件路径和语言
        if (node.nodeData.file_path) {
          details.push(
            <div key="file-path" className="node-info-section">
              <div className="info-label">📄 文件路径</div>
              <div className="info-value file-path">
                <code>{node.nodeData.file_path}</code>
              </div>
            </div>
          );
        }

        if (node.nodeData.language) {
          details.push(
            <div key="language" className="node-info-section">
              <div className="info-label">💻 语言</div>
              <div className="info-value">{node.nodeData.language}</div>
            </div>
          );
        }

        if (metadata.pattern) {
          details.push(
            <div key="pattern" className="node-info-section">
              <div className="info-label">🔧 设计模式</div>
              <div className="info-value">{metadata.pattern}</div>
            </div>
          );
        }

        if (metadata.extends) {
          details.push(
            <div key="extends" className="node-info-section">
              <div className="info-label">🔗 继承</div>
              <div className="info-value">{metadata.extends}</div>
            </div>
          );
        }

        if (metadata.responsibilities && Array.isArray(metadata.responsibilities)) {
          details.push(
            <div key="responsibilities" className="node-info-section">
              <div className="info-label">📋 职责</div>
              {metadata.responsibilities.map((resp: string, idx: number) => (
                <div key={idx} className="info-value responsibility-item">• {resp}</div>
              ))}
            </div>
          );
        }
      } else if (node.type === 'function') {
        // Function节点：显示文件路径、行号、参数、返回值
        if (node.nodeData.file_path) {
          details.push(
            <div key="location" className="node-info-section">
              <div className="info-label">📍 位置</div>
              <div className="info-value file-path">
                <code>{node.nodeData.file_path}</code>
                {node.nodeData.line_number && (
                  <span className="line-number">:{node.nodeData.line_number}</span>
                )}
              </div>
            </div>
          );
        }

        const params = node.nodeData.parameters || [];
        const returnType = node.nodeData.return_type || 'void';
        details.push(
          <div key="signature" className="node-info-section">
            <div className="info-label">⚙️ 签名</div>
            <div className="info-value function-signature">
              <code>({params.join(', ')}) → {returnType}</code>
            </div>
          </div>
        );

        if (node.nodeData.language) {
          details.push(
            <div key="language" className="node-info-section">
              <div className="info-label">💻 语言</div>
              <div className="info-value">{node.nodeData.language}</div>
            </div>
          );
        }

        if (metadata.visibility) {
          details.push(
            <div key="visibility" className="node-info-section">
              <div className="info-label">🔒 可见性</div>
              <div className="info-value">{metadata.visibility}</div>
            </div>
          );
        }

        if (metadata.is_async !== undefined) {
          details.push(
            <div key="async" className="node-info-section">
              <div className="info-label">⚡ 异步</div>
              <div className="info-value">{metadata.is_async ? 'Yes' : 'No'}</div>
            </div>
          );
        }

        if (metadata.is_critical_path) {
          details.push(
            <div key="critical" className="node-info-section critical-badge">
              <div className="info-label">⚠️ 关键路径</div>
            </div>
          );
        }

        if (metadata.has_side_effects) {
          details.push(
            <div key="side-effects" className="node-info-section">
              <div className="info-label">💥 副作用</div>
              <div className="info-value">Yes</div>
            </div>
          );
        }
      }

      // 共通：显示description
      if (node.nodeData.description && isExpanded) {
        details.push(
          <div key="description" className="node-info-section description">
            <div className="info-label">📝 描述</div>
            <div className="info-value">{node.nodeData.description}</div>
          </div>
        );
      }

      return details;
    };

    return (
      <div key={node.id} className="tree-node-wrapper">
        <div className="tree-node-indent" style={{ width: `${depth * 20}px` }}></div>
        <div
          className={`tree-node ${node.type} ${isSelected ? 'selected' : ''} ${isExpanded ? 'expanded' : ''}`}
          onClick={() => handleNodeClick(node)}
        >
          {hasChildren && (
            <span
              className="expand-icon"
              onClick={(e) => {
                e.stopPropagation();
                toggleNode(node.id);
              }}
            >
              {isExpanded ? '▼' : '▶'}
            </span>
          )}
          {!hasChildren && <span className="expand-icon-placeholder"></span>}
          <span className="node-icon">{iconMap[node.type]}</span>
          <div className="node-content">
            <div className="node-name">
              {node.name}
              {hasChildren && <span className="node-count">({node.children.length})</span>}
            </div>
            {/* 🆕 完整的详细信息面板 */}
            <div className="node-details-panel">
              {renderDetails()}
            </div>
          </div>
        </div>
        {isExpanded && hasChildren && (
          <div className="tree-node-children">
            {node.children.map(child => renderTreeNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  const tree = buildTree();

  if (!tree) {
    return (
      <div className="tree-view-container">
        <div className="tree-empty">暂无数据</div>
      </div>
    );
  }

  return (
    <div className="tree-view-container">
      <div className="tree-header">
        <h3>项目结构</h3>
        <div className="tree-stats">
          <span>{nodes.filter(n => n.stereotype === 'module').length} 模块</span>
          <span>{nodes.filter(n => n.stereotype === 'component').length} 类</span>
          <span>{nodes.filter(n => n.stereotype === 'function').length} 方法</span>
        </div>
      </div>
      <div className="tree-content">
        {renderTreeNode(tree)}
      </div>
    </div>
  );
}
