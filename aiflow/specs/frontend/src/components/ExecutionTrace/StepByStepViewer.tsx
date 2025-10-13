/**
 * Step-by-Step Viewer - Monaco Editor 代码逐步执行查看器
 *
 * 使用 Monaco Editor 展示代码的逐步执行过程。
 * 支持高亮当前执行行、显示变量状态、代码标注。
 */

import React, { useEffect, useRef, useState } from 'react';
import * as monaco from 'monaco-editor';
import { useAnalysisStore } from '../../stores/analysisStore';
import { useVisualizationStore } from '../../stores/visualizationStore';
import './StepByStepViewer.css';

interface ExecutionStep {
  id: string;
  lineNumber: number;
  code: string;
  description: string;
  variables?: Record<string, any>; // 变量状态
  callStack?: string[]; // 调用栈
}

interface StepByStepData {
  file_path: string;
  file_content: string;
  language: string;
  steps: ExecutionStep[];
}

export const StepByStepViewer: React.FC = () => {
  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [decorations, setDecorations] = useState<string[]>([]);

  // 状态管理
  const selectedTraceId = useAnalysisStore((state) => state.selectedTraceId);
  const analysisData = useAnalysisStore((state) => state.analysisData);
  const theme = useVisualizationStore((state) => state.theme);

  // 当前步骤（用于动画）
  const currentStep = useVisualizationStore((state) => state.currentStep);
  const animationState = useVisualizationStore((state) => state.animationState);
  const setCurrentStep = useVisualizationStore((state) => state.setCurrentStep);

  // 获取步进数据
  const [stepData, setStepData] = useState<StepByStepData | null>(null);

  useEffect(() => {
    if (!selectedTraceId) return;

    const trace = analysisData?.execution_trace?.traceable_units?.find(
      (t) => t.id === selectedTraceId
    );

    if (!trace) return;

    const stepTrace = trace.traces?.find((t) => t.format === 'step_by_step');
    if (!stepTrace) return;

    setStepData(stepTrace.data as unknown as StepByStepData);
  }, [selectedTraceId, analysisData]);

  // 初始化 Monaco Editor
  useEffect(() => {
    if (!containerRef.current || !stepData) return;

    // 创建编辑器
    const editor = monaco.editor.create(containerRef.current, {
      value: stepData.file_content,
      language: stepData.language || 'javascript',
      theme: theme === 'dark' ? 'vs-dark' : 'vs-light',
      readOnly: true,
      minimap: { enabled: true },
      lineNumbers: 'on',
      glyphMargin: true,
      folding: true,
      scrollBeyondLastLine: false,
      automaticLayout: true,
    });

    editorRef.current = editor;

    // 清理
    return () => {
      editor.dispose();
    };
  }, [stepData, theme]);

  // 更新当前步骤的高亮
  useEffect(() => {
    if (!editorRef.current || !stepData) return;

    const step = stepData.steps[currentStep];
    if (!step) return;

    // 清除旧的装饰
    const newDecorations = editorRef.current.deltaDecorations(
      decorations,
      [
        // 高亮当前执行行
        {
          range: new monaco.Range(step.lineNumber, 1, step.lineNumber, 1),
          options: {
            isWholeLine: true,
            className: 'current-execution-line',
            glyphMarginClassName: 'current-execution-glyph',
            hoverMessage: { value: `**当前步骤**: ${step.description}` },
          },
        },
        // 高亮前面已执行的行
        ...stepData.steps
          .slice(0, currentStep)
          .map((s) => ({
            range: new monaco.Range(s.lineNumber, 1, s.lineNumber, 1),
            options: {
              isWholeLine: true,
              className: 'executed-line',
            },
          })),
      ]
    );

    setDecorations(newDecorations);

    // 滚动到当前行
    editorRef.current.revealLineInCenter(step.lineNumber);
  }, [currentStep, stepData]);

  // 播放动画
  useEffect(() => {
    if (animationState !== 'playing' || !stepData) return;

    const interval = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev >= stepData.steps.length - 1) {
          // 播放结束
          return prev;
        }
        return prev + 1;
      });
    }, 1000); // 每秒执行一步

    return () => clearInterval(interval);
  }, [animationState, stepData]);

  if (!selectedTraceId) {
    return (
      <div className="step-viewer-empty">
        <p>请先选择一个执行轨迹</p>
      </div>
    );
  }

  if (!stepData) {
    return (
      <div className="step-viewer-empty">
        <p>该轨迹没有步进式执行数据</p>
      </div>
    );
  }

  const currentStepData = stepData.steps[currentStep];

  return (
    <div className="step-viewer">
      {/* 编辑器容器 */}
      <div className="step-viewer__editor" ref={containerRef}></div>

      {/* 侧边栏 - 步骤信息 */}
      <div className="step-viewer__sidebar">
        {/* 文件信息 */}
        <div className="sidebar-section">
          <h3 className="sidebar-title">文件信息</h3>
          <div className="file-info">
            <div className="file-path">{stepData.file_path}</div>
            <div className="file-language">{stepData.language}</div>
          </div>
        </div>

        {/* 当前步骤 */}
        <div className="sidebar-section">
          <h3 className="sidebar-title">当前步骤</h3>
          <div className="current-step-info">
            <div className="step-number">
              步骤 {currentStep + 1} / {stepData.steps.length}
            </div>
            <div className="step-description">{currentStepData?.description}</div>
            <div className="step-line">行 {currentStepData?.lineNumber}</div>
          </div>
        </div>

        {/* 变量状态 */}
        {currentStepData?.variables && (
          <div className="sidebar-section">
            <h3 className="sidebar-title">变量状态</h3>
            <div className="variables-list">
              {Object.entries(currentStepData.variables).map(([name, value]) => (
                <div key={name} className="variable-item">
                  <span className="variable-name">{name}:</span>
                  <span className="variable-value">
                    {JSON.stringify(value)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 调用栈 */}
        {currentStepData?.callStack && currentStepData.callStack.length > 0 && (
          <div className="sidebar-section">
            <h3 className="sidebar-title">调用栈</h3>
            <div className="call-stack-list">
              {currentStepData.callStack.map((frame, index) => (
                <div
                  key={index}
                  className={`call-stack-item ${index === 0 ? 'active' : ''}`}
                >
                  <span className="stack-index">{index + 1}.</span>
                  <span className="stack-frame">{frame}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 步骤列表 */}
        <div className="sidebar-section">
          <h3 className="sidebar-title">所有步骤</h3>
          <div className="steps-list">
            {stepData.steps.map((step, index) => (
              <div
                key={step.id}
                className={`step-item ${index === currentStep ? 'active' : ''} ${
                  index < currentStep ? 'executed' : ''
                }`}
                onClick={() => setCurrentStep(index)}
              >
                <div className="step-item-number">{index + 1}</div>
                <div className="step-item-content">
                  <div className="step-item-line">行 {step.lineNumber}</div>
                  <div className="step-item-description">{step.description}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
