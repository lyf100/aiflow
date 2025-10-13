/**
 * Data Loader - JSON 数据加载工具
 *
 * 负责从文件或 URL 加载 AIFlow 分析结果数据。
 */

import type { AnalysisResult } from '../types/protocol';
import { validateAnalysisResult } from './validators';

export interface LoadOptions {
  validate?: boolean;
  onProgress?: (progress: number) => void;
}

export interface LoadResult {
  success: boolean;
  data?: AnalysisResult;
  error?: string;
  validationErrors?: string[];
}

/**
 * 从文件对象加载分析数据
 */
export async function loadFromFile(
  file: File,
  options: LoadOptions = {}
): Promise<LoadResult> {
  const { validate = true, onProgress } = options;

  try {
    // 检查文件类型
    if (!file.name.endsWith('.json') && !file.name.endsWith('.json.gz')) {
      return {
        success: false,
        error: '不支持的文件格式。请上传 .json 或 .json.gz 文件。',
      };
    }

    // 检查文件大小（限制 100MB）
    const maxSize = 100 * 1024 * 1024;
    if (file.size > maxSize) {
      return {
        success: false,
        error: `文件过大（${(file.size / 1024 / 1024).toFixed(2)}MB）。最大支持 100MB。`,
      };
    }

    onProgress?.(10);

    // 读取文件内容
    const content = await readFileContent(file, onProgress);

    onProgress?.(60);

    // 解析 JSON
    let data: AnalysisResult;
    try {
      data = JSON.parse(content);
    } catch (error) {
      return {
        success: false,
        error: `JSON 解析失败: ${error instanceof Error ? error.message : '未知错误'}`,
      };
    }

    onProgress?.(80);

    // 验证数据
    if (validate) {
      const validationErrors = validateAnalysisResult(data);
      if (validationErrors.length > 0) {
        return {
          success: false,
          error: '数据验证失败',
          validationErrors,
        };
      }
    }

    onProgress?.(100);

    return {
      success: true,
      data,
    };
  } catch (error) {
    return {
      success: false,
      error: `加载失败: ${error instanceof Error ? error.message : '未知错误'}`,
    };
  }
}

/**
 * 从 URL 加载分析数据
 */
export async function loadFromURL(
  url: string,
  options: LoadOptions = {}
): Promise<LoadResult> {
  const { validate = true, onProgress } = options;

  try {
    onProgress?.(10);

    const response = await fetch(url);

    if (!response.ok) {
      return {
        success: false,
        error: `HTTP 错误: ${response.status} ${response.statusText}`,
      };
    }

    onProgress?.(50);

    const data: AnalysisResult = await response.json();

    onProgress?.(80);

    // 验证数据
    if (validate) {
      const validationErrors = validateAnalysisResult(data);
      if (validationErrors.length > 0) {
        return {
          success: false,
          error: '数据验证失败',
          validationErrors,
        };
      }
    }

    onProgress?.(100);

    return {
      success: true,
      data,
    };
  } catch (error) {
    return {
      success: false,
      error: `加载失败: ${error instanceof Error ? error.message : '未知错误'}`,
    };
  }
}

/**
 * 从 localStorage 加载最近的分析数据
 */
export function loadFromLocalStorage(): AnalysisResult | null {
  try {
    const stored = localStorage.getItem('aiflow-last-analysis');
    if (!stored) return null;

    const data = JSON.parse(stored);
    return data;
  } catch (error) {
    console.error('从 localStorage 加载失败:', error);
    return null;
  }
}

/**
 * 保存分析数据到 localStorage
 */
export function saveToLocalStorage(data: AnalysisResult): boolean {
  try {
    const jsonString = JSON.stringify(data);
    localStorage.setItem('aiflow-last-analysis', jsonString);
    return true;
  } catch (error) {
    console.error('保存到 localStorage 失败:', error);
    return false;
  }
}

/**
 * 读取文件内容（支持 .json 和 .json.gz）
 */
async function readFileContent(
  file: File,
  onProgress?: (progress: number) => void
): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();

    reader.onprogress = (event) => {
      if (event.lengthComputable) {
        const progress = 10 + (event.loaded / event.total) * 50; // 10-60%
        onProgress?.(progress);
      }
    };

    reader.onload = async (event) => {
      try {
        const arrayBuffer = event.target?.result as ArrayBuffer;

        // 如果是 .gz 文件，需要解压
        if (file.name.endsWith('.gz')) {
          const decompressed = await decompressGzip(arrayBuffer);
          resolve(decompressed);
        } else {
          const text = new TextDecoder().decode(arrayBuffer);
          resolve(text);
        }
      } catch (error) {
        reject(error);
      }
    };

    reader.onerror = () => {
      reject(new Error('文件读取失败'));
    };

    reader.readAsArrayBuffer(file);
  });
}

/**
 * 解压 gzip 数据
 */
async function decompressGzip(data: ArrayBuffer): Promise<string> {
  // 使用浏览器原生的 DecompressionStream API
  if ('DecompressionStream' in window) {
    const stream = new Blob([data])
      .stream()
      .pipeThrough(new DecompressionStream('gzip'));

    const decompressed = await new Response(stream).arrayBuffer();
    return new TextDecoder().decode(decompressed);
  }

  // 如果浏览器不支持，抛出错误
  throw new Error('浏览器不支持 gzip 解压。请上传未压缩的 .json 文件。');
}

/**
 * 导出分析数据为 JSON 文件
 */
export function exportToFile(
  data: AnalysisResult,
  filename: string = 'analysis_result.json'
): void {
  const jsonString = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonString], { type: 'application/json' });
  const url = URL.createObjectURL(blob);

  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();

  URL.revokeObjectURL(url);
}

/**
 * 获取文件大小的友好显示
 */
export function getFileSizeDisplay(bytes: number): string {
  if (bytes < 1024) {
    return `${bytes} B`;
  } else if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(2)} KB`;
  } else {
    return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
  }
}

/**
 * 验证 URL 格式
 */
export function isValidURL(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}
