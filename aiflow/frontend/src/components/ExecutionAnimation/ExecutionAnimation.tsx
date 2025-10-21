import { useState, useEffect, useMemo } from 'react';
import { ExecutionTrace, FlowchartStep, TimelineEvent } from '../../types/protocol';
import { ExecutionTimeline } from '../ExecutionTimeline/ExecutionTimeline';
import { VariableInspector } from '../VariableInspector/VariableInspector';
import './ExecutionAnimation.css';

// 🔧 类型安全: 播放控制命令接口
interface PlaybackControlCommand {
  command: 'stepForward' | 'stepBackward' | 'reset' | 'jumpToStep';
  value?: number;
}

// 🔧 类型安全: 扩展FlowchartStep以包含timeline event数据
interface EnrichedFlowchartStep extends FlowchartStep {
  source_location?: TimelineEvent['source_location'];
  operation_detail?: string;
  operation_type?: string;
  input_data?: string | number | boolean | null;
  output_data?: string | number | boolean | null;
  tcu_cost?: number;
  event_id?: string;
  node_id?: string;
  is_bottleneck?: boolean;
  true_branch?: string;
  false_branch?: string;
}

interface ExecutionAnimationProps {
  trace: ExecutionTrace;
  isPlaying: boolean;
  onStepChange?: (stepId: string) => void;
  controlCommand?: PlaybackControlCommand | null;
  onCurrentStepUpdate?: (stepIndex: number) => void;
}

export function ExecutionAnimation({
  trace,
  isPlaying,
  onStepChange,
  controlCommand,
  onCurrentStepUpdate
}: ExecutionAnimationProps) {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [executedSteps, setExecutedSteps] = useState<Set<string>>(new Set());
  const [activeBranches, setActiveBranches] = useState<Set<number>>(new Set());

  const steps = trace.flowchart?.steps || [];
  const events = trace.timeline_estimation?.events || [];

  // 🆕 将 timeline events 映射到 flowchart steps，获取详细执行信息
  const enrichedSteps = useMemo((): EnrichedFlowchartStep[] => {
    return steps.map((step, index) => {
      // 尝试找到对应的 event（通过序号匹配或ID匹配）
      const correspondingEvent = events[index] || events.find((e: TimelineEvent) =>
        e.event_id.includes(`${index + 1}`) || e.event_id.includes(step.id)
      );

      return {
        ...step,
        // 注入详细的执行信息
        source_location: correspondingEvent?.source_location,
        operation_detail: correspondingEvent?.operation_detail,
        operation_type: correspondingEvent?.operation_type,
        input_data: correspondingEvent?.input_data != null ? String(correspondingEvent.input_data) : undefined,
        output_data: correspondingEvent?.output_data != null ? String(correspondingEvent.output_data) : undefined,
        tcu_cost: step.estimated_duration_ms || correspondingEvent?.duration_tcu,
        event_id: correspondingEvent?.event_id
      };
    });
  }, [steps, events]);

  // 动画播放逻辑
  useEffect(() => {
    if (!isPlaying || currentStepIndex >= steps.length) {return;}

    const timer = setTimeout(() => {
      const step = steps[currentStepIndex];
      if (!step) {return;} // Guard against undefined

      // 标记当前步骤为已执行
      setExecutedSteps(prev => new Set([...prev, step.id]));

      // 记录分支ID (类型安全检查)
      if (step.type === 'process' && step.branch_id !== undefined) {
        setActiveBranches(prev => new Set([...prev, step.branch_id!]));
      }
      
      // 通知父组件
      onStepChange?.(step.id);
      
      // 移动到下一步
      if (currentStepIndex < steps.length - 1) {
        setCurrentStepIndex(currentStepIndex + 1);
      }
    }, 1500); // 每1.5秒执行一个步骤

    return () => clearTimeout(timer);
  }, [isPlaying, currentStepIndex, steps, onStepChange]);

  // 🆕 响应播放控制命令 (Previous/Next/Reset/Jump)
  useEffect(() => {
    if (!controlCommand) {return;}

    switch (controlCommand.command) {
      case 'stepForward':
        if (currentStepIndex < steps.length - 1) {
          handleTimelineStepClick(currentStepIndex + 1);
        }
        break;

      case 'stepBackward':
        if (currentStepIndex > 0) {
          handleTimelineStepClick(currentStepIndex - 1);
        }
        break;

      case 'reset':
        resetAnimation();
        break;

      case 'jumpToStep':
        if (typeof controlCommand.value === 'number') {
          handleTimelineStepClick(controlCommand.value);
        }
        break;
    }
  }, [controlCommand]);

  // 通知父组件当前步骤变化
  useEffect(() => {
    onCurrentStepUpdate?.(currentStepIndex);
  }, [currentStepIndex, onCurrentStepUpdate]);

  // 重置动画
  const resetAnimation = () => {
    setCurrentStepIndex(0);
    setExecutedSteps(new Set());
    setActiveBranches(new Set());
  };

  // 转换步骤数据为 ExecutionTimeline 格式
  const timelineSteps = useMemo(() => {
    return steps.map((step, index) => ({
      id: step.id,
      description: step.description || step.label || `步骤 ${index + 1}`,
      index: index,
      type: step.type
    }));
  }, [steps]);

  // 创建变量历史数据 - 支持 Per-Step 变量追踪
  // 🆕 Phase 4.2: 优先使用每个步骤自己的 variables 字段
  const variableHistory = useMemo(() => {
    return steps.map((step, index) => {
      // 优先使用 per-step 变量快照 (Phase 4.1+ 协议)
      if (step.variables) {
        return {
          stepIndex: index,
          stepId: step.id,
          variables: step.variables,  // 直接使用步骤自己的变量快照
          callStack: step.callStack || []  // 使用步骤自己的调用栈
        };
      }

      // 向后兼容：回退到 trace-level 变量快照 (旧协议)
      if (trace.variables_used) {
        return {
          stepIndex: index,
          stepId: step.id,
          variables: {
            global: trace.variables_used?.global,
            local: trace.variables_used?.local,
            parameter: trace.variables_used?.parameter
          },
          callStack: trace.call_stack || []
        };
      }

      // 无变量数据
      return {
        stepIndex: index,
        stepId: step.id,
        variables: {},
        callStack: []
      };
    });
  }, [steps, trace.variables_used, trace.call_stack]);

  // 处理时间轴点击 - 跳转到指定步骤
  const handleTimelineStepClick = (stepIndex: number) => {
    if (stepIndex >= 0 && stepIndex < steps.length) {
      setCurrentStepIndex(stepIndex);

      // 更新已执行步骤集合（包含当前步骤之前的所有步骤）
      const newExecutedSteps = new Set<string>();
      for (let i = 0; i <= stepIndex; i++) {
        const id = steps[i]?.id;
        if (id) {newExecutedSteps.add(id);}
      }
      setExecutedSteps(newExecutedSteps);

      // 通知父组件
      const targetStep = steps[stepIndex];
      if (targetStep) {onStepChange?.(targetStep.id);}
    }
  };

  // 获取步骤样式类名
  const getStepClassName = (step: FlowchartStep, index: number): string => {
    const classes = ['flowchart-step', `step-${step.type}`];

    if (index === currentStepIndex) {classes.push('current');}
    if (executedSteps.has(step.id)) {classes.push('executed');}
    if (step.branch_id !== undefined && activeBranches.has(step.branch_id)) {
      classes.push(`branch-${step.branch_id}`);
    }

    return classes.join(' ');
  };

  // 获取步骤图标
  const getStepIcon = (stepType: string): string => {
    const icons: Record<string, string> = {
      start: '▶️',
      process: '⚙️',
      decision: '🔀',
      end: '🏁',
      fork: '🔱',        // Fork节点：三叉戟表示分叉
      join: '🔗'         // Join节点：链接表示汇合
    };
    return icons[stepType] || '📍';
  };

  return (
    <div className="execution-animation-container">
      {/* 动画控制栏 */}
      <div className="animation-controls">
        <h3>🎬 {trace.trace_name || '执行动画'}</h3>
        <div className="controls-buttons">
          <button 
            className="control-btn reset"
            onClick={resetAnimation}
            title="重置动画"
          >
            🔄 重置
          </button>
          <div className="progress-info">
            <span className="step-counter">
              步骤 {currentStepIndex + 1} / {steps.length}
            </span>
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{ width: `${((currentStepIndex + 1) / steps.length) * 100}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* 🆕 执行时间轴 - D3.js可视化 */}
      <ExecutionTimeline
        steps={timelineSteps}
        currentStepIndex={currentStepIndex}
        onStepClick={handleTimelineStepClick}
      />

      {/* 流程图可视化 */}
      <div className="flowchart-container">
        <div className="flowchart-steps">
          {enrichedSteps.map((step, index) => {
            const isDivergence = step.type === 'decision';
            const isConvergence = enrichedSteps.some((s) =>
              s.true_branch === step.id || s.false_branch === step.id
            );

            return (
              <div key={step.id} className="step-wrapper">
                {/* 步骤节点 */}
                <div className={getStepClassName(step, index)}>
                  <div className="step-icon">{getStepIcon(step.type)}</div>
                  <div className="step-content">
                    <div className="step-header">
                      <div className="step-id">{step.id}</div>
                      {step.node_id && (
                        <div className="step-node-ref" title="执行的节点">
                          📍 {step.node_id}
                        </div>
                      )}
                    </div>
                    <div className="step-description">{step.description || step.label || `步骤 ${index + 1}`}</div>

                    {/* 🆕 详细操作信息 */}
                    {step.operation_detail && (
                      <div className="operation-detail">
                        <strong>操作:</strong> {step.operation_detail}
                      </div>
                    )}

                    {/* 🆕 源代码位置 */}
                    {step.source_location && (
                      <div className="source-location">
                        <div className="file-info">
                          📄 <code>{step.source_location.file}</code>
                          {step.source_location.line && (
                            <span className="line-number">:{step.source_location.line}</span>
                          )}
                        </div>
                        {step.source_location.code_snippet && (
                          <pre className="code-snippet">
                            <code>{step.source_location.code_snippet}</code>
                          </pre>
                        )}
                      </div>
                    )}

                    {/* 🆕 输入输出数据 */}
                    {(step.input_data || step.output_data) && (
                      <div className="data-flow">
                        {step.input_data && (
                          <div className="data-item input">
                            <span className="data-label">输入:</span>
                            <code className="data-value">{step.input_data}</code>
                          </div>
                        )}
                        {step.output_data && (
                          <div className="data-item output">
                            <span className="data-label">输出:</span>
                            <code className="data-value">{step.output_data}</code>
                          </div>
                        )}
                      </div>
                    )}

                    {/* 性能指标 */}
                    {step.tcu_cost && (
                      <div className="performance-metrics">
                        <span className={`tcu-badge ${step.is_bottleneck ? 'bottleneck' : ''}`}>
                          ⏱️ {step.tcu_cost} TCU
                          {step.operation_type && ` (${step.operation_type})`}
                          {step.is_bottleneck && ' ⚠️ 瓶颈'}
                        </span>
                      </div>
                    )}

                    {step.condition && (
                      <div className="step-condition">
                        <strong>条件:</strong> {step.condition}
                      </div>
                    )}
                    {step.branch_id !== undefined && (
                      <div className="branch-badge">
                        分支 {step.branch_id}
                      </div>
                    )}
                  </div>
                </div>

                {/* 连接线 */}
                {index < steps.length - 1 && (
                  <div className="step-connector">
                    {/* Fork节点：并发分叉 */}
                    {step.type === 'fork' ? (
                      <div className="fork-connector concurrent">
                        <div className="fork-line branch-1">
                          <span className="fork-label">🔀 分支 {step.concurrent_branches || 2}</span>
                        </div>
                        <div className="fork-line branch-2">
                          <span className="fork-label">⚡ 并发执行</span>
                        </div>
                      </div>
                    ) : /* Join节点：并发汇合 */
                    step.type === 'join' ? (
                      <div className="join-connector">
                        <div className="join-symbol">🔗</div>
                        {step.waits_for && step.waits_for.length > 0 && (
                          <span className="join-label">等待 {step.waits_for.length} 个分支</span>
                        )}
                      </div>
                    ) : /* Decision节点：条件分支 */
                    isDivergence ? (
                      <div className="fork-connector">
                        <div className="fork-line left">
                          <span className="fork-label">✓ True</span>
                        </div>
                        <div className="fork-line right">
                          <span className="fork-label">✗ False</span>
                        </div>
                      </div>
                    ) : isConvergence ? (
                      <div className="join-connector">
                        <div className="join-symbol">⬇</div>
                      </div>
                    ) : (
                      <div className="normal-connector">
                        <div className="connector-arrow">↓</div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* 🆕 变量检查器 - D3.js变量历史追踪 */}
      {variableHistory.length > 0 && (
        <VariableInspector
          variableHistory={variableHistory}
          currentStepIndex={currentStepIndex}
        />
      )}

      {/* 🆕 调用栈面板 - 显示当前步骤的调用栈 (Phase 4.2) */}
      {variableHistory.length > 0 && variableHistory[currentStepIndex]?.callStack && variableHistory[currentStepIndex]!.callStack.length > 0 && (
        <div className="callstack-panel">
          <h4>📚 调用栈 (步骤 {currentStepIndex + 1})</h4>
          <ol className="callstack-list">
            {variableHistory[currentStepIndex]!.callStack.map((call: string, index: number) => (
              <li key={index} className="callstack-item">
                <span className="stack-depth">{index + 1}</span>
                <span className="stack-function">{call}</span>
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}
