import { useState, useEffect, useRef } from 'react';
import { ExecutionTrace } from '../../types/protocol';
import { ExecutionAnimation } from '../ExecutionAnimation/ExecutionAnimation';
import { PlaybackControls } from '../PlaybackControls/PlaybackControls';
import './MultiTraceCoordinator.css';

interface MultiTraceCoordinatorProps {
  traces: ExecutionTrace[];
  isPlaying: boolean;
  onGlobalStepChange?: (traceId: string, stepId: string) => void;
}

export function MultiTraceCoordinator({ traces, isPlaying, onGlobalStepChange }: MultiTraceCoordinatorProps) {
  const [globalPlaybackState, setGlobalPlaybackState] = useState(isPlaying);
  const [activeTraceIndex, setActiveTraceIndex] = useState(0);
  const [syncMode, setSyncMode] = useState<'synchronized' | 'independent'>('synchronized');
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [currentStep, setCurrentStep] = useState(0);
  const [totalSteps, setTotalSteps] = useState(0);

  // 用于向ExecutionAnimation传递控制命令的ref
  const controlCommandRef = useRef<{ command: string; value?: any } | null>(null);

  // 全局播放控制：同步所有Trace的播放状态
  useEffect(() => {
    setGlobalPlaybackState(isPlaying);
  }, [isPlaying]);

  // 更新当前trace的总步骤数
  useEffect(() => {
    const activeTrace = traces[activeTraceIndex];
    if (activeTrace?.flowchart?.steps) {
      setTotalSteps(activeTrace.flowchart.steps.length);
    }
  }, [activeTraceIndex, traces]);

  // 处理Trace切换
  const handleTraceSwitch = (index: number) => {
    setActiveTraceIndex(index);
    setCurrentStep(0); // 重置步骤
  };

  // 处理步骤变化 - 用于同步协调
  const handleStepChange = (traceIndex: number, stepId: string) => {
    const trace = traces[traceIndex];
    if (!trace) return;  // 🔧 修复: 确保trace存在
    onGlobalStepChange?.(trace.trace_id, stepId);

    // TODO: 在synchronized模式下,同步其他traces的播放位置
    if (syncMode === 'synchronized') {
      // 未来可以实现跨trace的时间同步逻辑
      console.log(`🔗 同步模式: Trace ${traceIndex} 到达步骤 ${stepId}`);
    }
  };

  // 播放控制处理
  const handlePlayPause = () => {
    setGlobalPlaybackState(!globalPlaybackState);
  };

  const handleReset = () => {
    controlCommandRef.current = { command: 'reset' };
    setCurrentStep(0);
  };

  const handleStepForward = () => {
    controlCommandRef.current = { command: 'stepForward' };
  };

  const handleStepBackward = () => {
    controlCommandRef.current = { command: 'stepBackward' };
  };

  const handleSpeedChange = (newSpeed: number) => {
    setPlaybackSpeed(newSpeed);
  };

  const handleProgressChange = (step: number) => {
    controlCommandRef.current = { command: 'jumpToStep', value: step };
    setCurrentStep(step);
  };

  // 从ExecutionAnimation接收当前步骤更新
  const handleCurrentStepUpdate = (stepIndex: number) => {
    setCurrentStep(stepIndex);
  };

  // 渲染模式选择器
  const renderModeSelector = () => (
    <div className="mode-selector">
      <button
        className={`mode-btn ${syncMode === 'synchronized' ? 'active' : ''}`}
        onClick={() => setSyncMode('synchronized')}
        title="同步播放多个Trace"
      >
        🔗 同步模式
      </button>
      <button
        className={`mode-btn ${syncMode === 'independent' ? 'active' : ''}`}
        onClick={() => setSyncMode('independent')}
        title="独立播放每个Trace"
      >
        🔀 独立模式
      </button>
    </div>
  );

  // 单Trace模式：只有一个trace时直接显示
  if (traces.length === 1) {
    const singleTrace = traces[0];
    if (!singleTrace) return null;  // 🔧 修复: 确保trace存在

    return (
      <div className="multi-trace-coordinator single-trace">
        {/* 播放控制面板 */}
        <PlaybackControls
          isPlaying={globalPlaybackState}
          onPlayPause={handlePlayPause}
          onReset={handleReset}
          onStepForward={handleStepForward}
          onStepBackward={handleStepBackward}
          speed={playbackSpeed}
          onSpeedChange={handleSpeedChange}
          currentStep={currentStep}
          totalSteps={totalSteps}
          onProgressChange={handleProgressChange}
        />

        <ExecutionAnimation
          trace={singleTrace}
          isPlaying={globalPlaybackState}
          onStepChange={(stepId) => handleStepChange(0, stepId)}
          controlCommand={controlCommandRef.current}
          onCurrentStepUpdate={handleCurrentStepUpdate}
        />
      </div>
    );
  }

  // 多Trace模式：标签页 + 并排视图
  return (
    <div className="multi-trace-coordinator">
      {/* 全局控制栏 */}
      <div className="global-controls">
        <h3>🎬 多流程并发播放</h3>
        <div className="controls-group">
          {renderModeSelector()}
          <div className="trace-count">
            共 {traces.length} 个并发流程
          </div>
        </div>
      </div>

      {/* 播放控制面板 */}
      <PlaybackControls
        isPlaying={globalPlaybackState}
        onPlayPause={handlePlayPause}
        onReset={handleReset}
        onStepForward={handleStepForward}
        onStepBackward={handleStepBackward}
        speed={playbackSpeed}
        onSpeedChange={handleSpeedChange}
        currentStep={currentStep}
        totalSteps={totalSteps}
        onProgressChange={handleProgressChange}
      />

      {/* Trace切换标签 */}
      <div className="trace-tabs">
        {traces.map((trace, index) => (
          <button
            key={trace.trace_id}
            className={`trace-tab ${index === activeTraceIndex ? 'active' : ''}`}
            onClick={() => handleTraceSwitch(index)}
          >
            <span className="tab-icon">
              {index === activeTraceIndex ? '🎬' : '📹'}
            </span>
            <span className="tab-name">
              {trace.trace_name || `流程 ${index + 1}`}
            </span>
            {trace.flowchart?.steps && (
              <span className="tab-steps">
                {trace.flowchart.steps.length} 步
              </span>
            )}
          </button>
        ))}
      </div>

      {/* 当前激活的Trace动画 */}
      <div className="active-trace-container">
        {traces[activeTraceIndex] && (
          <ExecutionAnimation
            key={traces[activeTraceIndex].trace_id}
            trace={traces[activeTraceIndex]}
            isPlaying={globalPlaybackState}
            onStepChange={(stepId) => handleStepChange(activeTraceIndex, stepId)}
          />
        )}
      </div>

      {/* 未来扩展：并排视图模式 */}
      {/* {syncMode === 'synchronized' && (
        <div className="parallel-view">
          {traces.map((trace, index) => (
            <div key={trace.trace_id} className="parallel-trace">
              <ExecutionAnimation
                trace={trace}
                isPlaying={globalPlaybackState}
                onStepChange={(stepId) => handleStepChange(index, stepId)}
              />
            </div>
          ))}
        </div>
      )} */}
    </div>
  );
}
