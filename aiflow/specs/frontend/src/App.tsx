/**
 * App - 主应用组件
 *
 * AIFlow 可视化平台的入口组件
 * 整合所有子组件，提供完整的用户界面
 */

import React from 'react';
import { AppLayout } from './components/Layout/AppLayout';
import { ViewSwitcher } from './components/Controls/ViewSwitcher';
import { AnimationController } from './components/Controls/AnimationController';
import { CodeStructureGraph } from './components/CodeStructureGraph/CodeStructureGraph';
import { LaunchButtonList } from './components/LaunchButton/LaunchButtonList';
import { FlowchartViewer } from './components/ExecutionTrace/FlowchartViewer';
import { SequenceViewer } from './components/ExecutionTrace/SequenceViewer';
import { StepByStepViewer } from './components/ExecutionTrace/StepByStepViewer';
import { useVisualizationStore } from './stores/visualizationStore';
import './App.css';

export const App: React.FC = () => {
  const currentView = useVisualizationStore((state) => state.currentView);

  // 根据当前视图渲染对应的可视化组件
  const renderVisualization = () => {
    switch (currentView) {
      case 'structure':
        return (
          <div className="visualization-container">
            <div className="visualization-main">
              <CodeStructureGraph />
            </div>
            <div className="visualization-sidebar">
              <LaunchButtonList />
            </div>
          </div>
        );

      case 'sequence':
        return (
          <div className="visualization-container">
            <div className="visualization-main">
              <SequenceViewer />
            </div>
            <div className="visualization-controls">
              <AnimationController />
            </div>
          </div>
        );

      case 'flowchart':
        return (
          <div className="visualization-container">
            <div className="visualization-main">
              <FlowchartViewer />
            </div>
            <div className="visualization-controls">
              <AnimationController />
            </div>
          </div>
        );

      case 'step-by-step':
        return (
          <div className="visualization-container">
            <div className="visualization-main">
              <StepByStepViewer />
            </div>
            <div className="visualization-controls">
              <AnimationController />
            </div>
          </div>
        );

      default:
        return (
          <div className="visualization-error">
            <p>未知的视图类型: {currentView}</p>
          </div>
        );
    }
  };

  return (
    <AppLayout>
      <div className="app-workspace">
        {/* 视图切换器 */}
        <div className="workspace-header">
          <ViewSwitcher />
        </div>

        {/* 可视化内容 */}
        <div className="workspace-content">
          {renderVisualization()}
        </div>
      </div>
    </AppLayout>
  );
};

export default App;
