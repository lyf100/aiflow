/**
 * WebSocket 连接状态指示器
 * 显示连接状态、重连次数和控制按钮
 */

import { useWebSocket } from '../../hooks/useWebSocket';
import './ConnectionStatus.css';

export function ConnectionStatus() {
  const { isConnected, reconnectAttempts, connect, disconnect } = useWebSocket();

  return (
    <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
      <div className="status-indicator">
        <span className="status-dot"></span>
        <span className="status-text">
          {isConnected ? '已连接 MCP Server' : '未连接'}
        </span>
        {reconnectAttempts > 0 && !isConnected && (
          <span className="reconnect-info">
            (重连中... 第 {reconnectAttempts} 次)
          </span>
        )}
      </div>

      <div className="status-actions">
        {!isConnected ? (
          <button
            className="connect-btn"
            onClick={connect}
            title="连接到 MCP Server"
          >
            🔌 连接
          </button>
        ) : (
          <button
            className="disconnect-btn"
            onClick={disconnect}
            title="断开连接"
          >
            🔌 断开
          </button>
        )}
      </div>
    </div>
  );
}
