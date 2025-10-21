/**
 * useWebSocket Hook
 *
 * React Hook for AIFlow WebSocket connection management
 * 提供连接状态、进度监听、分析触发等功能
 */

import { useEffect, useState, useCallback, useRef } from 'react';
import {
  getWebSocketService,
  AnalysisProgress,
  AnalysisResult,
  AnalysisError
} from '../services/websocket';

export interface UseWebSocketOptions {
  autoConnect?: boolean;  // 是否自动连接
  onProgress?: (progress: AnalysisProgress) => void;
  onResult?: (result: AnalysisResult) => void;
  onError?: (error: AnalysisError) => void;
}

export interface UseWebSocketReturn {
  isConnected: boolean;
  reconnectAttempts: number;
  connect: () => void;
  disconnect: () => void;
  startAnalysis: (buttonId: string, projectPath: string, projectName?: string) => void;
  latestProgress: AnalysisProgress | null;
  latestResult: AnalysisResult | null;
  latestError: AnalysisError | null;
}

/**
 * WebSocket Hook - 管理连接和消息订阅
 */
export function useWebSocket(options: UseWebSocketOptions = {}): UseWebSocketReturn {
  const {
    autoConnect = false,
    onProgress,
    onResult,
    onError
  } = options;

  const wsService = getWebSocketService();

  // 连接状态
  const [isConnected, setIsConnected] = useState(wsService.isConnected());
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

  // 最新消息状态
  const [latestProgress, setLatestProgress] = useState<AnalysisProgress | null>(null);
  const [latestResult, setLatestResult] = useState<AnalysisResult | null>(null);
  const [latestError, setLatestError] = useState<AnalysisError | null>(null);

  // 防止回调函数变化导致重复订阅
  const onProgressRef = useRef(onProgress);
  const onResultRef = useRef(onResult);
  const onErrorRef = useRef(onError);

  useEffect(() => {
    onProgressRef.current = onProgress;
  }, [onProgress]);

  useEffect(() => {
    onResultRef.current = onResult;
  }, [onResult]);

  useEffect(() => {
    onErrorRef.current = onError;
  }, [onError]);

  // 连接管理
  const connect = useCallback(() => {
    wsService.connect();
  }, [wsService]);

  const disconnect = useCallback(() => {
    wsService.disconnect();
  }, [wsService]);

  // 触发分析
  const startAnalysis = useCallback((buttonId: string, projectPath: string, projectName?: string) => {
    wsService.startAnalysis(buttonId, projectPath, projectName);
  }, [wsService]);

  // 订阅 WebSocket 事件
  useEffect(() => {
    // 连接状态监听
    const unsubscribeConnection = wsService.onConnectionStatus((connected) => {
      setIsConnected(connected);
      setReconnectAttempts(wsService.getReconnectAttempts());
    });

    // 进度监听
    const unsubscribeProgress = wsService.onProgress((progress) => {
      setLatestProgress(progress);
      onProgressRef.current?.(progress);
    });

    // 结果监听
    const unsubscribeResult = wsService.onResult((result) => {
      setLatestResult(result);
      onResultRef.current?.(result);
    });

    // 错误监听
    const unsubscribeError = wsService.onError((error) => {
      setLatestError(error);
      onErrorRef.current?.(error);
    });

    // 自动连接
    if (autoConnect) {
      connect();
    }

    // 组件卸载时清理
    return () => {
      unsubscribeConnection();
      unsubscribeProgress();
      unsubscribeResult();
      unsubscribeError();
    };
  }, [wsService, autoConnect, connect]);

  return {
    isConnected,
    reconnectAttempts,
    connect,
    disconnect,
    startAnalysis,
    latestProgress,
    latestResult,
    latestError
  };
}

/**
 * useAnalysisProgress Hook - 监听特定按钮的分析进度
 */
export function useAnalysisProgress(buttonId: string | null) {
  const [progress, setProgress] = useState<AnalysisProgress | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleProgress = useCallback((incomingProgress: AnalysisProgress) => {
    if (buttonId && incomingProgress.button_id === buttonId) {
      setProgress(incomingProgress);
      setIsAnalyzing(incomingProgress.status === 'running');
    }
  }, [buttonId]);

  const handleResult = useCallback((result: AnalysisResult) => {
    if (buttonId && result.button_id === buttonId) {
      setIsAnalyzing(false);
    }
  }, [buttonId]);

  const handleError = useCallback((error: AnalysisError) => {
    if (buttonId && error.button_id === buttonId) {
      setIsAnalyzing(false);
    }
  }, [buttonId]);

  useWebSocket({
    onProgress: handleProgress,
    onResult: handleResult,
    onError: handleError
  });

  return {
    progress,
    isAnalyzing,
    stage: progress?.stage || 0,
    stageName: progress?.stage_name || '',
    progressPercent: progress?.progress_percent || 0,
    message: progress?.message || '',
    estimatedTimeRemaining: progress?.estimated_time_remaining_ms || null
  };
}
