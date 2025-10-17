import { useState, useEffect, useMemo } from 'react';
import { ExecutionTrace } from '../../types/protocol';
import { ExecutionTimeline } from '../ExecutionTimeline/ExecutionTimeline';
import { VariableInspector } from '../VariableInspector/VariableInspector';
import './ExecutionAnimation.css';

interface ExecutionAnimationProps {
  trace: ExecutionTrace;
  isPlaying: boolean;
  onStepChange?: (stepId: string) => void;
  controlCommand?: { command: string; value?: any } | null;
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
  const enrichedSteps = useMemo(() => {
    return steps.map((step: any, index: number) => {
      // 尝试找到对应的 event（通过序号匹配或ID匹配）
      const correspondingEvent = events[index] || events.find((e: any) =>
        e.event_id.includes(`${index + 1}`) || e.event_id.includes(step.id)
      );

      return {
        ...step,
        // 注入详细的执行信息
        source_location: correspondingEvent?.source_location,
        operation_detail: correspondingEvent?.operation_detail,
        operation_type: correspondingEvent?.operation_type,
        input_data: correspondingEvent?.input_data,
        output_data: correspondingEvent?.output_data,
        tcu_cost: step.tcu_cost || correspondingEvent?.duration_tcu,
        event_id: correspondingEvent?.event_id
      };
    });
  }, [steps, events]);

  // 动画播放逻辑
  useEffect(() => {
    if (!isPlaying || currentStepIndex >= steps.length) return;

    const timer = setTimeout(() => {
      const step = steps[currentStepIndex];
      if (!step) return; // Guard against undefined

      // 标记当前步骤为已执行
      setExecutedSteps(prev => new Set([...prev, step.id]));
      
      // 记录分支ID
      if (step.type === 'process' && 'branch_id' in step) {
        setActiveBranches(prev => new Set([...prev, (step as any).branch_id]));
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
    if (!controlCommand) return;

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
    return steps.map((step: any, index: number) => ({
      id: step.id,
      description: step.description || step.label || `步骤 ${index + 1}`,
      index: index,
      type: step.type
    }));
  }, [steps]);

  // 创建变量历史数据 - 支持 Per-Step 变量追踪
  // 🆕 Phase 4.2: 优先使用每个步骤自己的 variables 字段
  const variableHistory = useMemo(() => {
    return steps.map((step: any, index: number) => {
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
        if (id) newExecutedSteps.add(id);
      }
      setExecutedSteps(newExecutedSteps);

      // 通知父组件
      const targetStep = steps[stepIndex];
      if (targetStep) onStepChange?.(targetStep.id);
    }
  };

  // 获取步骤样式类名
  const getStepClassName = (step: any, index: number): string => {
    const classes = ['flowchart-step', `step-${step.type}`];
    
    if (index === currentStepIndex) classes.push('current');
    if (executedSteps.has(step.id)) classes.push('executed');
    if (step.branch_id && activeBranches.has(step.branch_id)) {
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
            const stepData = step as any;
            const isDivergence = stepData.type === 'decision';
            const isConvergence = enrichedSteps.some((s: any) =>
              s.true_branch === stepData.id || s.false_branch === stepData.id
            );

            return (
              <div key={stepData.id} className="step-wrapper">
                {/* 步骤节点 */}
                <div className={getStepClassName(stepData, index)}>
                  <div className="step-icon">{getStepIcon(stepData.type)}</div>
                  <div className="step-content">
                    <div className="step-header">
                      <div className="step-id">{stepData.id}</div>
                      {stepData.node_id && (
                        <div className="step-node-ref" title="执行的节点">
                          📍 {stepData.node_id}
                        </div>
                      )}
                    </div>
                    <div className="step-description">{stepData.description || stepData.label || `步骤 ${index + 1}`}</div>

                    {/* 🆕 详细操作信息 */}
                    {stepData.operation_detail && (
                      <div className="operation-detail">
                        <strong>操作:</strong> {stepData.operation_detail}
                      </div>
                    )}

                    {/* 🆕 源代码位置 */}
                    {stepData.source_location && (
                      <div className="source-location">
                        <div className="file-info">
                          📄 <code>{stepData.source_location.file}</code>
                          {stepData.source_location.line && (
                            <span className="line-number">:{stepData.source_location.line}</span>
                          )}
                        </div>
                        {stepData.source_location.code_snippet && (
                          <pre className="code-snippet">
                            <code>{stepData.source_location.code_snippet}</code>
                          </pre>
                        )}
                      </div>
                    )}

                    {/* 🆕 输入输出数据 */}
                    {(stepData.input_data || stepData.output_data) && (
                      <div className="data-flow">
                        {stepData.input_data && (
                          <div className="data-item input">
                            <span className="data-label">输入:</span>
                            <code className="data-value">{stepData.input_data}</code>
                          </div>
                        )}
                        {stepData.output_data && (
                          <div className="data-item output">
                            <span className="data-label">输出:</span>
                            <code className="data-value">{stepData.output_data}</code>
                          </div>
                        )}
                      </div>
                    )}

                    {/* 性能指标 */}
                    {stepData.tcu_cost && (
                      <div className="performance-metrics">
                        <span className={`tcu-badge ${stepData.is_bottleneck ? 'bottleneck' : ''}`}>
                          ⏱️ {stepData.tcu_cost} TCU
                          {stepData.operation_type && ` (${stepData.operation_type})`}
                          {stepData.is_bottleneck && ' ⚠️ 瓶颈'}
                        </span>
                      </div>
                    )}

                    {stepData.condition && (
                      <div className="step-condition">
                        <strong>条件:</strong> {stepData.condition}
                      </div>
                    )}
                    {stepData.branch_id && (
                      <div className="branch-badge">
                        分支 {stepData.branch_id}
                      </div>
                    )}
                  </div>
                </div>

                {/* 连接线 */}
                {index < steps.length - 1 && (
                  <div className="step-connector">
                    {/* Fork节点：并发分叉 */}
                    {stepData.type === 'fork' ? (
                      <div className="fork-connector concurrent">
                        <div className="fork-line branch-1">
                          <span className="fork-label">🔀 分支 {stepData.concurrent_branches || 2}</span>
                        </div>
                        <div className="fork-line branch-2">
                          <span className="fork-label">⚡ 并发执行</span>
                        </div>
                      </div>
                    ) : /* Join节点：并发汇合 */
                    stepData.type === 'join' ? (
                      <div className="join-connector">
                        <div className="join-symbol">🔗</div>
                        {stepData.waits_for && stepData.waits_for.length > 0 && (
                          <span className="join-label">等待 {stepData.waits_for.length} 个分支</span>
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
      {variableHistory.length > 0 && variableHistory[currentStepIndex]?.callStack?.length > 0 && (
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
