/**
 * AIFlow Analysis Data Protocol - TypeScript Types
 * 标准化数据协议 v1.0.0 - 前端类型定义
 *
 * 基于: analysis-schema-v1.0.0.json
 * 对应后端: backend/aiflow/protocol/entities.py
 */

// ============================================================================
// 顶层结构
// ============================================================================

/**
 * 完整的分析结果 (顶层对象)
 */
export interface AnalysisResult {
  $schema: string;
  version: string;
  project_metadata: ProjectMetadata;
  code_structure: CodeStructure;
  execution_trace: ExecutionTrace;
  behavior_metadata?: BehaviorMetadata;
  concurrency_info?: ConcurrencyInfo;
  prompt_templates?: PromptTemplates;
}

// ============================================================================
// 项目元数据 (Project Metadata)
// ============================================================================

export interface ProjectMetadata {
  project_name: string;
  project_path: string;
  language: string;
  analyzed_at: string; // ISO 8601 timestamp
  framework?: string;
  architecture_pattern?: string;
  ai_model?: string;
  total_lines?: number;
}

// ============================================================================
// 代码结构 (Code Structure)
// ============================================================================

export interface CodeLocation {
  file_path: string;
  start_line: number;
  end_line: number;
}

export interface NodeMetadata {
  ai_confidence?: number;
  ai_explanation?: string;
  code_location?: CodeLocation;
}

export interface NodePosition {
  x: number;
  y: number;
}

export type NodeStereotype =
  | "system"
  | "module"
  | "class"
  | "function"
  | "service"
  | "component";

export interface CodeNode {
  id: string; // UUID v4
  label: string; // AI 生成的业务语义化名称
  stereotype: NodeStereotype;
  parent?: string; // 父节点 ID
  classes?: string[]; // Cytoscape.js 样式类
  metadata?: NodeMetadata;
  position?: NodePosition;
}

export type EdgeType = "dependency" | "inheritance" | "composition" | "call";

export interface CodeEdge {
  id: string;
  source: string; // 源节点 ID
  target: string; // 目标节点 ID
  type: EdgeType;
  label?: string;
}

export interface CodeStructure {
  nodes: CodeNode[];
  edges: CodeEdge[];
}

// ============================================================================
// 行为元数据 (Behavior Metadata)
// ============================================================================

export type LaunchButtonType = "macro" | "micro";

export interface LaunchButton {
  id: string; // UUID v4
  node_id: string; // 关联的节点 ID
  name: string; // AI 生成的按钮名称
  type: LaunchButtonType;
  description?: string;
  icon?: string;
}

export interface BehaviorMetadata {
  launch_buttons?: LaunchButton[];
}

// ============================================================================
// 执行追踪 (Execution Trace)
// ============================================================================

export type FlowchartStepType =
  | "start"
  | "end"
  | "process"
  | "decision"
  | "fork"
  | "join";

export interface FlowchartStep {
  id: string;
  label: string;
  type: FlowchartStepType;
  data?: any;
}

export type ConnectionType = "control_flow" | "data_flow";

export interface FlowchartConnection {
  id: string;
  source: string; // 源步骤 ID
  target: string; // 目标步骤 ID
  type: ConnectionType;
  label?: string;
}

export interface FlowchartTrace {
  steps: FlowchartStep[];
  connections: FlowchartConnection[];
}

export interface Lifeline {
  id: string;
  label: string; // 执行实体名称
  type: string;
}

export type MessageType = "sync" | "async" | "return";

export interface Message {
  id: string;
  source: string; // 源生命线 ID
  target: string; // 目标生命线 ID
  type: MessageType;
  timestamp: number;
  label: string;
}

export interface SequenceTrace {
  lifelines: Lifeline[];
  messages: Message[];
}

export interface ExecutionStep {
  id: string; // UUID v4
  order: number; // 局部顺序 (0开始)
  file_path: string;
  line_number: number; // 行号 (1开始)
  code: string; // 代码内容
  timestamp: string; // ISO 8601 timestamp
  execution_order: number; // 全局唯一序号
  scope_id: string; // 所属作用域 ID
  duration?: number; // 执行时长 (毫秒)
}

export interface VariableChange {
  timestamp: string; // ISO 8601 timestamp
  old_value: any;
  new_value: any;
  execution_order: number;
  changed_at: string; // 格式: "file.py:123"
}

export interface Variable {
  name: string;
  type: string; // 变量类型
  value: any;
  memory_address?: string; // 十六进制字符串 (如 "0x7f8b2c3d1e40")
  size_bytes?: number;
  is_mutable?: boolean;
  references?: string[]; // 引用的其他对象 ID
  history?: VariableChange[];
}

export type ScopeType = "global" | "local" | "closure" | "class" | "module";

export interface VariableScope {
  id: string; // UUID v4
  scope_type: ScopeType;
  variables: Variable[];
  timestamp: string; // ISO 8601 timestamp
  execution_order: number;
  parent_scope_id?: string; // 父作用域 ID
}

export interface StackFrame {
  id: string; // UUID v4
  function_name: string;
  module_name: string;
  file_path: string;
  line_number: number;
  depth: number; // 调用深度 (0 = 顶层)
  local_scope_id: string; // 关联的局部作用域 ID
  timestamp: string; // ISO 8601 timestamp
  execution_order: number;
  is_recursive?: boolean;
  recursion_depth?: number;
  arguments?: Record<string, any>; // 函数参数
  parent_frame_id?: string; // 父栈帧 ID
  return_value?: any;
}

export interface StepByStepTrace {
  steps: ExecutionStep[];
  variableScopes: VariableScope[];
  callStack: StackFrame[];
}

export type TraceFormat = "flowchart" | "sequence" | "step-by-step";

export interface Trace {
  format: TraceFormat;
  data: FlowchartTrace | SequenceTrace | StepByStepTrace;
}

export type TraceableUnitType = "single-trace" | "multi-trace";

export interface TraceableUnit {
  id: string; // UUID v4
  name: string; // AI 生成的功能名称
  type: TraceableUnitType;
  traces: Trace[];
  subUnitIds?: string[]; // 子单元 ID
}

export interface ExecutionTrace {
  traceable_units: TraceableUnit[];
}

// ============================================================================
// 并发信息 (Concurrency Info)
// ============================================================================

export type ConcurrencyType = "parallel" | "concurrent" | "async" | "sync_wait";

export interface ConcurrencyFlow {
  id: string; // UUID v4
  type: ConcurrencyType;
  involved_units: string[]; // 涉及的代码单元 ID
  start_point: string; // 起点节点 ID
  end_point: string; // 终点节点 ID
  dependencies?: string[]; // 依赖的其他并发流 ID
}

export type SyncType = "barrier" | "mutex" | "semaphore" | "join";

export interface SyncPoint {
  id: string; // UUID v4
  location: string; // 同步点位置 (格式: "file.py:123")
  waiting_flows: string[]; // 等待的并发流 ID
  type: SyncType;
}

export interface ConcurrencyInfo {
  flows?: ConcurrencyFlow[];
  sync_points?: SyncPoint[];
}

// ============================================================================
// Prompt 模板记录 (Prompt Templates)
// ============================================================================

export type AnalysisStage =
  | "project_understanding"
  | "structure_recognition"
  | "semantic_analysis"
  | "execution_inference"
  | "concurrency_detection";

export interface UsedPrompt {
  id: string; // Prompt 模板 ID
  stage: AnalysisStage;
  executed_at: string; // ISO 8601 timestamp
}

export interface PromptTemplates {
  used_prompts?: UsedPrompt[];
}

// ============================================================================
// 类型守卫 (Type Guards)
// ============================================================================

export function isFlowchartTrace(data: any): data is FlowchartTrace {
  return (
    data &&
    Array.isArray(data.steps) &&
    Array.isArray(data.connections)
  );
}

export function isSequenceTrace(data: any): data is SequenceTrace {
  return (
    data &&
    Array.isArray(data.lifelines) &&
    Array.isArray(data.messages)
  );
}

export function isStepByStepTrace(data: any): data is StepByStepTrace {
  return (
    data &&
    Array.isArray(data.steps) &&
    Array.isArray(data.variableScopes) &&
    Array.isArray(data.callStack)
  );
}

// ============================================================================
// 工具类型 (Utility Types)
// ============================================================================

/**
 * 提取特定格式的 Trace 数据
 */
export type TraceData<F extends TraceFormat> =
  F extends "flowchart" ? FlowchartTrace :
  F extends "sequence" ? SequenceTrace :
  F extends "step-by-step" ? StepByStepTrace :
  never;

/**
 * 创建 Trace 的辅助类型
 */
export interface TypedTrace<F extends TraceFormat> {
  format: F;
  data: TraceData<F>;
}

/**
 * 可选字段包装器 (用于部分更新)
 */
export type PartialDeep<T> = {
  [P in keyof T]?: T[P] extends object ? PartialDeep<T[P]> : T[P];
};

// ============================================================================
// 验证辅助函数
// ============================================================================

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
  const iso8601Regex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z?$/;
  return iso8601Regex.test(timestamp);
}

/**
 * 验证文件路径:行号格式
 */
export function isValidLocation(location: string): boolean {
  const locationRegex = /^.+:\d+$/;
  return locationRegex.test(location);
}

// ============================================================================
// 常量定义
// ============================================================================

export const SCHEMA_VERSION = "1.0.0";
export const SCHEMA_URL = "https://aiflow.dev/schemas/analysis-v1.0.0.json";

export const NODE_STEREOTYPES: readonly NodeStereotype[] = [
  "system",
  "module",
  "class",
  "function",
  "service",
  "component",
] as const;

export const EDGE_TYPES: readonly EdgeType[] = [
  "dependency",
  "inheritance",
  "composition",
  "call",
] as const;

export const TRACE_FORMATS: readonly TraceFormat[] = [
  "flowchart",
  "sequence",
  "step-by-step",
] as const;

export const ANALYSIS_STAGES: readonly AnalysisStage[] = [
  "project_understanding",
  "structure_recognition",
  "semantic_analysis",
  "execution_inference",
  "concurrency_detection",
] as const;
