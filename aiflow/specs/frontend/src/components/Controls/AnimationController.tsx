/**
 * Animation Controller - 动画控制器组件
 *
 * 提供执行动画的播放控制
 * 支持：播放、暂停、停止、步进、速度调节
 */

import React, { useEffect, useState } from 'react';
import { useVisualizationStore } from '../../stores/visualizationStore';
import { useAnalysisStore } from '../../stores/analysisStore';
import './AnimationController.css';

export const AnimationController: React.FC = () => {
  const [totalSteps, setTotalSteps] = useState(0);

  // 状态管理
  const animationState = useVisualizationStore((state) => state.animationState);
  const currentStep = useVisualizationStore((state) => state.currentStep);
  const animationSpeed = useVisualizationStore((state) => state.animationSpeed);

  const playAnimation = useVisualizationStore((state) => state.playAnimation);
  const pauseAnimation = useVisualizationStore((state) => state.pauseAnimation);
  const stopAnimation = useVisualizationStore((state) => state.stopAnimation);
  const setCurrentStep = useVisualizationStore((state) => state.setCurrentStep);
  const setAnimationSpeed = useVisualizationStore((state) => state.setAnimationSpeed);

  const selectedTraceId = useAnalysisStore((state) => state.selectedTraceId);
  const analysisData = useAnalysisStore((state) => state.analysisData);

  // 计算总步数
  useEffect(() => {
    if (!selectedTraceId || !analysisData) {
      setTotalSteps(0);
      return;
    }

    const trace = analysisData.execution_trace?.traceable_units?.find(
      (t) => t.id === selectedTraceId
    );

    if (!trace) {
      setTotalSteps(0);
      return;
    }

    // 尝试从不同格式获取步数
    const stepTrace = trace.traces?.find((t) => t.format === 'step_by_step');
    if (stepTrace) {
      const data = stepTrace.data as any;
      setTotalSteps(data.steps?.length || 0);
      return;
    }

    const flowchartTrace = trace.traces?.find((t) => t.format === 'flowchart');
    if (flowchartTrace) {
      const data = flowchartTrace.data as any;
      setTotalSteps(data.steps?.length || 0);
      return;
    }

    const sequenceTrace = trace.traces?.find((t) => t.format === 'sequence');
    if (sequenceTrace) {
      const data = sequenceTrace.data as any;
      setTotalSteps(data.messages?.length || 0);
      return;
    }

    setTotalSteps(0);
  }, [selectedTraceId, analysisData]);

  // 播放/暂停切换
  const handlePlayPause = () => {
    if (animationState === 'playing') {
      pauseAnimation();
    } else {
      playAnimation();
    }
  };

  // 上一步
  const handlePrevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  // 下一步
  const handleNextStep = () => {
    if (currentStep < totalSteps - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  // 跳转到开始
  const handleGoToStart = () => {
    setCurrentStep(0);
  };

  // 跳转到结束
  const handleGoToEnd = () => {
    setCurrentStep(totalSteps - 1);
  };

  // 速度调节
  const handleSpeedChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const speed = parseFloat(event.target.value);
    setAnimationSpeed(speed);
  };

  // 进度条拖动
  const handleProgressChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const step = parseInt(event.target.value);
    setCurrentStep(step);
  };

  // 格式化时间
  const formatTime = (step: number): string => {
    const seconds = Math.floor(step / animationSpeed);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  if (totalSteps === 0) {
    return (
      <div className="animation-controller animation-controller--disabled">
        <div className="controller-disabled-message">
          <span className="disabled-icon">⏸️</span>
          <span>请先选择一个执行轨迹</span>
        </div>
      </div>
    );
  }

  return (
    <div className="animation-controller">
      {/* 进度信息 */}
      <div className="controller-progress-info">
        <span className="progress-step">
          步骤 {currentStep + 1} / {totalSteps}
        </span>
        <span className="progress-time">
          {formatTime(currentStep)} / {formatTime(totalSteps)}
        </span>
      </div>

      {/* 进度条 */}
      <div className="controller-progress-bar">
        <input
          type="range"
          min={0}
          max={totalSteps - 1}
          value={currentStep}
          onChange={handleProgressChange}
          className="progress-slider"
        />
        <div
          className="progress-fill"
          style={{ width: `${((currentStep + 1) / totalSteps) * 100}%` }}
        ></div>
      </div>

      {/* 控制按钮 */}
      <div className="controller-buttons">
        {/* 跳转到开始 */}
        <button
          className="control-btn"
          onClick={handleGoToStart}
          disabled={currentStep === 0}
          title="跳转到开始"
        >
          ⏮️
        </button>

        {/* 上一步 */}
        <button
          className="control-btn"
          onClick={handlePrevStep}
          disabled={currentStep === 0}
          title="上一步"
        >
          ⏪
        </button>

        {/* 播放/暂停 */}
        <button
          className="control-btn control-btn--primary"
          onClick={handlePlayPause}
          title={animationState === 'playing' ? '暂停' : '播放'}
        >
          {animationState === 'playing' ? '⏸️' : '▶️'}
        </button>

        {/* 下一步 */}
        <button
          className="control-btn"
          onClick={handleNextStep}
          disabled={currentStep === totalSteps - 1}
          title="下一步"
        >
          ⏩
        </button>

        {/* 跳转到结束 */}
        <button
          className="control-btn"
          onClick={handleGoToEnd}
          disabled={currentStep === totalSteps - 1}
          title="跳转到结束"
        >
          ⏭️
        </button>

        {/* 停止 */}
        <button
          className="control-btn"
          onClick={stopAnimation}
          disabled={animationState === 'idle'}
          title="停止"
        >
          ⏹️
        </button>
      </div>

      {/* 速度控制 */}
      <div className="controller-speed">
        <label className="speed-label">
          <span className="speed-icon">⚡</span>
          <span className="speed-text">速度: {animationSpeed.toFixed(1)}x</span>
        </label>
        <input
          type="range"
          min={0.25}
          max={4}
          step={0.25}
          value={animationSpeed}
          onChange={handleSpeedChange}
          className="speed-slider"
        />
        <div className="speed-marks">
          <span>0.25x</span>
          <span>1x</span>
          <span>2x</span>
          <span>4x</span>
        </div>
      </div>
    </div>
  );
};
