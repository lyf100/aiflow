/**
 * AIFlow WebSocket Service
 *
 * 管理与 MCP Server 的 WebSocket 实时连接
 * 支持：分析触发、进度监听、结果接收、自动重连
 */

export interface AnalysisRequest {
  type: 'start_analysis';
  button_id: string;
  project_path: string;
  project_name?: string;
}

export interface AnalysisProgress {
  type: 'progress';
  button_id: string;
  stage: number;  // 1-5
  stage_name: string;
  status: 'running' | 'completed' | 'error';
  message: string;
  progress_percent: number;  // 0-100
  estimated_time_remaining_ms?: number;
}

export interface AnalysisResult {
  type: 'result';
  button_id: string;
  success: boolean;
  data?: any;  // 分析结果 JSON
  error?: string;
}

export interface AnalysisError {
  type: 'error';
  button_id: string;
  error: string;
  stage?: number;
}

export type WebSocketMessage = AnalysisRequest | AnalysisProgress | AnalysisResult | AnalysisError;

export type ProgressCallback = (progress: AnalysisProgress) => void;
export type ResultCallback = (result: AnalysisResult) => void;
export type ErrorCallback = (error: AnalysisError) => void;
export type ConnectionStatusCallback = (connected: boolean) => void;

export class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 2000;  // 初始重连延迟 2 秒
  private reconnectTimer: number | null = null;  // 🔧 修复: 使用number类型代替NodeJS.Timeout
  private isIntentionalClose = false;

  // 回调函数集合
  private progressCallbacks = new Set<ProgressCallback>();
  private resultCallbacks = new Set<ResultCallback>();
  private errorCallbacks = new Set<ErrorCallback>();
  private connectionCallbacks = new Set<ConnectionStatusCallback>();

  // 消息队列（连接断开时缓存）
  private messageQueue: WebSocketMessage[] = [];

  constructor(
    private url: string = 'ws://localhost:8765/ws',
    _autoConnect: boolean = true  // 🔧 修复: 使用_前缀表示有意忽略
  ) {
    if (_autoConnect) {
      this.connect();
    }
  }

  /**
   * 建立 WebSocket 连接
   */
  public connect(): void {
    if (this.ws && (this.ws.readyState === WebSocket.CONNECTING || this.ws.readyState === WebSocket.OPEN)) {
      console.log('[WebSocket] 已经连接或正在连接中');
      return;
    }

    console.log(`[WebSocket] 正在连接到 ${this.url}...`);
    this.isIntentionalClose = false;

    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = this.handleOpen.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);
      this.ws.onerror = this.handleError.bind(this);
      this.ws.onclose = this.handleClose.bind(this);
    } catch (error) {
      console.error('[WebSocket] 连接失败:', error);
      this.scheduleReconnect();
    }
  }

  /**
   * 关闭连接
   */
  public disconnect(): void {
    this.isIntentionalClose = true;
    this.clearReconnectTimer();

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    this.notifyConnectionStatus(false);
  }

  /**
   * 发送分析请求
   */
  public startAnalysis(buttonId: string, projectPath: string, projectName?: string): void {
    const request: AnalysisRequest = {
      type: 'start_analysis',
      button_id: buttonId,
      project_path: projectPath,
      project_name: projectName
    };

    this.send(request);
  }

  /**
   * 注册进度回调
   */
  public onProgress(callback: ProgressCallback): () => void {
    this.progressCallbacks.add(callback);
    return () => this.progressCallbacks.delete(callback);
  }

  /**
   * 注册结果回调
   */
  public onResult(callback: ResultCallback): () => void {
    this.resultCallbacks.add(callback);
    return () => this.resultCallbacks.delete(callback);
  }

  /**
   * 注册错误回调
   */
  public onError(callback: ErrorCallback): () => void {
    this.errorCallbacks.add(callback);
    return () => this.errorCallbacks.delete(callback);
  }

  /**
   * 注册连接状态回调
   */
  public onConnectionStatus(callback: ConnectionStatusCallback): () => void {
    this.connectionCallbacks.add(callback);
    // 立即通知当前连接状态
    callback(this.isConnected());
    return () => this.connectionCallbacks.delete(callback);
  }

  /**
   * 检查连接状态
   */
  public isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  /**
   * 获取当前重连次数
   */
  public getReconnectAttempts(): number {
    return this.reconnectAttempts;
  }

  // ============================================================================
  // 私有方法
  // ============================================================================

  private handleOpen(): void {  // 🔧 修复: 移除未使用的event参数
    console.log('[WebSocket] 连接成功');
    this.reconnectAttempts = 0;
    this.notifyConnectionStatus(true);

    // 发送队列中的消息
    this.flushMessageQueue();
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);

      console.log('[WebSocket] 收到消息:', message);

      switch (message.type) {
        case 'progress':
          this.notifyProgress(message as AnalysisProgress);
          break;

        case 'result':
          this.notifyResult(message as AnalysisResult);
          break;

        case 'error':
          this.notifyError(message as AnalysisError);
          break;

        default:
          console.warn('[WebSocket] 未知消息类型:', message);
      }
    } catch (error) {
      console.error('[WebSocket] 解析消息失败:', error);
    }
  }

  private handleError(): void {  // 🔧 修复: 移除未使用的event参数
    console.error('[WebSocket] 连接错误');
  }

  private handleClose(event: CloseEvent): void {
    console.log(`[WebSocket] 连接关闭 (code: ${event.code}, reason: ${event.reason})`);
    this.ws = null;
    this.notifyConnectionStatus(false);

    // 如果不是主动关闭，尝试重连
    if (!this.isIntentionalClose) {
      this.scheduleReconnect();
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[WebSocket] 达到最大重连次数，停止重连');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts - 1); // 指数退避

    console.log(`[WebSocket] ${delay}ms 后尝试第 ${this.reconnectAttempts} 次重连...`);

    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, delay);
  }

  private clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  private send(message: WebSocketMessage): void {
    if (this.isConnected() && this.ws) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('[WebSocket] 连接未建立，消息已加入队列');
      this.messageQueue.push(message);
    }
  }

  private flushMessageQueue(): void {
    if (this.messageQueue.length === 0) {return;}

    console.log(`[WebSocket] 发送队列中的 ${this.messageQueue.length} 条消息`);

    while (this.messageQueue.length > 0 && this.isConnected()) {
      const message = this.messageQueue.shift();
      if (message) {
        this.send(message);
      }
    }
  }

  private notifyProgress(progress: AnalysisProgress): void {
    this.progressCallbacks.forEach(callback => {
      try {
        callback(progress);
      } catch (error) {
        console.error('[WebSocket] 进度回调执行失败:', error);
      }
    });
  }

  private notifyResult(result: AnalysisResult): void {
    this.resultCallbacks.forEach(callback => {
      try {
        callback(result);
      } catch (error) {
        console.error('[WebSocket] 结果回调执行失败:', error);
      }
    });
  }

  private notifyError(error: AnalysisError): void {
    this.errorCallbacks.forEach(callback => {
      try {
        callback(error);
      } catch (error) {
        console.error('[WebSocket] 错误回调执行失败:', error);
      }
    });
  }

  private notifyConnectionStatus(connected: boolean): void {
    this.connectionCallbacks.forEach(callback => {
      try {
        callback(connected);
      } catch (error) {
        console.error('[WebSocket] 连接状态回调执行失败:', error);
      }
    });
  }
}

// 全局单例实例
let wsServiceInstance: WebSocketService | null = null;

/**
 * 获取 WebSocket 服务单例
 */
export function getWebSocketService(): WebSocketService {
  if (!wsServiceInstance) {
    // 从环境变量或默认值获取 WebSocket URL
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8765/ws';
    wsServiceInstance = new WebSocketService(wsUrl, false);  // 不自动连接，由用户手动触发
  }
  return wsServiceInstance;
}

/**
 * 销毁 WebSocket 服务单例
 */
export function destroyWebSocketService(): void {
  if (wsServiceInstance) {
    wsServiceInstance.disconnect();
    wsServiceInstance = null;
  }
}
