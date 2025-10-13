/**
 * App Layout - 主应用布局组件
 *
 * 提供整体页面结构：Header + Sidebar + Main Content
 * 管理文件加载、主题切换、全局导航
 */

import React, { useState, useCallback } from 'react';
import { useAnalysisStore } from '../../stores/analysisStore';
import { useVisualizationStore } from '../../stores/visualizationStore';
import { loadFromFile, loadFromURL, exportToFile } from '../../utils/dataLoader';
import type { AnalysisResult } from '../../types/protocol';
import './AppLayout.css';

interface AppLayoutProps {
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  // 状态管理
  const analysisData = useAnalysisStore((state) => state.analysisData);
  const setAnalysisData = useAnalysisStore((state) => state.setAnalysisData);
  const clearAnalysisData = useAnalysisStore((state) => state.clearAnalysisData);

  const theme = useVisualizationStore((state) => state.theme);
  const toggleTheme = useVisualizationStore((state) => state.toggleTheme);
  const currentView = useVisualizationStore((state) => state.currentView);

  // 文件上传处理
  const handleFileUpload = useCallback(async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsLoading(true);
    setLoadError(null);

    try {
      const result = await loadFromFile(file, {
        validate: true,
        onProgress: (progress) => {
          console.log(`Loading progress: ${progress}%`);
        },
      });

      if (!result.success || !result.data) {
        throw new Error(result.error || 'Failed to load file');
      }

      setAnalysisData(result.data);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setLoadError(errorMessage);
      console.error('File load error:', error);
    } finally {
      setIsLoading(false);
    }
  }, [setAnalysisData]);

  // URL 加载处理
  const handleURLLoad = useCallback(async () => {
    const url = prompt('请输入 JSON 文件的 URL:');
    if (!url) return;

    setIsLoading(true);
    setLoadError(null);

    try {
      const result = await loadFromURL(url, { validate: true });

      if (!result.success || !result.data) {
        throw new Error(result.error || 'Failed to load URL');
      }

      setAnalysisData(result.data);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setLoadError(errorMessage);
      console.error('URL load error:', error);
    } finally {
      setIsLoading(false);
    }
  }, [setAnalysisData]);

  // 导出数据
  const handleExport = useCallback(() => {
    if (!analysisData) return;

    const filename = `aiflow-analysis-${Date.now()}.json`;
    exportToFile(analysisData, filename);
  }, [analysisData]);

  // 清除数据
  const handleClear = useCallback(() => {
    if (confirm('确定要清除当前数据吗？')) {
      clearAnalysisData();
      setLoadError(null);
    }
  }, [clearAnalysisData]);

  return (
    <div className={`app-layout ${theme === 'dark' ? 'dark-theme' : 'light-theme'}`}>
      {/* Header */}
      <header className="app-header">
        <div className="header-left">
          <h1 className="app-title">
            <span className="title-icon">🚀</span>
            AIFlow
          </h1>
          <span className="app-subtitle">无外壳 MCP Tools · AI 分析可视化平台</span>
        </div>

        <div className="header-right">
          {/* 文件操作 */}
          <div className="header-actions">
            <label className="btn btn-primary">
              <input
                type="file"
                accept=".json,.json.gz"
                onChange={handleFileUpload}
                style={{ display: 'none' }}
                disabled={isLoading}
              />
              📁 打开文件
            </label>

            <button
              className="btn btn-secondary"
              onClick={handleURLLoad}
              disabled={isLoading}
            >
              🌐 加载 URL
            </button>

            {analysisData && (
              <>
                <button
                  className="btn btn-secondary"
                  onClick={handleExport}
                >
                  💾 导出
                </button>

                <button
                  className="btn btn-secondary"
                  onClick={handleClear}
                >
                  🗑️ 清除
                </button>
              </>
            )}
          </div>

          {/* 主题切换 */}
          <button
            className="btn btn-icon"
            onClick={toggleTheme}
            title={theme === 'dark' ? '切换到亮色主题' : '切换到暗色主题'}
          >
            {theme === 'dark' ? '☀️' : '🌙'}
          </button>

          {/* 侧边栏切换 */}
          <button
            className="btn btn-icon"
            onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
            title={isSidebarCollapsed ? '展开侧边栏' : '收起侧边栏'}
          >
            {isSidebarCollapsed ? '☰' : '✕'}
          </button>
        </div>
      </header>

      {/* 加载状态 */}
      {isLoading && (
        <div className="loading-overlay">
          <div className="loading-spinner"></div>
          <p className="loading-text">正在加载数据...</p>
        </div>
      )}

      {/* 错误提示 */}
      {loadError && (
        <div className="error-banner">
          <span className="error-icon">⚠️</span>
          <span className="error-message">{loadError}</span>
          <button
            className="error-close"
            onClick={() => setLoadError(null)}
          >
            ✕
          </button>
        </div>
      )}

      {/* 主内容区域 */}
      <main className="app-main">
        {/* 侧边栏 */}
        <aside className={`app-sidebar ${isSidebarCollapsed ? 'collapsed' : ''}`}>
          {!isSidebarCollapsed && (
            <div className="sidebar-content">
              {/* 项目信息 */}
              {analysisData && (
                <div className="sidebar-section">
                  <h3 className="sidebar-title">项目信息</h3>
                  <div className="project-info">
                    <div className="info-item">
                      <span className="info-label">项目ID:</span>
                      <span className="info-value" title={analysisData.metadata.project_id}>
                        {analysisData.metadata.project_id.slice(0, 8)}...
                      </span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">分析时间:</span>
                      <span className="info-value">
                        {new Date(analysisData.metadata.timestamp).toLocaleString('zh-CN')}
                      </span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">AI模型:</span>
                      <span className="info-value">{analysisData.metadata.ai_model}</span>
                    </div>
                    {analysisData.metadata.project_name && (
                      <div className="info-item">
                        <span className="info-label">项目名:</span>
                        <span className="info-value">{analysisData.metadata.project_name}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* 统计信息 */}
              {analysisData && (
                <div className="sidebar-section">
                  <h3 className="sidebar-title">数据统计</h3>
                  <div className="stats-grid">
                    <div className="stat-card">
                      <div className="stat-value">
                        {analysisData.code_structure?.nodes?.length || 0}
                      </div>
                      <div className="stat-label">代码节点</div>
                    </div>
                    <div className="stat-card">
                      <div className="stat-value">
                        {analysisData.code_structure?.edges?.length || 0}
                      </div>
                      <div className="stat-label">依赖关系</div>
                    </div>
                    <div className="stat-card">
                      <div className="stat-value">
                        {analysisData.behavior_metadata?.launch_buttons?.length || 0}
                      </div>
                      <div className="stat-label">启动按钮</div>
                    </div>
                    <div className="stat-card">
                      <div className="stat-value">
                        {analysisData.execution_trace?.traceable_units?.length || 0}
                      </div>
                      <div className="stat-label">执行轨迹</div>
                    </div>
                  </div>
                </div>
              )}

              {/* 当前视图 */}
              <div className="sidebar-section">
                <h3 className="sidebar-title">当前视图</h3>
                <div className="current-view-badge">
                  {getViewLabel(currentView)}
                </div>
              </div>

              {/* 帮助信息 */}
              <div className="sidebar-section">
                <h3 className="sidebar-title">快速帮助</h3>
                <div className="help-text">
                  <p>💡 上传 AI 分析生成的 JSON 文件开始可视化</p>
                  <p>🔄 使用视图切换器在不同可视化模式间切换</p>
                  <p>🎮 点击启动按钮查看执行动画</p>
                </div>
              </div>
            </div>
          )}
        </aside>

        {/* 内容区域 */}
        <div className="app-content">
          {analysisData ? (
            children
          ) : (
            <div className="empty-state">
              <div className="empty-icon">📊</div>
              <h2 className="empty-title">欢迎使用 AIFlow</h2>
              <p className="empty-description">
                请上传 AI 分析生成的 JSON 文件，或从 URL 加载数据
              </p>
              <div className="empty-actions">
                <label className="btn btn-primary btn-large">
                  <input
                    type="file"
                    accept=".json,.json.gz"
                    onChange={handleFileUpload}
                    style={{ display: 'none' }}
                  />
                  📁 选择文件
                </label>
                <button
                  className="btn btn-secondary btn-large"
                  onClick={handleURLLoad}
                >
                  🌐 从 URL 加载
                </button>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

// 工具函数
function getViewLabel(view: string): string {
  const labels: Record<string, string> = {
    structure: '📐 代码结构图',
    sequence: '📊 序列图',
    flowchart: '🔀 流程图',
    'step-by-step': '🐾 逐步执行',
  };
  return labels[view] || view;
}
