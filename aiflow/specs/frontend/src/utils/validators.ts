/**
 * Validators - 前端数据验证工具
 *
 * 验证从文件加载的分析数据是否符合标准数据协议。
 */

import type { AnalysisResult } from '../types/protocol';

/**
 * 验证分析结果的完整性
 */
export function validateAnalysisResult(data: any): string[] {
  const errors: string[] = [];

  // 基本结构验证
  if (!data || typeof data !== 'object') {
    errors.push('数据格式错误：必须是对象类型');
    return errors;
  }

  // Schema 版本验证
  if (!data.$schema || typeof data.$schema !== 'string') {
    errors.push('缺少 $schema 字段或格式错误');
  }

  if (!data.version || typeof data.version !== 'string') {
    errors.push('缺少 version 字段或格式错误');
  }

  // project_metadata 验证
  if (!data.project_metadata) {
    errors.push('缺少 project_metadata 字段');
  } else {
    errors.push(...validateProjectMetadata(data.project_metadata));
  }

  // code_structure 验证
  if (!data.code_structure) {
    errors.push('缺少 code_structure 字段');
  } else {
    errors.push(...validateCodeStructure(data.code_structure));
  }

  // behavior_metadata 验证（可选）
  if (data.behavior_metadata) {
    errors.push(...validateBehaviorMetadata(data.behavior_metadata));
  }

  // execution_trace 验证（可选）
  if (data.execution_trace) {
    errors.push(...validateExecutionTrace(data.execution_trace));
  }

  // concurrency_info 验证（可选）
  if (data.concurrency_info) {
    errors.push(...validateConcurrencyInfo(data.concurrency_info));
  }

  return errors;
}

/**
 * 验证项目元数据
 */
function validateProjectMetadata(metadata: any): string[] {
  const errors: string[] = [];

  const requiredFields = ['name', 'language'];
  for (const field of requiredFields) {
    if (!metadata[field]) {
      errors.push(`project_metadata.${field} 字段缺失`);
    }
  }

  return errors;
}

/**
 * 验证代码结构
 */
function validateCodeStructure(structure: any): string[] {
  const errors: string[] = [];

  if (!Array.isArray(structure.nodes)) {
    errors.push('code_structure.nodes 必须是数组');
    return errors;
  }

  if (!Array.isArray(structure.edges)) {
    errors.push('code_structure.edges 必须是数组');
  }

  // 验证节点
  const nodeIds = new Set<string>();
  structure.nodes.forEach((node: any, index: number) => {
    if (!node.id) {
      errors.push(`节点 [${index}] 缺少 id 字段`);
    } else {
      if (!isValidUUID(node.id)) {
        errors.push(`节点 [${index}] 的 id "${node.id}" 不是有效的 UUID v4`);
      }
      nodeIds.add(node.id);
    }

    if (!node.label) {
      errors.push(`节点 [${index}] 缺少 label 字段`);
    }

    if (!node.stereotype) {
      errors.push(`节点 [${index}] 缺少 stereotype 字段`);
    } else {
      const validStereotypes = ['system', 'module', 'class', 'function', 'service', 'component'];
      if (!validStereotypes.includes(node.stereotype)) {
        errors.push(`节点 [${index}] 的 stereotype "${node.stereotype}" 无效`);
      }
    }
  });

  // 验证边的引用完整性
  if (Array.isArray(structure.edges)) {
    structure.edges.forEach((edge: any, index: number) => {
      if (!edge.source) {
        errors.push(`边 [${index}] 缺少 source 字段`);
      } else if (!nodeIds.has(edge.source)) {
        errors.push(`边 [${index}] 的 source "${edge.source}" 引用不存在的节点`);
      }

      if (!edge.target) {
        errors.push(`边 [${index}] 缺少 target 字段`);
      } else if (!nodeIds.has(edge.target)) {
        errors.push(`边 [${index}] 的 target "${edge.target}" 引用不存在的节点`);
      }
    });
  }

  return errors;
}

/**
 * 验证行为元数据
 */
function validateBehaviorMetadata(metadata: any): string[] {
  const errors: string[] = [];

  if (metadata.launch_buttons && !Array.isArray(metadata.launch_buttons)) {
    errors.push('behavior_metadata.launch_buttons 必须是数组');
  }

  if (Array.isArray(metadata.launch_buttons)) {
    const buttonIds = new Set<string>();

    metadata.launch_buttons.forEach((button: any, index: number) => {
      if (!button.id) {
        errors.push(`启动按钮 [${index}] 缺少 id 字段`);
      } else {
        if (!isValidUUID(button.id)) {
          errors.push(`启动按钮 [${index}] 的 id 不是有效的 UUID v4`);
        }
        buttonIds.add(button.id);
      }

      if (!button.name) {
        errors.push(`启动按钮 [${index}] 缺少 name 字段`);
      }

      if (!button.type) {
        errors.push(`启动按钮 [${index}] 缺少 type 字段`);
      } else if (!['macro', 'micro'].includes(button.type)) {
        errors.push(`启动按钮 [${index}] 的 type "${button.type}" 无效`);
      }
    });

    // 验证嵌套关系
    metadata.launch_buttons.forEach((button: any, index: number) => {
      if (button.parent_button_id && !buttonIds.has(button.parent_button_id)) {
        errors.push(`启动按钮 [${index}] 的 parent_button_id 引用不存在的按钮`);
      }

      if (Array.isArray(button.child_button_ids)) {
        button.child_button_ids.forEach((childId: string) => {
          if (!buttonIds.has(childId)) {
            errors.push(`启动按钮 [${index}] 的 child_button_ids 引用不存在的按钮 "${childId}"`);
          }
        });
      }
    });
  }

  return errors;
}

/**
 * 验证执行轨迹
 */
function validateExecutionTrace(trace: any): string[] {
  const errors: string[] = [];

  if (!Array.isArray(trace.traceable_units)) {
    errors.push('execution_trace.traceable_units 必须是数组');
    return errors;
  }

  trace.traceable_units.forEach((unit: any, index: number) => {
    if (!unit.id) {
      errors.push(`可追踪单元 [${index}] 缺少 id 字段`);
    } else if (!isValidUUID(unit.id)) {
      errors.push(`可追踪单元 [${index}] 的 id 不是有效的 UUID v4`);
    }

    if (!unit.name) {
      errors.push(`可追踪单元 [${index}] 缺少 name 字段`);
    }

    if (!Array.isArray(unit.traces)) {
      errors.push(`可追踪单元 [${index}] 的 traces 必须是数组`);
    }
  });

  return errors;
}

/**
 * 验证并发信息
 */
function validateConcurrencyInfo(info: any): string[] {
  const errors: string[] = [];

  if (info.mechanisms && !Array.isArray(info.mechanisms)) {
    errors.push('concurrency_info.mechanisms 必须是数组');
  }

  if (info.flows && !Array.isArray(info.flows)) {
    errors.push('concurrency_info.flows 必须是数组');
  }

  if (info.sync_points && !Array.isArray(info.sync_points)) {
    errors.push('concurrency_info.sync_points 必须是数组');
  }

  return errors;
}

/**
 * 验证 UUID v4 格式
 */
export function isValidUUID(id: string): boolean {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  return uuidRegex.test(id);
}

/**
 * 验证 ISO 8601 时间戳格式
 */
export function isValidISO8601(timestamp: string): boolean {
  try {
    const date = new Date(timestamp);
    return date.toISOString() === timestamp;
  } catch {
    return false;
  }
}

/**
 * 获取数据统计信息
 */
export function getDataStatistics(data: AnalysisResult): {
  nodeCount: number;
  edgeCount: number;
  buttonCount: number;
  traceCount: number;
} {
  return {
    nodeCount: data.code_structure?.nodes?.length || 0,
    edgeCount: data.code_structure?.edges?.length || 0,
    buttonCount: data.behavior_metadata?.launch_buttons?.length || 0,
    traceCount: data.execution_trace?.traceable_units?.length || 0,
  };
}
