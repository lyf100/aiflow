/**
 * Launch Button List - 启动按钮列表组件
 *
 * 展示所有顶层启动按钮，并支持嵌套显示。
 */

import React, { useMemo, useState } from 'react';
import { useAnalysisStore } from '../../stores/analysisStore';
import { LaunchButton } from './LaunchButton';
import type { LaunchButton as LaunchButtonType } from '../../types/protocol';
import './LaunchButtonList.css';

export const LaunchButtonList: React.FC = () => {
  const analysisData = useAnalysisStore((state) => state.analysisData);
  const [filter, setFilter] = useState<'all' | 'macro' | 'micro'>('all');
  const [searchQuery, setSearchQuery] = useState('');

  // 获取所有顶层按钮（没有父按钮的按钮）
  const topLevelButtons = useMemo(() => {
    if (!analysisData?.behavior_metadata?.launch_buttons) return [];

    return analysisData.behavior_metadata.launch_buttons.filter(
      (button) => !button.parent_button_id
    );
  }, [analysisData]);

  // 过滤按钮
  const filteredButtons = useMemo(() => {
    let buttons = topLevelButtons;

    // 类型过滤
    if (filter !== 'all') {
      buttons = buttons.filter((button) => button.type === filter);
    }

    // 搜索过滤
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      buttons = buttons.filter(
        (button) =>
          button.name.toLowerCase().includes(query) ||
          button.description?.toLowerCase().includes(query)
      );
    }

    return buttons;
  }, [topLevelButtons, filter, searchQuery]);

  // 统计信息
  const stats = useMemo(() => {
    const allButtons = analysisData?.behavior_metadata?.launch_buttons || [];
    return {
      total: allButtons.length,
      macro: allButtons.filter((b) => b.type === 'macro').length,
      micro: allButtons.filter((b) => b.type === 'micro').length,
    };
  }, [analysisData]);

  if (!analysisData) {
    return (
      <div className="launch-button-list-empty">
        <p>请先加载分析数据</p>
      </div>
    );
  }

  if (topLevelButtons.length === 0) {
    return (
      <div className="launch-button-list-empty">
        <p>未检测到启动按钮</p>
        <p className="hint">AI 未识别出可执行的功能单元</p>
      </div>
    );
  }

  return (
    <div className="launch-button-list">
      {/* 头部 */}
      <div className="launch-button-list__header">
        <h3 className="launch-button-list__title">启动按钮</h3>

        {/* 统计信息 */}
        <div className="launch-button-list__stats">
          <span className="stat-item">
            总计: <strong>{stats.total}</strong>
          </span>
          <span className="stat-item stat-item--macro">
            大按钮: <strong>{stats.macro}</strong>
          </span>
          <span className="stat-item stat-item--micro">
            小按钮: <strong>{stats.micro}</strong>
          </span>
        </div>
      </div>

      {/* 过滤和搜索 */}
      <div className="launch-button-list__filters">
        {/* 类型过滤 */}
        <div className="filter-group">
          <button
            className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            全部
          </button>
          <button
            className={`filter-btn ${filter === 'macro' ? 'active' : ''}`}
            onClick={() => setFilter('macro')}
          >
            大按钮
          </button>
          <button
            className={`filter-btn ${filter === 'micro' ? 'active' : ''}`}
            onClick={() => setFilter('micro')}
          >
            小按钮
          </button>
        </div>

        {/* 搜索框 */}
        <div className="search-box">
          <input
            type="text"
            placeholder="搜索按钮..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
          {searchQuery && (
            <button
              className="search-clear"
              onClick={() => setSearchQuery('')}
              aria-label="清除搜索"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* 按钮列表 */}
      <div className="launch-button-list__content">
        {filteredButtons.length === 0 ? (
          <div className="launch-button-list-empty">
            <p>未找到匹配的按钮</p>
          </div>
        ) : (
          filteredButtons.map((button) => (
            <LaunchButton key={button.id} button={button} depth={0} />
          ))
        )}
      </div>

      {/* 帮助提示 */}
      <div className="launch-button-list__help">
        <p className="help-text">
          💡 <strong>提示</strong>：点击按钮启动执行动画，点击 ▶ 展开子按钮
        </p>
      </div>
    </div>
  );
};
