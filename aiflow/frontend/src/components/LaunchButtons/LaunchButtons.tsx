import { useState } from 'react';
import { LaunchButton } from '../../types/protocol';
import { useWebSocket } from '../../hooks/useWebSocket';
import './LaunchButtons.css';

interface LaunchButtonsProps {
  buttons: LaunchButton[];
  onButtonClick: (buttonId: string) => void;
  onAnalyzeClick?: (buttonId: string) => void;  // 🆕 触发分析的回调
}

export function LaunchButtons({ buttons, onButtonClick, onAnalyzeClick }: LaunchButtonsProps) {
  const [expandedMacro, setExpandedMacro] = useState<Set<string>>(new Set());
  const [selectedButton, setSelectedButton] = useState<string | null>(null);
  const [analyzingButton, setAnalyzingButton] = useState<string | null>(null);

  // 🆕 WebSocket 连接状态
  const { isConnected, startAnalysis } = useWebSocket();

  // 分离macro和micro按钮
  const macroButtons = buttons.filter(b => b.type === 'macro' && !b.parent_button_id);

  const toggleMacro = (macroId: string) => {
    const newExpanded = new Set(expandedMacro);
    if (newExpanded.has(macroId)) {
      newExpanded.delete(macroId);
    } else {
      newExpanded.add(macroId);
    }
    setExpandedMacro(newExpanded);
  };

  const handleButtonClick = (buttonId: string) => {
    setSelectedButton(buttonId);
    onButtonClick(buttonId);
  };

  // 🆕 处理分析触发
  const handleAnalyzeClick = (e: React.MouseEvent, buttonId: string) => {
    e.stopPropagation();  // 阻止触发 handleButtonClick

    if (!isConnected) {
      alert('❌ 请先连接到 MCP Server');
      return;
    }

    // 从 localStorage 获取上次使用的项目路径
    const lastProjectPath = localStorage.getItem('aiflow_project_path') || '';
    const projectPath = prompt('请输入项目路径:', lastProjectPath);

    if (!projectPath) {
      return;  // 用户取消
    }

    // 保存项目路径
    localStorage.setItem('aiflow_project_path', projectPath);

    // 触发分析
    const button = buttons.find(b => b.id === buttonId);
    const projectName = button?.name || 'Unknown Project';

    setAnalyzingButton(buttonId);
    startAnalysis(buttonId, projectPath, projectName);

    // 通知父组件
    onAnalyzeClick?.(buttonId);

    console.log(`🔍 触发分析: ${buttonId} (${projectPath})`);
  };

  const getMicroButtons = (macroId: string): LaunchButton[] => {
    const macro = buttons.find(b => b.id === macroId);
    if (!macro || !macro.child_button_ids) {return [];}

    return macro.child_button_ids
      .map(childId => buttons.find(b => b.id === childId))
      .filter(Boolean) as LaunchButton[];
  };

  const getButtonIcon = (button: LaunchButton): string => {
    if (button.icon) {return button.icon;}

    // 根据按钮名称智能推荐图标
    const name = button.name.toLowerCase();
    if (name.includes('rest') || name.includes('api') || name.includes('http')) {return '🌐';}
    if (name.includes('kafka') || name.includes('消息')) {return '📨';}
    if (name.includes('断言') || name.includes('验证')) {return '✅';}
    if (name.includes('加载') || name.includes('读取')) {return '📁';}
    if (name.includes('执行') || name.includes('测试')) {return '▶️';}
    if (name.includes('报告') || name.includes('生成')) {return '📊';}
    if (name.includes('生产') || name.includes('发送')) {return '📤';}
    if (name.includes('消费') || name.includes('接收')) {return '📥';}

    return button.type === 'macro' ? '🎯' : '⚡';
  };

  return (
    <div className="launch-buttons-container">
      <div className="buttons-header">
        <h3>🚀 启动按钮</h3>
        <span className="buttons-count">
          {macroButtons.length} 个宏观流程 · {buttons.length - macroButtons.length} 个微观步骤
        </span>
      </div>

      <div className="buttons-list">
        {macroButtons.map(macro => {
          const isExpanded = expandedMacro.has(macro.id);
          const isSelected = selectedButton === macro.id;
          const microButtons = getMicroButtons(macro.id);

          return (
            <div key={macro.id} className="button-group">
              {/* Macro按钮 */}
              <div
                className={`launch-button macro ${isSelected ? 'selected' : ''} ${analyzingButton === macro.id ? 'analyzing' : ''}`}
                onClick={() => handleButtonClick(macro.id)}
              >
                <div className="button-main">
                  <span className="button-icon">{getButtonIcon(macro)}</span>
                  <div className="button-content">
                    <div className="button-name">{macro.name}</div>
                    {macro.description && (
                      <div className="button-description">{macro.description}</div>
                    )}
                    {macro.metadata?.estimated_duration_ms && (
                      <div className="button-meta">
                        <span className="duration">⏱️ {macro.metadata.estimated_duration_ms}ms</span>
                      </div>
                    )}
                  </div>

                  {/* 🆕 分析按钮 (Phase 5.2) */}
                  <button
                    className={`analyze-button ${!isConnected ? 'disabled' : ''}`}
                    onClick={(e) => handleAnalyzeClick(e, macro.id)}
                    disabled={!isConnected || analyzingButton === macro.id}
                    title={isConnected ? '触发 AI 分析' : '请先连接 MCP Server'}
                  >
                    {analyzingButton === macro.id ? (
                      <span className="analyzing-spinner">⏳</span>
                    ) : (
                      '🔍'
                    )}
                  </button>

                  {microButtons.length > 0 && (
                    <button
                      className={`expand-button ${isExpanded ? 'expanded' : ''}`}
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleMacro(macro.id);
                      }}
                      aria-label={isExpanded ? '收起' : '展开'}
                    >
                      <svg width="16" height="16" viewBox="0 0 16 16">
                        <path
                          d="M4 6 L8 10 L12 6"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                      </svg>
                    </button>
                  )}
                </div>
              </div>

              {/* Micro按钮 (展开时显示) */}
              {isExpanded && microButtons.length > 0 && (
                <div className="micro-buttons-container">
                  {microButtons.map((micro, index) => {
                    const isMicroSelected = selectedButton === micro.id;
                    return (
                      <div
                        key={micro.id}
                        className={`launch-button micro ${isMicroSelected ? 'selected' : ''}`}
                        onClick={() => handleButtonClick(micro.id)}
                      >
                        <div className="button-main">
                          <span className="step-number">{index + 1}</span>
                          <span className="button-icon">{getButtonIcon(micro)}</span>
                          <div className="button-content">
                            <div className="button-name">{micro.name}</div>
                            {micro.description && (
                              <div className="button-description">{micro.description}</div>
                            )}
                            {micro.metadata?.estimated_duration_ms && (
                              <div className="button-meta">
                                <span className="duration">⏱️ {micro.metadata.estimated_duration_ms}ms</span>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
