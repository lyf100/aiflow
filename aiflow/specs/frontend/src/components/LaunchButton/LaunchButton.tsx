/**
 * Launch Button - 嵌套启动按钮组件
 *
 * 这是 AIFlow 的核心创新：嵌套式行为启动。
 * - 大按钮（Macro）：系统级多流程联动
 * - 小按钮（Micro）：子模块独立业务流程
 */

import React, { useState } from 'react';
import { useAnalysisStore } from '../../stores/analysisStore';
import { useVisualizationStore } from '../../stores/visualizationStore';
import type { LaunchButton as LaunchButtonType } from '../../types/protocol';
import './LaunchButton.css';

interface LaunchButtonProps {
  button: LaunchButtonType;
  depth?: number; // 嵌套深度（用于缩进）
}

export const LaunchButton: React.FC<LaunchButtonProps> = ({
  button,
  depth = 0,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  // 状态管理
  const analysisData = useAnalysisStore((state) => state.analysisData);
  const selectedButtonId = useAnalysisStore((state) => state.selectedButtonId);
  const selectButton = useAnalysisStore((state) => state.selectButton);

  const playAnimation = useVisualizationStore((state) => state.playAnimation);
  const animationState = useVisualizationStore((state) => state.animationState);

  // 获取子按钮
  const childButtons = button.child_button_ids
    ? button.child_button_ids
        .map((childId) =>
          analysisData?.behavior_metadata?.launch_buttons?.find(
            (b) => b.id === childId
          )
        )
        .filter(Boolean) as LaunchButtonType[]
    : [];

  const hasChildren = childButtons.length > 0;

  // 处理按钮点击
  const handleButtonClick = (e: React.MouseEvent) => {
    e.stopPropagation();

    // 选中按钮
    selectButton(button.id);

    // 开始播放动画
    if (button.traceable_unit_id) {
      playAnimation();
    }
  };

  // 处理展开/折叠
  const handleToggleExpand = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsExpanded(!isExpanded);
  };

  // 获取按钮图标
  const getButtonIcon = () => {
    if (button.icon) {
      return button.icon;
    }

    // 默认图标
    switch (button.type) {
      case 'macro':
        return '🚀';
      case 'micro':
        return '⚡';
      default:
        return '▶️';
    }
  };

  // 获取按钮样式类
  const getButtonClassName = () => {
    const classes = ['launch-button'];

    // 类型样式
    classes.push(`launch-button--${button.type}`);

    // 层级样式
    if (button.level) {
      classes.push(`launch-button--${button.level}`);
    }

    // 选中状态
    if (selectedButtonId === button.id) {
      classes.push('launch-button--selected');
    }

    // 播放状态
    if (selectedButtonId === button.id && animationState === 'playing') {
      classes.push('launch-button--playing');
    }

    // 禁用状态
    if (!button.traceable_unit_id) {
      classes.push('launch-button--disabled');
    }

    return classes.join(' ');
  };

  return (
    <div
      className="launch-button-container"
      style={{ marginLeft: `${depth * 24}px` }}
    >
      {/* 主按钮 */}
      <div className={getButtonClassName()} onClick={handleButtonClick}>
        {/* 展开/折叠图标 */}
        {hasChildren && (
          <button
            className="launch-button__expand"
            onClick={handleToggleExpand}
            aria-label={isExpanded ? '折叠' : '展开'}
          >
            <span className={`expand-icon ${isExpanded ? 'expanded' : ''}`}>
              ▶
            </span>
          </button>
        )}

        {/* 按钮图标 */}
        <span className="launch-button__icon">{getButtonIcon()}</span>

        {/* 按钮内容 */}
        <div className="launch-button__content">
          <div className="launch-button__name">{button.name}</div>
          {button.description && (
            <div className="launch-button__description">
              {button.description}
            </div>
          )}
        </div>

        {/* 按钮徽章 */}
        <div className="launch-button__badges">
          {/* 类型徽章 */}
          <span className={`badge badge--${button.type}`}>
            {button.type === 'macro' ? '大' : '小'}
          </span>

          {/* 层级徽章 */}
          {button.level && (
            <span className="badge badge--level">
              {getLevelLabel(button.level)}
            </span>
          )}

          {/* AI 置信度 */}
          {button.metadata?.ai_confidence && (
            <span
              className="badge badge--confidence"
              title={`AI 置信度: ${(button.metadata.ai_confidence * 100).toFixed(0)}%`}
            >
              {(button.metadata.ai_confidence * 100).toFixed(0)}%
            </span>
          )}
        </div>

        {/* 播放指示器 */}
        {selectedButtonId === button.id && animationState === 'playing' && (
          <div className="launch-button__playing-indicator">
            <div className="pulse-ring"></div>
            <div className="pulse-ring pulse-ring--delayed"></div>
          </div>
        )}
      </div>

      {/* 元数据提示 */}
      {button.metadata && (
        <div className="launch-button-metadata">
          {button.metadata.estimated_duration && (
            <span className="metadata-item" title="预估执行时间">
              ⏱️ {formatDuration(button.metadata.estimated_duration)}
            </span>
          )}
          {button.metadata.requires_input && (
            <span className="metadata-item" title="需要用户输入">
              📝 需要输入
            </span>
          )}
          {button.metadata.has_side_effects && (
            <span className="metadata-item" title="有副作用">
              ⚠️ 有副作用
            </span>
          )}
        </div>
      )}

      {/* 子按钮（递归渲染） */}
      {hasChildren && isExpanded && (
        <div className="launch-button__children">
          {childButtons.map((child) => (
            <LaunchButton key={child.id} button={child} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  );
};

// 工具函数

function getLevelLabel(level: string): string {
  const labels: Record<string, string> = {
    system: '系统',
    module: '模块',
    component: '组件',
    function: '函数',
  };
  return labels[level] || level;
}

function formatDuration(ms: number): string {
  if (ms < 1000) {
    return `${ms}ms`;
  } else if (ms < 60000) {
    return `${(ms / 1000).toFixed(1)}s`;
  } else {
    return `${(ms / 60000).toFixed(1)}min`;
  }
}
