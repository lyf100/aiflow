import { useState } from 'react';
import type { LaunchButton } from '../../types/protocol';
import './LaunchButtons.css';

interface LaunchButtonsProps {
  buttons: LaunchButton[];
  onButtonClick?: (buttonId: string) => void;
}

export function LaunchButtons({ buttons, onButtonClick }: LaunchButtonsProps) {
  const [expandedButtons, setExpandedButtons] = useState<Set<string>>(new Set());

  // 构建按钮层级树
  const rootButtons = buttons.filter(btn => !btn.parent_button_id);

  const toggleExpand = (buttonId: string) => {
    setExpandedButtons(prev => {
      const newSet = new Set(prev);
      if (newSet.has(buttonId)) {
        newSet.delete(buttonId);
      } else {
        newSet.add(buttonId);
      }
      return newSet;
    });
  };

  const renderButton = (button: LaunchButton, depth: number = 0) => {
    const hasChildren = button.child_button_ids && button.child_button_ids.length > 0;
    const isExpanded = expandedButtons.has(button.id);
    const childButtons = hasChildren
      ? buttons.filter(btn => button.child_button_ids?.includes(btn.id))
      : [];

    return (
      <div key={button.id} className="launch-button-item" style={{ marginLeft: `${depth * 20}px` }}>
        <div
          className={`launch-button ${button.type} ${button.level}`}
          onClick={() => onButtonClick?.(button.id)}
        >
          <div className="button-header">
            {hasChildren && (
              <button
                className="expand-toggle"
                onClick={(e) => {
                  e.stopPropagation();
                  toggleExpand(button.id);
                }}
              >
                {isExpanded ? '▼' : '▶'}
              </button>
            )}
            <span className="button-icon">{button.icon || '▶️'}</span>
            <span className="button-name">{button.name}</span>
            <span className="button-badge">{button.level}</span>
          </div>

          {button.description && (
            <div className="button-description">{button.description}</div>
          )}

          {button.metadata?.ai_confidence && (
            <div className="button-meta">
              <span className="confidence">
                置信度: {(button.metadata.ai_confidence * 100).toFixed(0)}%
              </span>
              {button.metadata.estimated_duration && (
                <span className="duration">
                  预计: {button.metadata.estimated_duration}ms
                </span>
              )}
            </div>
          )}
        </div>

        {hasChildren && isExpanded && (
          <div className="child-buttons">
            {childButtons.map(childBtn => renderButton(childBtn, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="launch-buttons-container">
      <div className="buttons-header">
        <h3>🎯 启动按钮</h3>
        <span className="buttons-count">{buttons.length} 个按钮</span>
      </div>

      <div className="buttons-list">
        {rootButtons.length > 0 ? (
          rootButtons.map(btn => renderButton(btn))
        ) : (
          <div className="empty-state">
            <p>暂无启动按钮</p>
            <p className="hint">等待分析完成...</p>
          </div>
        )}
      </div>
    </div>
  );
}
