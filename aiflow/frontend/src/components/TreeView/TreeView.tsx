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

    // 生成详细信息
    let details = '';
    if (node.type === 'system') {
      details = node.nodeData.file_path || '';
    } else if (node.type === 'module') {
      details = `包: ${node.name}`;
    } else if (node.type === 'component') {
      details = `文件: ${node.nodeData.file_path || ''}`;
    } else if (node.type === 'function') {
      const params = node.nodeData.parameters || [];
      const returnType = node.nodeData.return_type || 'void';
      details = `(${params.join(', ')}) → ${returnType}`;
    }

    return (
      <div key={node.id} className="tree-node-wrapper">
        <div className="tree-node-indent" style={{ width: `${depth * 20}px` }}></div>
        <div
          className={`tree-node ${node.type} ${isSelected ? 'selected' : ''}`}
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
            {details && <div className="node-details">{details}</div>}
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
