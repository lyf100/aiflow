import { useEffect, useState } from 'react';
import { useAnalysisStore } from './stores/analysisStore';
import { CodeGraph } from './components/CodeGraph/CodeGraph';
import { TreeView } from './components/TreeView/TreeView';
import { MultiTraceCoordinator } from './components/MultiTraceCoordinator/MultiTraceCoordinator';
import { ProjectList } from './components/ProjectList/ProjectList';
import { ProjectManager } from './services/ProjectManager';
import ErrorBoundary from './components/ErrorBoundary/ErrorBoundary';
import { useNodeNavigation } from './hooks/useNodeNavigation';
import './App.css';

function App() {
  const { data, loading, error, setData, setLoading, setError } = useAnalysisStore();
  const [autoLoadAttempted, setAutoLoadAttempted] = useState(false);
  const [isPlaying] = useState(true);  // 🔧 修复: 移除未使用的setter
  const [showAnimationModal, setShowAnimationModal] = useState(false);
  const [animationTraces, setAnimationTraces] = useState<any[]>([]);
  const [selectedNodeName, setSelectedNodeName] = useState<string>('');

  // 🎯 使用节点导航Hook (必须在顶层调用)
  const {
    selectedNodeId,
    filteredNodes,
    filteredEdges,
    handleNodeClick,
    handleBack,
    resetNavigation,
  } = useNodeNavigation({
    codeStructure: data?.code_structure || { nodes: [], edges: [] },
    executionTraces: data?.execution_traces || [],
    onAnimationModalOpen: (traces, nodeName) => {
      setAnimationTraces(traces);
      setSelectedNodeName(nodeName);
      setShowAnimationModal(true);
    },
  });

  // 自动加载 analysis.json
  useEffect(() => {
    if (!autoLoadAttempted) {
      setAutoLoadAttempted(true);

      // 强制重新加载最新数据
      setLoading(true);
      fetch('/analysis.json?t=' + Date.now())
        .then(res => {
          if (!res.ok) {
            throw new Error('分析数据未找到');
          }
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

  // 🆕 处理项目切换
  const handleProjectSelect = (projectData: any) => {
    setData(projectData);
    resetNavigation(); // 使用Hook提供的重置函数
    console.log('🔄 已切换项目:', projectData.metadata?.project_name || projectData.project_name);
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-left">
          <h1>🚀 AIFlow</h1>
          <span className="project-name">{metadata.project_name}</span>
        </div>
        <div className="header-right">
          <ErrorBoundary>
            <ProjectList
              onProjectSelect={handleProjectSelect}
              currentProjectName={metadata.project_name}
            />
          </ErrorBoundary>
          <span className="protocol-version">v{metadata.protocol_version}</span>
          <span className="timestamp">{new Date(metadata.timestamp || metadata.analysis_timestamp).toLocaleString('zh-CN')}</span>
        </div>
      </header>

      <main className="app-main">
        <div className="structure-view">
          <div className="sidebar-panel">
            <ErrorBoundary>
              <TreeView
                nodes={code_structure.nodes}
                onNodeClick={handleNodeClick}
              />
            </ErrorBoundary>
          </div>
          <div className="graph-panel">
            {selectedNodeId ? (
              <ErrorBoundary>
                <CodeGraph
                  nodes={filteredNodes}
                  edges={filteredEdges}
                  onNodeClick={handleNodeClick}
                  onBack={handleBack}
                />
              </ErrorBoundary>
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
              <ErrorBoundary>
                <MultiTraceCoordinator
                  traces={animationTraces}
                  isPlaying={isPlaying}
                  onGlobalStepChange={(traceId, stepId) => {
                    console.log(`Trace ${traceId} - 当前步骤:`, stepId);
                  }}
                />
              </ErrorBoundary>
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
