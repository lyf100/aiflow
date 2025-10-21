/**
 * AnalysisProgress 组件
 *
 * 实时显示 MCP 五阶段分析进度
 * 显示当前阶段、进度百分比、预估剩余时间
 */

import { useAnalysisProgress } from '../../hooks/useWebSocket';
import './AnalysisProgress.css';

interface AnalysisProgressProps {
  buttonId: string;
  buttonName?: string;
}

const STAGE_NAMES = {
  1: '项目认知',
  2: '结构识别',
  3: '语义分析',
  4: '执行推理',
  5: '并发检测'
};

const STAGE_ICONS = {
  1: '🧠',
  2: '🏗️',
  3: '🔍',
  4: '⚡',
  5: '🔀'
};

export function AnalysisProgress({ buttonId, buttonName }: AnalysisProgressProps) {
  const {
    progress,
    isAnalyzing,
    stage,
    stageName: _stageName,  // 🔧 修复: 使用前缀_表示有意忽略
    progressPercent,
    message,
    estimatedTimeRemaining
  } = useAnalysisProgress(buttonId);

  if (!isAnalyzing && !progress) {
    return null; // 无分析进行中，不显示
  }

  // 格式化剩余时间
  const formatTimeRemaining = (ms: number | null): string => {
    if (!ms) {return '计算中...';}

    const seconds = Math.ceil(ms / 1000);
    if (seconds < 60) {return `${seconds}秒`;}

    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}分${remainingSeconds}秒`;
  };

  return (
    <div className="analysis-progress-container">
      <div className="progress-header">
        <div className="progress-title">
          <span className="progress-icon">🔍</span>
          <span className="progress-text">正在分析</span>
          {buttonName && <span className="button-name-badge">{buttonName}</span>}
        </div>
        <div className="progress-percent">{Math.round(progressPercent)}%</div>
      </div>

      {/* 五阶段进度条 */}
      <div className="stages-container">
        {[1, 2, 3, 4, 5].map((stageNum) => {
          const isCompleted = stage > stageNum;
          const isCurrent = stage === stageNum;
          const isPending = stage < stageNum;

          return (
            <div
              key={stageNum}
              className={`stage-item ${isCompleted ? 'completed' : ''} ${isCurrent ? 'current' : ''} ${isPending ? 'pending' : ''}`}
            >
              <div className="stage-icon">
                {isCompleted ? '✅' : STAGE_ICONS[stageNum as keyof typeof STAGE_ICONS]}
              </div>
              <div className="stage-info">
                <div className="stage-name">
                  Stage {stageNum}: {STAGE_NAMES[stageNum as keyof typeof STAGE_NAMES]}
                </div>
                {isCurrent && (
                  <div className="stage-status">
                    <div className="stage-progress-bar">
                      <div
                        className="stage-progress-fill"
                        style={{ width: `${progressPercent}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* 当前消息和剩余时间 */}
      {message && (
        <div className="progress-message">
          <span className="message-icon">💬</span>
          <span className="message-text">{message}</span>
        </div>
      )}

      {estimatedTimeRemaining && (
        <div className="time-remaining">
          <span className="time-icon">⏱️</span>
          <span className="time-text">
            预计剩余: {formatTimeRemaining(estimatedTimeRemaining)}
          </span>
        </div>
      )}

      {/* 整体进度条 */}
      <div className="overall-progress">
        <div className="overall-progress-bar">
          <div
            className="overall-progress-fill"
            style={{ width: `${(stage - 1) * 20 + progressPercent * 0.2}%` }}
          />
        </div>
        <div className="overall-progress-label">
          整体进度: {Math.round((stage - 1) * 20 + progressPercent * 0.2)}%
        </div>
      </div>
    </div>
  );
}
