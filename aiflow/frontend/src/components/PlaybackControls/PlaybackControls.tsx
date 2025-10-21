import { useState } from 'react';
import './PlaybackControls.css';

interface PlaybackControlsProps {
  isPlaying: boolean;
  onPlayPause: () => void;
  onReset: () => void;
  onStepForward?: () => void;
  onStepBackward?: () => void;
  speed: number;
  onSpeedChange: (speed: number) => void;
  currentStep: number;
  totalSteps: number;
  onProgressChange?: (step: number) => void;
}

export function PlaybackControls({
  isPlaying,
  onPlayPause,
  onReset,
  onStepForward,
  onStepBackward,
  speed,
  onSpeedChange,
  currentStep,
  totalSteps,
  onProgressChange
}: PlaybackControlsProps) {
  const [showSpeedMenu, setShowSpeedMenu] = useState(false);

  const speedOptions = [
    { value: 0.25, label: '0.25x' },
    { value: 0.5, label: '0.5x' },
    { value: 1, label: '1x' },
    { value: 1.5, label: '1.5x' },
    { value: 2, label: '2x' },
    { value: 3, label: '3x' }
  ];

  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!onProgressChange) {return;}

    const rect = e.currentTarget.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const percentage = clickX / rect.width;
    const targetStep = Math.floor(percentage * totalSteps);

    onProgressChange(Math.max(0, Math.min(targetStep, totalSteps - 1)));
  };

  return (
    <div className="playback-controls">
      <div className="controls-section primary-controls">
        {/* 步进后退 */}
        {onStepBackward && (
          <button
            className="control-btn step-btn"
            onClick={onStepBackward}
            disabled={currentStep === 0}
            title="上一步 (←)"
          >
            ⏮
          </button>
        )}

        {/* 播放/暂停 */}
        <button
          className="control-btn play-pause-btn"
          onClick={onPlayPause}
          title={isPlaying ? '暂停 (Space)' : '播放 (Space)'}
        >
          {isPlaying ? '⏸' : '▶️'}
        </button>

        {/* 步进前进 */}
        {onStepForward && (
          <button
            className="control-btn step-btn"
            onClick={onStepForward}
            disabled={currentStep >= totalSteps - 1}
            title="下一步 (→)"
          >
            ⏭
          </button>
        )}

        {/* 重置 */}
        <button
          className="control-btn reset-btn"
          onClick={onReset}
          title="重置 (R)"
        >
          🔄
        </button>
      </div>

      <div className="controls-section progress-section">
        {/* 步骤计数器 */}
        <span className="step-counter">
          {currentStep + 1} / {totalSteps}
        </span>

        {/* 进度条 */}
        <div
          className="progress-track"
          onClick={handleProgressClick}
          title="点击跳转到指定步骤"
        >
          <div
            className="progress-bar"
            style={{ width: `${((currentStep + 1) / totalSteps) * 100}%` }}
          />
          <div
            className="progress-thumb"
            style={{ left: `${((currentStep + 1) / totalSteps) * 100}%` }}
          />
        </div>
      </div>

      <div className="controls-section speed-controls">
        {/* 速度控制 */}
        <div className="speed-selector">
          <button
            className="control-btn speed-btn"
            onClick={() => setShowSpeedMenu(!showSpeedMenu)}
            title="播放速度"
          >
            ⚡ {speed}x
          </button>

          {showSpeedMenu && (
            <div className="speed-menu">
              {speedOptions.map(option => (
                <button
                  key={option.value}
                  className={`speed-option ${speed === option.value ? 'active' : ''}`}
                  onClick={() => {
                    onSpeedChange(option.value);
                    setShowSpeedMenu(false);
                  }}
                >
                  {option.label}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
