import { useEffect, useState } from 'react';
import { useAnalysisStore } from './stores/analysisStore';
import { CodeGraph } from './components/CodeGraph/CodeGraph';
import { TreeView } from './components/TreeView/TreeView';
import './App.css';

function App() {
  const { data, loading, error, setData, setLoading, setError } = useAnalysisStore();
  const [autoLoadAttempted, setAutoLoadAttempted] = useState(false);
  const [currentView, setCurrentView] = useState<'structure' | 'execution'>('structure');
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [filteredNodes, setFilteredNodes] = useState<any[]>([]);
  const [filteredEdges, setFilteredEdges] = useState<any[]>([]);

  // 自动加载 analysis.json
  useEffect(() => {
    if (!autoLoadAttempted && !data) {
      setAutoLoadAttempted(true);
      setLoading(true);

      fetch('/analysis.json')
        .then(res => {
          if (!res.ok) throw new Error('分析数据未找到');
          return res.json();
        })
        .then(jsonData => {
          setData(jsonData);
          console.log('✅ 自动加载分析数据成功', jsonData);
        })
        .catch(err => {
          console.log('⏳ 等待分析数据生成...', err.message);
          setError('等待分析数据生成... 运行 /ac:analyze <项目名> 开始分析');
        });
    }
  }, [autoLoadAttempted, data, setData, setLoading, setError]);

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
          <code>/ac:analyze &lt;项目名&gt;</code>
          <p className="example">例如: /ac:analyze NewPipe-dev</p>
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
              <li>在 Claude Code 中运行: <code>/ac:analyze &lt;项目名&gt;</code></li>
              <li>等待分析完成</li>
              <li>查看可视化结果</li>
            </ol>
          </div>
        </div>
      </div>
    );
  }

  const { metadata, code_structure } = data;

  // 处理节点点击 - 动态过滤显示相关节点
  const handleNodeClick = (nodeId: string) => {
    console.log('节点点击:', nodeId);
    setSelectedNodeId(nodeId);

    const allNodes = code_structure.nodes;
    const allEdges = code_structure.edges;

    // 找到被点击的节点
    const clickedNode = allNodes.find((n: any) => n.id === nodeId);
    if (!clickedNode) return;

    // 根据节点类型决定显示策略
    let nodesToShow: any[] = [];
    let edgesToShow: any[] = [];

    if (clickedNode.stereotype === 'system') {
      // 点击系统节点：显示所有模块
      nodesToShow = allNodes.filter((n: any) =>
        n.stereotype === 'system' || n.stereotype === 'module'
      );
      edgesToShow = allEdges.filter((e: any) =>
        nodesToShow.some((n: any) => n.id === e.source) &&
        nodesToShow.some((n: any) => n.id === e.target)
      );
    } else if (clickedNode.stereotype === 'module') {
      // 点击模块节点：显示该模块下的所有类
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
      // 点击类节点：显示该类的所有方法和关系
      const methodNodes = allNodes.filter((n: any) =>
        n.stereotype === 'function' && n.parent_class_id === nodeId
      );
      nodesToShow = [clickedNode, ...methodNodes];

      // 显示方法之间的调用关系
      edgesToShow = allEdges.filter((e: any) =>
        nodesToShow.some((n: any) => n.id === e.source) &&
        nodesToShow.some((n: any) => n.id === e.target)
      );
    } else if (clickedNode.stereotype === 'function') {
      // 点击方法节点：显示该方法调用的其他方法
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
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-left">
          <h1>🚀 AIFlow</h1>
          <span className="project-name">{metadata.project_name}</span>
        </div>
        <div className="header-center">
          <button
            className={`view-btn ${currentView === 'structure' ? 'active' : ''}`}
            onClick={() => setCurrentView('structure')}
          >
            📊 代码结构
          </button>
          <button
            className={`view-btn ${currentView === 'execution' ? 'active' : ''}`}
            onClick={() => setCurrentView('execution')}
          >
            🎬 执行动画
          </button>
        </div>
        <div className="header-right">
          <span className="protocol-version">v{metadata.protocol_version}</span>
          <span className="timestamp">{new Date(metadata.timestamp).toLocaleString('zh-CN')}</span>
        </div>
      </header>

      <main className="app-main">
        {currentView === 'structure' ? (
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
                />
              ) : (
                <div className="graph-placeholder">
                  <div className="placeholder-content">
                    <h2>👈 点击左侧树节点查看详情</h2>
                    <p>选择系统、模块、类或方法节点</p>
                    <p>右侧将显示对应的关系图</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="execution-view">
            <div className="execution-placeholder">
              <h2>🎬 执行动画视图</h2>
              <p>点击左侧启动按钮查看动画</p>
              {selectedButton && (
                <p className="selected">
                  已选择: {behavior_metadata.launch_buttons.find(b => b.id === selectedButton)?.name}
                </p>
              )}
              <div className="coming-soon">
                <p>🚧 执行动画功能开发中...</p>
                <ul>
                  <li>✅ 代码结构图 - 已完成</li>
                  <li>✅ 启动按钮 - 已完成</li>
                  <li>⏳ 流程图动画 - 开发中</li>
                  <li>⏳ 序列图动画 - 开发中</li>
                  <li>⏳ 逐步执行 - 开发中</li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>🚀 AIFlow - 无外壳 MCP Tools · AI 分析可视化平台</p>
      </footer>
    </div>
  );
}

export default App;
