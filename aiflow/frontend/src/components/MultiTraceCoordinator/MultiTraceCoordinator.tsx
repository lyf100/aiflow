import { useState, useEffect, useRef } from 'react';
import { ExecutionTrace, FlowchartStep } from '../../types/protocol';
import { ExecutionAnimation } from '../ExecutionAnimation/ExecutionAnimation';
import { PlaybackControls } from '../PlaybackControls/PlaybackControls';
import './MultiTraceCoordinator.css';

// 🔧 类型安全: 播放控制命令接口
interface PlaybackControlCommand {
  command: 'stepForward' | 'stepBackward' | 'reset' | 'jumpToStep';
  value?: number;
}

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

  // 🆕 为每个trace创建独立的控制ref
  const controlCommandRefs = useRef<Array<PlaybackControlCommand | null>>(
    traces.map(() => null)
  );

  // 🆕 跟踪每个trace的当前步骤
  const [traceSteps, setTraceSteps] = useState<number[]>(traces.map(() => 0));

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
    const stepIndex = traceSteps[index];
    setCurrentStep(stepIndex ?? 0); // 恢复该trace的步骤位置，默认为0
  };

  // 🆕 计算累计时间戳（基于estimated_duration_ms）
  const calculateCumulativeTime = (steps: FlowchartStep[], upToIndex: number): number => {
    let cumulativeTime = 0;
    for (let i = 0; i <= upToIndex && i < steps.length; i++) {
      const step = steps[i];
      if (step) {
        cumulativeTime += step.estimated_duration_ms || 0;
      }
    }
    return cumulativeTime;
  };

  // 🆕 处理步骤变化 - 实现synchronized模式的同步逻辑
  const handleStepChange = (traceIndex: number, stepId: string) => {
    const trace = traces[traceIndex];
    if (!trace) {return;}

    onGlobalStepChange?.(trace.trace_id, stepId);

    // 🆕 在synchronized模式下,同步其他traces的播放位置
    if (syncMode === 'synchronized' && traces.length > 1) {
      const currentSteps = trace.flowchart?.steps || [];
      const currentStepIndex = currentSteps.findIndex(s => s.id === stepId);

      if (currentStepIndex !== -1) {
        // 计算当前步骤的累计时间戳
        const currentTimestamp = calculateCumulativeTime(currentSteps, currentStepIndex);

        console.log(`🔗 同步模式: Trace ${traceIndex} 到达步骤 ${stepId} (累计时间: ${currentTimestamp}ms)`);

        // 同步其他traces到相同的累计时间位置
        traces.forEach((otherTrace, otherIndex) => {
          if (otherIndex === traceIndex) {return;} // 跳过当前trace

          const otherSteps = otherTrace.flowchart?.steps || [];

          // 找到最接近当前累计时间的步骤
          let closestStepIndex = 0;
          let minTimeDiff = Infinity;

          otherSteps.forEach((_step, index) => {
            const stepCumulativeTime = calculateCumulativeTime(otherSteps, index);
            const timeDiff = Math.abs(stepCumulativeTime - currentTimestamp);

            if (timeDiff < minTimeDiff) {
              minTimeDiff = timeDiff;
              closestStepIndex = index;
            }
          });

          // 发送同步命令到其他ExecutionAnimation
          controlCommandRefs.current[otherIndex] = {
            command: 'jumpToStep',
            value: closestStepIndex
          };

          console.log(`  ↪️ 同步 Trace ${otherIndex} 到步骤 ${closestStepIndex} (时间差: ${minTimeDiff}ms)`);
        });
      }
    }

    // 更新当前trace的步骤记录
    setTraceSteps(prev => {
      const updated = [...prev];
      const stepIndex = (trace.flowchart?.steps || []).findIndex(s => s.id === stepId);
      if (stepIndex !== -1) {
        updated[traceIndex] = stepIndex;
      }
      return updated;
    });
  };

  // 播放控制处理
  const handlePlayPause = () => {
    setGlobalPlaybackState(!globalPlaybackState);
  };

  const handleReset = () => {
    // 重置当前激活的trace
    controlCommandRefs.current[activeTraceIndex] = { command: 'reset' };
    setCurrentStep(0);

    // 在synchronized模式下，重置所有traces
    if (syncMode === 'synchronized') {
      controlCommandRefs.current.forEach((_, index) => {
        controlCommandRefs.current[index] = { command: 'reset' };
      });
      setTraceSteps(traces.map(() => 0));
    }
  };

  const handleStepForward = () => {
    controlCommandRefs.current[activeTraceIndex] = { command: 'stepForward' };
  };

  const handleStepBackward = () => {
    controlCommandRefs.current[activeTraceIndex] = { command: 'stepBackward' };
  };

  const handleSpeedChange = (newSpeed: number) => {
    setPlaybackSpeed(newSpeed);
  };

  const handleProgressChange = (step: number) => {
    controlCommandRefs.current[activeTraceIndex] = { command: 'jumpToStep', value: step };
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
    if (!singleTrace) {return null;}  // 🔧 修复: 确保trace存在

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
          controlCommand={controlCommandRefs.current[0]}
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
            controlCommand={controlCommandRefs.current[activeTraceIndex]}
            onCurrentStepUpdate={handleCurrentStepUpdate}
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
