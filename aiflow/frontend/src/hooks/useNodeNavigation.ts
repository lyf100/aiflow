import { useState, useCallback } from 'react';
import type { CodeNode, CodeEdge } from '../types/protocol';

export interface CodeStructure {
  nodes: CodeNode[];
  edges: CodeEdge[];
}

export interface UseNodeNavigationProps {
  codeStructure: CodeStructure;
  executionTraces: any[];
  onAnimationModalOpen?: (traces: any[], nodeName: string) => void;
}

export interface UseNodeNavigationReturn {
  selectedNodeId: string | null;
  navigationHistory: string[];
  filteredNodes: CodeNode[];
  filteredEdges: CodeEdge[];
  handleNodeClick: (nodeId: string, addToHistory?: boolean) => void;
  handleBack: () => void;
  resetNavigation: () => void;
}

/**
 * useNodeNavigation - 节点导航自定义Hook
 *
 * 功能:
 * - 管理节点选择状态和导航历史栈
 * - 处理节点点击和返回导航
 * - 过滤相关节点和边
 * - 查找并过滤执行轨迹
 *
 * 优势:
 * - 提取复杂导航逻辑，简化App组件
 * - 可复用的导航状态管理
 * - 清晰的职责分离
 * - 便于单元测试
 */
export function useNodeNavigation({
  codeStructure,
  executionTraces,
  onAnimationModalOpen,
}: UseNodeNavigationProps): UseNodeNavigationReturn {
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [navigationHistory, setNavigationHistory] = useState<string[]>([]);
  const [filteredNodes, setFilteredNodes] = useState<CodeNode[]>([]);
  const [filteredEdges, setFilteredEdges] = useState<CodeEdge[]>([]);

  const allNodes = codeStructure.nodes;
  const allEdges = codeStructure.edges;

  /**
   * 重置导航状态
   */
  const resetNavigation = useCallback(() => {
    setSelectedNodeId(null);
    setFilteredNodes([]);
    setFilteredEdges([]);
    setNavigationHistory([]);
  }, []);

  /**
   * 返回上一层导航
   */
  const handleBack = useCallback(() => {
    if (navigationHistory.length > 0) {
      const previousNodeId = navigationHistory[navigationHistory.length - 1];
      if (!previousNodeId) {return;}

      setNavigationHistory(navigationHistory.slice(0, -1));
      console.log('🔙 返回上一层:', previousNodeId);
      // Recursive call with false to avoid adding to history again
      handleNodeClick(previousNodeId, false);
    } else {
      console.log('🔙 返回主界面');
      resetNavigation();
    }
  }, [navigationHistory]); // Note: handleNodeClick will be defined below

  /**
   * 处理节点点击 - 显示相关节点 + 查找执行轨迹
   */
  const handleNodeClick = useCallback((nodeId: string, addToHistory: boolean = true) => {
    console.log('==========================================');
    console.log('🎯 节点点击:', nodeId, addToHistory ? '(加入历史)' : '(不加入历史)');

    // 加入导航历史
    if (selectedNodeId && addToHistory) {
      setNavigationHistory(prev => [...prev, selectedNodeId]);
      console.log('📚 加入导航历史:', selectedNodeId);
    }

    setSelectedNodeId(nodeId);

    // 找到被点击的节点
    const clickedNode = allNodes.find((n: any) => n.id === nodeId);
    if (!clickedNode) {
      console.log('❌ 未找到节点');
      return;
    }
    console.log('✅ 找到节点:', clickedNode.name, '类型:', clickedNode.stereotype);

    // 根据节点类型决定显示策略
    let nodesToShow: CodeNode[] = [];
    let edgesToShow: CodeEdge[] = [];

    if (clickedNode.stereotype === 'system') {
      // System节点: 显示所有system和module节点
      nodesToShow = allNodes.filter((n) =>
        n.stereotype === 'system' || n.stereotype === 'module'
      );
      edgesToShow = allEdges.filter((e) =>
        nodesToShow.some((n) => n.id === e.source) &&
        nodesToShow.some((n) => n.id === e.target)
      );
    } else if (clickedNode.stereotype === 'module') {
      // Module节点: 显示module自身和包含的component
      nodesToShow = allNodes.filter((n) =>
        n.id === nodeId ||
        (n.stereotype === 'component' && allEdges.some((e) =>
          e.source === nodeId && e.target === n.id && e.type === 'contains'
        ))
      );
      edgesToShow = allEdges.filter((e) =>
        nodesToShow.some((n) => n.id === e.source) &&
        nodesToShow.some((n) => n.id === e.target)
      );
    } else if (clickedNode.stereotype === 'component') {
      // Component节点: 显示component和所有方法
      const methodNodes = allNodes.filter((n) =>
        n.stereotype === 'function' && n.parent_class_id === nodeId
      );
      nodesToShow = [clickedNode, ...methodNodes];
      edgesToShow = allEdges.filter((e) =>
        nodesToShow.some((n) => n.id === e.source) &&
        nodesToShow.some((n) => n.id === e.target)
      );
    } else if (clickedNode.stereotype === 'function') {
      // Function节点: 显示function和调用的方法
      const calledMethods = allEdges
        .filter((e) => e.source === nodeId && e.type === 'calls')
        .map((e) => allNodes.find((n) => n.id === e.target))
        .filter((node): node is CodeNode => node !== undefined);

      nodesToShow = [clickedNode, ...calledMethods];
      edgesToShow = allEdges.filter((e) =>
        nodesToShow.some((n) => n.id === e.source) &&
        nodesToShow.some((n) => n.id === e.target)
      );
    }

    console.log(`显示 ${nodesToShow.length} 个节点, ${edgesToShow.length} 条边`);
    setFilteredNodes(nodesToShow);
    setFilteredEdges(edgesToShow);

    // 🎬 查找并过滤执行轨迹
    console.log(`📊 开始查找执行轨迹,总共 ${executionTraces.length} 个traces`);

    // 确定相关的节点ID集合
    const relevantNodeIds = new Set<string>([nodeId]);

    if (clickedNode.stereotype === 'component') {
      const childFunctions = allNodes.filter((n) =>
        n.stereotype === 'function' && n.parent_class_id === nodeId
      );
      childFunctions.forEach((n) => relevantNodeIds.add(n.id));
      console.log(`📦 组件节点 "${clickedNode.name}" 包含 ${childFunctions.length} 个子函数`);
    } else if (clickedNode.stereotype === 'module') {
      const childComponents = allNodes.filter((n) =>
        n.stereotype === 'component' && allEdges.some((e) =>
          e.source === nodeId && e.target === n.id && e.type === 'contains'
        )
      );
      childComponents.forEach((comp) => {
        relevantNodeIds.add(comp.id);
        const compFunctions = allNodes.filter((n) =>
          n.stereotype === 'function' && n.parent_class_id === comp.id
        );
        compFunctions.forEach((f) => relevantNodeIds.add(f.id));
      });
      console.log(`📁 模块节点 "${clickedNode.name}" 包含 ${childComponents.length} 个组件`);
    } else if (clickedNode.stereotype === 'system') {
      const childModules = allNodes.filter((n) => n.stereotype === 'module');
      childModules.forEach((mod) => {
        relevantNodeIds.add(mod.id);
        const modComponents = allNodes.filter((n) =>
          n.stereotype === 'component' && allEdges.some((e) =>
            e.source === mod.id && e.target === n.id && e.type === 'contains'
          )
        );
        modComponents.forEach((comp) => {
          relevantNodeIds.add(comp.id);
          const compFunctions = allNodes.filter((n) =>
            n.stereotype === 'function' && n.parent_class_id === comp.id
          );
          compFunctions.forEach((f) => relevantNodeIds.add(f.id));
        });
      });
      console.log(`🏢 系统节点 "${clickedNode.name}" 包含 ${childModules.length} 个模块`);
    }

    console.log(`🎯 相关节点ID集合 (${relevantNodeIds.size} 个):`, Array.from(relevantNodeIds));

    // 为每个trace创建只包含相关步骤的新trace对象
    const relevantTraces = executionTraces
      .map((trace: any) => {
        const steps = trace.flowchart?.steps || [];
        const filteredSteps = steps.filter((step: any) =>
          relevantNodeIds.has(step.node_id)
        );

        if (filteredSteps.length === 0) {
          return null;
        }

        return {
          ...trace,
          flowchart: {
            ...trace.flowchart,
            steps: filteredSteps
          },
          _original_step_count: steps.length,
          _filtered_step_count: filteredSteps.length
        };
      })
      .filter(Boolean);

    console.log(`🔍 查找结果: ${relevantTraces.length} 个匹配的traces`);

    if (relevantTraces.length > 0) {
      console.log(`🎬 打开动画模态框, 显示 ${relevantTraces.length} 个执行轨迹`);
      onAnimationModalOpen?.(relevantTraces, clickedNode.name);
    } else {
      console.log('❌ 该节点没有相关的执行轨迹');
    }

    console.log('==========================================');
  }, [selectedNodeId, allNodes, allEdges, executionTraces, onAnimationModalOpen]);

  return {
    selectedNodeId,
    navigationHistory,
    filteredNodes,
    filteredEdges,
    handleNodeClick,
    handleBack,
    resetNavigation,
  };
}
