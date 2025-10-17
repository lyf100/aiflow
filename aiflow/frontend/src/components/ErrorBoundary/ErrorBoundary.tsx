import { Component, ErrorInfo, ReactNode } from 'react';
import './ErrorBoundary.css';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

/**
 * React错误边界组件
 *
 * 功能:
 * - 捕获子组件树中的JavaScript错误
 * - 记录错误信息用于调试
 * - 显示友好的错误UI而不是白屏
 * - 提供错误恢复机制
 */
class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    // 更新state使下一次渲染能够显示降级UI
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // 记录错误信息
    console.error('🚨 ErrorBoundary捕获错误:', error);
    console.error('📍 错误组件栈:', errorInfo.componentStack);

    this.setState({
      error,
      errorInfo,
    });

    // TODO: 可以在这里将错误发送到错误监控服务
    // sendErrorToMonitoring(error, errorInfo);
  }

  handleReset = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render(): ReactNode {
    const { hasError, error, errorInfo } = this.state;
    const { children, fallback } = this.props;

    if (hasError) {
      // 如果提供了自定义fallback UI，使用它
      if (fallback) {
        return fallback;
      }

      // 默认错误UI
      return (
        <div className="error-boundary">
          <div className="error-boundary-container">
            <div className="error-boundary-icon">⚠️</div>
            <h1 className="error-boundary-title">糟糕，出现了一些问题</h1>
            <p className="error-boundary-message">
              AIFlow遇到了一个意外错误。我们已经记录了这个问题。
            </p>

            <div className="error-boundary-actions">
              <button
                className="error-boundary-button primary"
                onClick={this.handleReset}
              >
                🔄 重新尝试
              </button>
              <button
                className="error-boundary-button secondary"
                onClick={() => window.location.reload()}
              >
                🏠 刷新页面
              </button>
            </div>

            {import.meta.env.DEV && error && (
              <details className="error-boundary-details">
                <summary className="error-boundary-summary">
                  🐛 开发者信息 (仅在开发环境显示)
                </summary>
                <div className="error-boundary-debug">
                  <div className="error-section">
                    <h3>错误信息:</h3>
                    <pre className="error-text">{error.toString()}</pre>
                  </div>

                  {error.stack && (
                    <div className="error-section">
                      <h3>错误堆栈:</h3>
                      <pre className="error-stack">{error.stack}</pre>
                    </div>
                  )}

                  {errorInfo && (
                    <div className="error-section">
                      <h3>组件堆栈:</h3>
                      <pre className="error-stack">{errorInfo.componentStack}</pre>
                    </div>
                  )}
                </div>
              </details>
            )}
          </div>
        </div>
      );
    }

    return children;
  }
}

export default ErrorBoundary;
