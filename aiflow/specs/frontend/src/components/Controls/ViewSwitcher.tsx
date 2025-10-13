/**
 * View Switcher - 视图切换器组件
 *
 * 提供不同可视化模式的切换界面
 * 支持：代码结构图、序列图、流程图、逐步执行
 */

import React from 'react';
import { useVisualizationStore, ViewMode } from '../../stores/visualizationStore';
import { useAnalysisStore } from '../../stores/analysisStore';
import './ViewSwitcher.css';

interface ViewOption {
  id: ViewMode;
  label: string;
  icon: string;
  description: string;
  requiredData: 'structure' | 'trace' | 'both';
}

const VIEW_OPTIONS: ViewOption[] = [
  {
    id: 'structure',
    label: '代码结构图',
    icon: '📐',
    description: '展示代码架构和依赖关系',
    requiredData: 'structure',
  },
  {
    id: 'sequence',
    label: '序列图',
    icon: '📊',
    description: '展示组件间的消息传递',
    requiredData: 'trace',
  },
  {
    id: 'flowchart',
    label: '流程图',
    icon: '🔀',
    description: '展示执行流程和控制流',
    requiredData: 'trace',
  },
  {
    id: 'step-by-step',
    label: '逐步执行',
    icon: '🐾',
    description: '逐行展示代码执行过程',
    requiredData: 'trace',
  },
];

export const ViewSwitcher: React.FC = () => {
  const currentView = useVisualizationStore((state) => state.currentView);
  const setView = useVisualizationStore((state) => state.setView);
  const analysisData = useAnalysisStore((state) => state.analysisData);

  // 检查数据可用性
  const hasStructureData = !!analysisData?.code_structure;
  const hasTraceData = !!analysisData?.execution_trace?.traceable_units?.length;

  // 判断视图是否可用
  const isViewAvailable = (view: ViewOption): boolean => {
    switch (view.requiredData) {
      case 'structure':
        return hasStructureData;
      case 'trace':
        return hasTraceData;
      case 'both':
        return hasStructureData && hasTraceData;
      default:
        return false;
    }
  };

  return (
    <div className="view-switcher">
      {/* 紧凑模式 - 标签式切换 */}
      <div className="view-tabs">
        {VIEW_OPTIONS.map((view) => {
          const isAvailable = isViewAvailable(view);
          const isActive = currentView === view.id;

          return (
            <button
              key={view.id}
              className={`view-tab ${isActive ? 'active' : ''} ${
                !isAvailable ? 'disabled' : ''
              }`}
              onClick={() => isAvailable && setView(view.id)}
              disabled={!isAvailable}
              title={
                isAvailable
                  ? view.description
                  : `需要${
                      view.requiredData === 'structure'
                        ? '代码结构数据'
                        : view.requiredData === 'trace'
                        ? '执行轨迹数据'
                        : '完整数据'
                    }`
              }
            >
              <span className="tab-icon">{view.icon}</span>
              <span className="tab-label">{view.label}</span>
              {!isAvailable && <span className="tab-lock">🔒</span>}
            </button>
          );
        })}
      </div>

      {/* 展开模式 - 卡片式选择 */}
      <div className="view-cards">
        {VIEW_OPTIONS.map((view) => {
          const isAvailable = isViewAvailable(view);
          const isActive = currentView === view.id;

          return (
            <div
              key={view.id}
              className={`view-card ${isActive ? 'active' : ''} ${
                !isAvailable ? 'disabled' : ''
              }`}
              onClick={() => isAvailable && setView(view.id)}
            >
              {!isAvailable && <div className="card-lock-overlay">🔒</div>}

              <div className="card-icon">{view.icon}</div>
              <div className="card-content">
                <h3 className="card-title">{view.label}</h3>
                <p className="card-description">{view.description}</p>
              </div>

              {isActive && <div className="card-active-indicator">✓</div>}

              {!isAvailable && (
                <div className="card-unavailable-hint">
                  {view.requiredData === 'structure'
                    ? '需要代码结构数据'
                    : view.requiredData === 'trace'
                    ? '需要执行轨迹数据'
                    : '需要完整数据'}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* 数据可用性提示 */}
      <div className="data-status">
        <div className={`status-item ${hasStructureData ? 'available' : 'unavailable'}`}>
          <span className="status-icon">
            {hasStructureData ? '✓' : '✕'}
          </span>
          <span className="status-label">代码结构数据</span>
        </div>

        <div className={`status-item ${hasTraceData ? 'available' : 'unavailable'}`}>
          <span className="status-icon">
            {hasTraceData ? '✓' : '✕'}
          </span>
          <span className="status-label">执行轨迹数据</span>
        </div>
      </div>
    </div>
  );
};
