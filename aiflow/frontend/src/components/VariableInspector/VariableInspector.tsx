import { useState } from 'react';
import './VariableInspector.css';

interface VariableSnapshot {
  stepIndex: number;
  stepId: string;
  variables: {
    global?: Record<string, string>;
    local?: Record<string, string>;
    parameter?: Record<string, string>;
  };
}

interface VariableInspectorProps {
  variableHistory: VariableSnapshot[];
  currentStepIndex: number;
}

export function VariableInspector({ variableHistory, currentStepIndex }: VariableInspectorProps) {
  const [selectedVariable, setSelectedVariable] = useState<string | null>(null);
  const [selectedScope, setSelectedScope] = useState<'global' | 'local' | 'parameter' | null>(null);

  // 获取当前步骤的变量状态
  const currentSnapshot = variableHistory.find(s => s.stepIndex === currentStepIndex);

  // 🔧 保留以备将来使用 - 获取所有唯一的变量名
  // const getAllVariables = (scope: 'global' | 'local' | 'parameter'): string[] => {
  //   const varSet = new Set<string>();
  //   variableHistory.forEach(snapshot => {
  //     const vars = snapshot.variables[scope];
  //     if (vars) {
  //       Object.keys(vars).forEach(key => varSet.add(key));
  //     }
  //   });
  //   return Array.from(varSet).sort();
  // };

  // 获取变量的历史值
  const getVariableHistory = (varName: string, scope: 'global' | 'local' | 'parameter') => {
    return variableHistory.map(snapshot => ({
      stepIndex: snapshot.stepIndex,
      stepId: snapshot.stepId,
      value: snapshot.variables[scope]?.[varName] || 'undefined',
    }));
  };

  // 渲染变量历史表
  const renderVariableHistory = () => {
    if (!selectedVariable || !selectedScope) {
      return (
        <div className="no-selection">
          <p>👈 点击左侧变量查看历史变化</p>
        </div>
      );
    }

    const history = getVariableHistory(selectedVariable, selectedScope);

    return (
      <div className="variable-history">
        <h5>
          📊 {selectedScope === 'global' ? '全局' : selectedScope === 'local' ? '局部' : '参数'} - {selectedVariable}
        </h5>
        <table className="history-table">
          <thead>
            <tr>
              <th>步骤</th>
              <th>Step ID</th>
              <th>值</th>
              <th>变化</th>
            </tr>
          </thead>
          <tbody>
            {history.map((item, index) => {
              const previousValue = index > 0 ? history[index - 1]?.value : null;
              const hasChanged = previousValue && previousValue !== item.value;
              const isCurrent = item.stepIndex === currentStepIndex;

              return (
                <tr key={index} className={isCurrent ? 'current-step' : ''}>
                  <td>{item.stepIndex + 1}</td>
                  <td className="step-id">{item.stepId}</td>
                  <td className="value-cell">
                    <code>{item.value}</code>
                  </td>
                  <td className="change-indicator">
                    {hasChanged && <span className="changed">🔄 Changed</span>}
                    {!hasChanged && previousValue && <span className="unchanged">━ Same</span>}
                    {!previousValue && <span className="new">✨ New</span>}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div className="variable-inspector-container">
      <div className="inspector-header">
        <h4>🔍 变量检查器</h4>
        <span className="current-step-label">
          步骤 {currentStepIndex + 1}
        </span>
      </div>

      <div className="inspector-content">
        {/* 左侧：当前变量列表 */}
        <div className="variables-list">
          {currentSnapshot && currentSnapshot.variables.global && (
            <div className="variable-group">
              <h5>🌐 全局变量</h5>
              <ul>
                {Object.entries(currentSnapshot.variables.global).map(([key, value]) => (
                  <li
                    key={key}
                    className={selectedVariable === key && selectedScope === 'global' ? 'selected' : ''}
                    onClick={() => {
                      setSelectedVariable(key);
                      setSelectedScope('global');
                    }}
                  >
                    <span className="var-name">{key}</span>
                    <span className="var-value">{value as string}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {currentSnapshot && currentSnapshot.variables.local && (
            <div className="variable-group">
              <h5>📍 局部变量</h5>
              <ul>
                {Object.entries(currentSnapshot.variables.local).map(([key, value]) => (
                  <li
                    key={key}
                    className={selectedVariable === key && selectedScope === 'local' ? 'selected' : ''}
                    onClick={() => {
                      setSelectedVariable(key);
                      setSelectedScope('local');
                    }}
                  >
                    <span className="var-name">{key}</span>
                    <span className="var-value">{value as string}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {currentSnapshot && currentSnapshot.variables.parameter && (
            <div className="variable-group">
              <h5>🎯 参数变量</h5>
              <ul>
                {Object.entries(currentSnapshot.variables.parameter).map(([key, value]) => (
                  <li
                    key={key}
                    className={selectedVariable === key && selectedScope === 'parameter' ? 'selected' : ''}
                    onClick={() => {
                      setSelectedVariable(key);
                      setSelectedScope('parameter');
                    }}
                  >
                    <span className="var-name">{key}</span>
                    <span className="var-value">{value as string}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {!currentSnapshot && (
            <div className="no-variables">
              <p>当前步骤无变量数据</p>
            </div>
          )}
        </div>

        {/* 右侧：变量历史 */}
        <div className="variable-history-panel">
          {renderVariableHistory()}
        </div>
      </div>
    </div>
  );
}
