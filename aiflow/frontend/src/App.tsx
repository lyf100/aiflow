import { useEffect, useState } from 'react';
import { useAnalysisStore } from './stores/analysisStore';
import { CodeGraph } from './components/CodeGraph/CodeGraph';
import { TreeView } from './components/TreeView/TreeView';
import { MultiTraceCoordinator } from './components/MultiTraceCoordinator/MultiTraceCoordinator';
import { ProjectList } from './components/ProjectList/ProjectList';
import { ProjectManager } from './services/ProjectManager';
import './App.css';

function App() {
  const { data, loading, error, setData, setLoading, setError } = useAnalysisStore();
  const [autoLoadAttempted, setAutoLoadAttempted] = useState(false);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [isPlaying] = useState(true);  // 🔧 修复: 移除未使用的setter
  const [filteredNodes, setFilteredNodes] = useState<any[]>([]);
  const [filteredEdges, setFilteredEdges] = useState<any[]>([]);
  const [showAnimationModal, setShowAnimationModal] = useState(false);
  const [animationTraces, setAnimationTraces] = useState<any[]>([]);
  const [selectedNodeName, setSelectedNodeName] = useState<string>('');
  const [navigationHistory, setNavigationHistory] = useState<string[]>([]); // 导航历史栈

  // 自动加载 analysis.json
  useEffect(() => {
    if (!autoLoadAttempted) {
      setAutoLoadAttempted(true);

      // 强制重新加载最新数据
      setLoading(true);
      fetch('/analysis.json?t=' + Date.now())
        .then(res => {
          if (!res.ok) throw new Error('分析数据未找到');
          return res.json();
        })
        .then(jsonData => {
          setData(jsonData);
          console.log('✅ 自动加载分析数据成功', jsonData);
          console.log('📊 项目:', jsonData.project_name || jsonData.metadata?.project_name || 'Unknown');
          console.log('📦 节点数:', jsonData.code_structure?.nodes?.length || 0);
          console.log('🎬 轨迹数:', jsonData.execution_traces?.length || 0);

          // 🆕 自动保存到项目缓存
          try {
            ProjectManager.saveProject(jsonData);
            console.log('💾 项目已自动保存到缓存');
          } catch (error) {
            console.warn('⚠️ 自动保存失败:', error);
          }
        })
        .catch(err => {
          console.log('⏳ 等待分析数据生成...', err.message);
          setError('等待分析数据生成... 运行 /ac-analyze <项目名> 开始分析');
        });
    }
  }, [autoLoadAttempted, setData, setLoading, setError]);

  if (loading) {
    return (
      <div className="app-container loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <h2>🔄 加载中...</h2>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="app-container error">
        <div className="error-message">
          <h2>⚠️ {error}</h2>
          <p>请在 Claude Code 中运行命令:</p>
          <code>/ac-analyze &lt;项目名&gt;</code>
          <p className="example">例如: /ac-analyze NewPipe-dev</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="app-container welcome">
        <div className="welcome-message">
          <h1>🚀 AIFlow</h1>
          <h2>AI 分析可视化平台</h2>
          <p>等待分析数据...</p>
          <div className="instructions">
            <h3>使用方法:</h3>
            <ol>
              <li>在 Claude Code 中运行: <code>/ac-analyze &lt;项目名&gt;</code></li>
              <li>等待分析完成</li>
              <li>查看可视化结果</li>
            </ol>
          </div>
        </div>
      </div>
    );
  }

  // 🔧 兼容 MCP Server 输出格式（无 metadata 包装）
  const metadata = data.metadata || {
    project_name: data.project_name || 'Unknown Project',
    protocol_version: data.protocol_version || '2.0.0',
    timestamp: data.timestamp || new Date().toISOString(),
    analysis_timestamp: new Date().toISOString()
  };

  // 验证必需字段
  if (!data.code_structure || !data.code_structure.nodes || !data.code_structure.edges) {
    console.error('❌ 数据结构错误:', {
      hasCodeStructure: !!data.code_structure,
      hasNodes: !!(data.code_structure && data.code_structure.nodes),
      hasEdges: !!(data.code_structure && data.code_structure.edges),
      dataKeys: Object.keys(data)
    });
    return (
      <div className="app-container error">
        <div className="error-message">
          <h2>⚠️ 数据格式错误</h2>
          <p>code_structure 字段缺失或格式不正确</p>
          <p>请检查 analysis.json 文件是否包含完整的 code_structure 数据</p>
          <code>必需字段: code_structure.nodes, code_structure.edges</code>
        </div>
      </div>
    );
  }

  const code_structure = data.code_structure;
  const execution_traces = data.execution_traces || [];

  console.log('✅ 数据加载成功:', {
    project: metadata.project_name,
    nodes: code_structure.nodes.length,
    edges: code_structure.edges.length,
    traces: execution_traces.length
  });

  // 🔙 返回上一层
  const handleBack = () => {
    if (navigationHistory.length > 0) {
      // 弹出历史栈的最后一个节点
      const previousNodeId = navigationHistory[navigationHistory.length - 1];
      if (!previousNodeId) return;  // 🔧 修复: 确保previousNodeId存在
      setNavigationHistory(navigationHistory.slice(0, -1));

      // 重新显示上一个节点，使用 false 标记表示不加入历史
      console.log('🔙 返回上一层:', previousNodeId);
      handleNodeClick(previousNodeId, false);
    } else {
      // 历史栈为空，返回主界面
      setSelectedNodeId(null);
      setFilteredNodes([]);
      setFilteredEdges([]);
      setNavigationHistory([]);
      console.log('🔙 返回主界面');
    }
  };

  // 🆕 处理项目切换
  const handleProjectSelect = (projectData: any) => {
    setData(projectData);
    setSelectedNodeId(null);
    setFilteredNodes([]);
    setFilteredEdges([]);
    setNavigationHistory([]);
    console.log('🔄 已切换项目:', projectData.metadata?.project_name || projectData.project_name);
  };

  // 🎯 处理节点点击 - 显示相关节点 + 查找执行轨迹
  const handleNodeClick = (nodeId: string, addToHistory: boolean = true) => {
    console.log('==========================================');
    console.log('🎯 节点点击:', nodeId, addToHistory ? '(加入历史)' : '(不加入历史)');

    // 如果当前有选中的节点，且需要加入历史，则将其加入历史栈
    if (selectedNodeId && addToHistory) {
      setNavigationHistory([...navigationHistory, selectedNodeId]);
      console.log('📚 加入导航历史:', selectedNodeId, '→ 历史栈:', [...navigationHistory, selectedNodeId]);
    }

    setSelectedNodeId(nodeId);

    const allNodes = code_structure.nodes;
    const allEdges = code_structure.edges;

    // 找到被点击的节点
    const clickedNode = allNodes.find((n: any) => n.id === nodeId);
    if (!clickedNode) {
      console.log('❌ 未找到节点');
      return;
    }
    console.log('✅ 找到节点:', clickedNode.name, '类型:', clickedNode.stereotype);

    // 根据节点类型决定显示策略
    let nodesToShow: any[] = [];
    let edgesToShow: any[] = [];

    if (clickedNode.stereotype === 'system') {
      nodesToShow = allNodes.filter((n: any) =>
        n.stereotype === 'system' || n.stereotype === 'module'
      );
      edgesToShow = allEdges.filter((e: any) =>
        nodesToShow.some((n: any) => n.id === e.source) &&
        nodesToShow.some((n: any) => n.id === e.target)
      );
    } else if (clickedNode.stereotype === 'module') {
      nodesToShow = allNodes.filter((n: any) =>
        n.id === nodeId ||
        (n.stereotype === 'component' && allEdges.some((e: any) =>
          e.source === nodeId && e.target === n.id && e.type === 'contains'
        ))
      );
      edgesToShow = allEdges.filter((e: any) =>
        nodesToShow.some((n: any) => n.id === e.source) &&
        nodesToShow.some((n: any) => n.id === e.target)
      );
    } else if (clickedNode.stereotype === 'component') {
      const methodNodes = allNodes.filter((n: any) =>
        n.stereotype === 'function' && n.parent_class_id === nodeId
      );
      nodesToShow = [clickedNode, ...methodNodes];

      edgesToShow = allEdges.filter((e: any) =>
        nodesToShow.some((n: any) => n.id === e.source) &&
        nodesToShow.some((n: any) => n.id === e.target)
      );
    } else if (clickedNode.stereotype === 'function') {
      const calledMethods = allEdges
        .filter((e: any) => e.source === nodeId && e.type === 'calls')
        .map((e: any) => allNodes.find((n: any) => n.id === e.target))
        .filter(Boolean);

      nodesToShow = [clickedNode, ...calledMethods];
      edgesToShow = allEdges.filter((e: any) =>
        nodesToShow.some((n: any) => n.id === e.source) &&
        nodesToShow.some((n: any) => n.id === e.target)
      );
    }

    console.log(`显示 ${nodesToShow.length} 个节点, ${edgesToShow.length} 条边`);
    setFilteredNodes(nodesToShow);
    setFilteredEdges(edgesToShow);

    // 🎬 查找并过滤执行轨迹 - 只显示与该节点相关的步骤
    console.log(`📊 开始查找执行轨迹,总共 ${execution_traces.length} 个traces`);

    // 确定相关的节点ID集合（考虑层次结构）
    let relevantNodeIds = new Set<string>([nodeId]);

    if (clickedNode.stereotype === 'component') {
      // 对于组件节点，包含所有子函数
      const childFunctions = allNodes.filter((n: any) =>
        n.stereotype === 'function' && n.parent_class_id === nodeId
      );
      childFunctions.forEach((n: any) => relevantNodeIds.add(n.id));
      console.log(`📦 组件节点 "${clickedNode.name}" 包含 ${childFunctions.length} 个子函数`);
    } else if (clickedNode.stereotype === 'module') {
      // 对于模块节点，包含所有子组件和子函数
      const childComponents = allNodes.filter((n: any) =>
        n.stereotype === 'component' && allEdges.some((e: any) =>
          e.source === nodeId && e.target === n.id && e.type === 'contains'
        )
      );
      childComponents.forEach((comp: any) => {
        relevantNodeIds.add(comp.id);
        // 还要包含组件的子函数
        const compFunctions = allNodes.filter((n: any) =>
          n.stereotype === 'function' && n.parent_class_id === comp.id
        );
        compFunctions.forEach((f: any) => relevantNodeIds.add(f.id));
      });
      console.log(`📁 模块节点 "${clickedNode.name}" 包含 ${childComponents.length} 个组件`);
    } else if (clickedNode.stereotype === 'system') {
      // 对于系统节点，包含所有模块及其子节点
      const childModules = allNodes.filter((n: any) => n.stereotype === 'module');
      childModules.forEach((mod: any) => {
        relevantNodeIds.add(mod.id);
        // 包含模块的所有子节点
        const modComponents = allNodes.filter((n: any) =>
          n.stereotype === 'component' && allEdges.some((e: any) =>
            e.source === mod.id && e.target === n.id && e.type === 'contains'
          )
        );
        modComponents.forEach((comp: any) => {
          relevantNodeIds.add(comp.id);
          const compFunctions = allNodes.filter((n: any) =>
            n.stereotype === 'function' && n.parent_class_id === comp.id
          );
          compFunctions.forEach((f: any) => relevantNodeIds.add(f.id));
        });
      });
      console.log(`🏢 系统节点 "${clickedNode.name}" 包含 ${childModules.length} 个模块`);
    }

    console.log(`🎯 相关节点ID集合 (${relevantNodeIds.size} 个):`, Array.from(relevantNodeIds));

    // 打印所有traces的信息
    execution_traces.forEach((trace: any, index: number) => {
      const steps = trace.flowchart?.steps || [];
      const nodeIds = steps.map((s: any) => s.node_id).filter(Boolean);
      console.log(`  Trace ${index + 1}: ${trace.trace_name}, ${steps.length} 步骤, node_ids:`, nodeIds);
    });

    // 为每个trace创建只包含相关步骤的新trace对象
    const relevantTraces = execution_traces
      .map((trace: any) => {
        const steps = trace.flowchart?.steps || [];
        // 只保留相关节点的步骤
        const filteredSteps = steps.filter((step: any) =>
          relevantNodeIds.has(step.node_id)
        );

        if (filteredSteps.length === 0) {
          return null; // 该trace没有相关步骤
        }

        // 创建新的trace对象，只包含过滤后的步骤
        return {
          ...trace,
          flowchart: {
            ...trace.flowchart,
            steps: filteredSteps
          },
          _original_step_count: steps.length, // 保存原始步骤数用于调试
          _filtered_step_count: filteredSteps.length
        };
      })
      .filter(Boolean); // 移除null值

    console.log(`🔍 查找结果: ${relevantTraces.length} 个匹配的traces`);
    relevantTraces.forEach((trace: any, index: number) => {
      console.log(`  ✅ Trace ${index + 1}: "${trace.trace_name}"`);
      console.log(`     原始步骤: ${trace._original_step_count}, 过滤后步骤: ${trace._filtered_step_count}`);
      console.log(`     步骤详情:`, trace.flowchart.steps.map((s: any) => `${s.id}(${s.node_id})`).join(', '));
    });

    if (relevantTraces.length > 0) {
      console.log(`🎬 打开动画模态框, 显示 ${relevantTraces.length} 个执行轨迹`);
      setAnimationTraces(relevantTraces);
      setSelectedNodeName(clickedNode.name);
      setShowAnimationModal(true);
      console.log('Modal state set:', {
        showAnimationModal: true,
        animationTraces: relevantTraces.length,
        selectedNodeName: clickedNode.name
      });
    } else {
      console.log('❌ 该节点没有相关的执行轨迹');
      console.log(`   当前节点: ${clickedNode.name} (${clickedNode.stereotype})`);
      console.log('   建议:尝试点击 function 类型的节点，或者包含function的上层节点');
    }
    console.log('==========================================');
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-left">
          <h1>🚀 AIFlow</h1>
          <span className="project-name">{metadata.project_name}</span>
        </div>
        <div className="header-right">
          <ProjectList
            onProjectSelect={handleProjectSelect}
            currentProjectName={metadata.project_name}
          />
          <span className="protocol-version">v{metadata.protocol_version}</span>
          <span className="timestamp">{new Date(metadata.timestamp || metadata.analysis_timestamp).toLocaleString('zh-CN')}</span>
        </div>
      </header>

      <main className="app-main">
        <div className="structure-view">
          <div className="sidebar-panel">
            <TreeView
              nodes={code_structure.nodes}
              onNodeClick={handleNodeClick}
            />
          </div>
          <div className="graph-panel">
            {selectedNodeId ? (
              <CodeGraph
                nodes={filteredNodes}
                edges={filteredEdges}
                onNodeClick={handleNodeClick}
                onBack={handleBack}
              />
            ) : (
              <div className="graph-placeholder">
                <div className="placeholder-content">
                  <h2>👈 点击左侧树节点查看详情</h2>
                  <p>点击节点查看代码结构图</p>
                  <p>如果节点有执行轨迹，会自动弹出动画</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* 🎬 动画弹窗 */}
      {showAnimationModal && animationTraces.length > 0 && (
        <div className="animation-modal-overlay" onClick={() => setShowAnimationModal(false)}>
          <div className="animation-modal" onClick={(e) => e.stopPropagation()}>
            <div className="animation-modal-header">
              <h2>🎬 执行动画: {selectedNodeName}</h2>
              <button
                className="close-button"
                onClick={() => setShowAnimationModal(false)}
              >
                ✕
              </button>
            </div>
            <div className="animation-modal-content">
              <MultiTraceCoordinator
                traces={animationTraces}
                isPlaying={isPlaying}
                onGlobalStepChange={(traceId, stepId) => {
                  console.log(`Trace ${traceId} - 当前步骤:`, stepId);
                }}
              />
            </div>
          </div>
        </div>
      )}

      <footer className="app-footer">
        <p>🚀 AIFlow - AI 代码执行流程可视化</p>
      </footer>
    </div>
  );
}

export default App;
