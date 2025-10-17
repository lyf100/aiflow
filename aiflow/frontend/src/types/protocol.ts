// AIFlow Protocol Types - JSON Schema v2.0.0
// 支持五阶段AI分析结果的完整协议定义

/**
 * 顶层分析结果结构
 * 包含五阶段分析的所有输出
 */
export interface AnalysisResult {
  metadata?: ProjectMetadata;
  stage1_project_cognition?: Stage1Output;
  stage2_structure_recognition?: Stage2Output;
  stage3_semantic_analysis?: Stage3Output;
  stage4_execution_inference?: Stage4Output;
  stage5_concurrency_detection?: Stage5Output;

  // 🆕 v1协议向后兼容字段（MCP Server可能直接输出这些字段）
  project_name?: string;
  protocol_version?: string;
  timestamp?: string;
  execution_traces?: ExecutionTrace[];  // 复数形式兼容

  // 向后兼容的简化访问
  code_structure?: CodeStructure;
  behavior_metadata?: BehaviorMetadata;
  execution_trace?: ExecutionTrace;
}

// ============================================================================
// 元数据定义
// ============================================================================

export interface ProjectMetadata {
  project_name: string;
  project_type?: string;
  analysis_timestamp: string;
  timestamp?: string;          // 🆕 向后兼容别名
  protocol_version: string;  // "2.0.0"
  aiflow_version?: string;   // "2.0.0-mcp"
  ai_model?: string;          // "claude-4.5"
  analysis_stats?: {
    total_files?: number;
    analyzed_files?: number;
    total_nodes?: number;
    total_edges?: number;
    total_buttons?: number;
    total_traceable_units?: number;
    languages?: Record<string, number>;
  };
}

// ============================================================================
// Stage 1: 项目认知输出
// ============================================================================

export interface Stage1Output {
  stage: 'project_cognition';
  project_name: string;
  project_type: string;
  tech_stack: TechStack;
  architecture: Architecture;
  complexity_assessment: ComplexityAssessment;
  entry_points: EntryPoint[];
  core_modules: CoreModule[];
  detected_patterns?: DetectedPatterns;
  recommendations?: Recommendations;
}

export interface TechStack {
  primary_language: string;
  languages: string[];
  frameworks: Framework[];
  build_tools?: string[];
  package_managers?: string[];
}

export interface Framework {
  name: string;
  version?: string;
  category: 'web' | 'mobile' | 'backend' | 'data' | 'testing' | 'other';
}

export interface Architecture {
  pattern: string;  // 'MVC' | 'MVVM' | 'Microservices' | etc.
  pattern_confidence: number;
  description: string;
  layers?: ArchitectureLayer[];
}

export interface ArchitectureLayer {
  name: string;
  directories: string[];
}

export interface ComplexityAssessment {
  score: number;  // 0.0 - 1.0
  factors: {
    codebase_size: number;
    dependency_depth: number;
    business_logic: number;
    concurrency: number;
  };
  reasoning: string;
}

export interface EntryPoint {
  file: string;
  function?: string;
  description: string;
}

export interface CoreModule {
  name: string;
  directories: string[];
  importance: 'high' | 'medium' | 'low';
  business_value: string;
}

export interface DetectedPatterns {
  design_patterns?: string[];
  concurrency_patterns?: string[];
  data_patterns?: string[];
}

export interface Recommendations {
  analysis_strategy?: string;
  focus_areas?: string[];
  estimated_time?: string;
}

// ============================================================================
// Stage 2: 结构识别输出
// ============================================================================

export interface Stage2Output {
  stage: 'structure_recognition';
  extends_stage: 'project_cognition';
  code_structure: CodeStructure;
  grouping_strategy?: GroupingStrategy;
  analysis_metrics?: AnalysisMetrics;
}

export interface CodeStructure {
  nodes: CodeNode[];
  edges: CodeEdge[];
}

export interface CodeNode {
  id: string;
  name: string;
  type: 'class' | 'function' | 'interface' | 'module' | 'system';
  stereotype: 'system' | 'module' | 'component' | 'function';
  parent_id?: string;
  file_path?: string;
  language?: string;
  line_number?: number;
  description?: string;
  parent_class_id?: string;  // 对于function节点，指向所属class
  directories?: string[];    // 🆕 包含的目录列表（用于module/component节点）

  // 🆕 函数特定字段
  parameters?: Array<{name: string; type?: string}>;  // 函数参数
  return_type?: string;                               // 返回值类型

  // 🆕 边的引用字段（用于TreeView等组件）
  source?: string;
  target?: string;

  metadata?: {
    pattern?: string;
    responsibilities?: string[];
    visibility?: string;
    is_async?: boolean;
    complexity?: number;
    is_critical_path?: boolean;  // 标记是否在关键路径上

    // 🆕 系统级元数据（用于system节点）
    total_packages?: number;
    core_packages?: number;
    architecture_style?: string;

    // 🆕 模块级元数据（用于module节点）
    business_domain?: string;

    // 🆕 组件级元数据（用于component节点）
    extends?: string;  // 继承的父类

    // 🆕 函数级元数据（用于function节点）
    has_side_effects?: boolean;
  };
}

export interface CodeEdge {
  id: string;
  source: string;
  target: string;
  type: 'contains' | 'calls' | 'inherits' | 'implements' | 'depends_on';
  description?: string;
  metadata?: {
    call_count_estimate?: string;
    is_critical_path?: boolean;
    dependency_type?: string;
  };
}

export interface GroupingStrategy {
  by_business?: BusinessGroup[];
  by_layer?: LayerGroup[];
  by_pattern?: PatternGroup;
}

export interface BusinessGroup {
  group_name: string;
  node_ids: string[];
  description: string;
}

export interface LayerGroup {
  layer_name: string;
  node_ids: string[];
  description: string;
}

export interface PatternGroup {
  pattern: string;
  groups: Record<string, string[]>;  // 如 { "Model": [...], "View": [...] }
}

export interface AnalysisMetrics {
  total_nodes: number;
  nodes_by_type: Record<string, number>;
  total_edges: number;
  edges_by_type: Record<string, number>;
  max_depth?: number;
  cyclomatic_complexity_avg?: number;
}

// ============================================================================
// Stage 3: 语义分析输出
// ============================================================================

export interface Stage3Output {
  stage: 'semantic_analysis';
  extends_stage: 'structure_recognition';
  launch_buttons: LaunchButton[];
  button_hierarchy?: ButtonHierarchy;
  business_scenarios?: BusinessScenario[];
}

export interface LaunchButton {
  id: string;
  name: string;                    // AI生成的业务语义化名称
  type: 'macro' | 'micro';        // macro=大按钮(系统级), micro=小按钮(组件级)
  level: 'system' | 'module' | 'component' | 'function';
  description?: string;
  icon?: string;

  // 🆕 嵌套关系字段
  parent_button_id?: string | null;
  child_button_ids?: string[];

  // 关联数据
  related_node_ids?: string[];     // 关联的代码节点
  traceable_unit_id?: string;      // 关联的执行单元ID

  metadata?: {
    business_value?: string;
    user_facing?: boolean;
    estimated_duration_ms?: number;
    requires_input?: boolean;
    input_description?: string;
    has_side_effects?: boolean;
    side_effects?: string[];
    database_access?: boolean;
    ai_confidence?: number;
    ai_reasoning?: string;
  };
}

export interface ButtonHierarchy {
  total_buttons: number;
  macro_buttons: number;
  micro_buttons: number;
  max_nesting_depth: number;
  independent_micro_buttons?: number;
  description?: string;
}

export interface BusinessScenario {
  scenario_name: string;
  macro_button_ids: string[];
  description: string;
}

export interface BehaviorMetadata {
  launch_buttons: LaunchButton[];
}

// ============================================================================
// Stage 4: 执行推理输出
// ============================================================================

export interface Stage4Output {
  stage: 'execution_inference';
  extends_stage: 'semantic_analysis';
  traceable_units: TraceableUnit[];
}

export interface TraceableUnit {
  id: string;
  name: string;
  description?: string;
  entry_point?: {
    node_id: string;
    file: string;
    function: string;
    line_number?: number;
  };
  estimated_duration_ms?: number;
  traces: Trace[];
  concurrency_info?: ConcurrencyInfo;
}

export interface Trace {
  format: 'flowchart' | 'sequence' | 'step_by_step';
  data: FlowchartData | SequenceData | StepByStepData;
}

// 🆕 流程图数据 - 支持fork/join并发节点
export interface FlowchartData {
  steps: FlowchartStep[];
  connections: FlowchartConnection[];
}

export interface FlowchartStep {
  id: string;
  label: string;
  type: 'start' | 'end' | 'process' | 'decision' | 'fork' | 'join';  // 🆕 支持fork和join
  lineNumber?: number;
  code_snippet?: string;
  estimated_duration_ms?: number;

  // 🆕 并发相关字段
  branch_id?: number;              // 对于并发分支，标识分支编号
  concurrent_branches?: number;    // 对于fork节点，说明分叉数量
  waits_for?: string[];           // 对于join节点，等待哪些步骤
  condition?: string;             // 对于decision节点，判断条件
  description?: string;           // 节点描述

  // 🆕 Per-step 变量状态追踪 (Phase 4.1)
  variables?: VariableScope;       // 该步骤执行后的变量快照
  callStack?: string[];            // 该步骤的调用堆栈
}

export interface FlowchartConnection {
  id: string;
  source: string;
  target: string;
  type: 'control_flow' | 'data_flow';
  label?: string;
  condition_result?: boolean;     // 对于decision节点的分支
  is_concurrent?: boolean;        // 🆕 标记并发连接
}

// 🆕 时序图数据 - 支持异步消息
export interface SequenceData {
  participants: Participant[];
  messages: Message[];
}

export interface Participant {
  id: string;
  name: string;
  type: 'actor' | 'component' | 'service';
}

export interface Message {
  id: string;
  from: string;
  to: string;
  label: string;
  type: 'call' | 'return' | 'async' | 'create' | 'destroy';  // 🆕 支持async
  order: number;
  concurrent_group?: number;      // 🆕 标记并发组
}

// 🆕 单步执行数据 - 支持变量状态和调用堆栈
export interface StepByStepData {
  file_path: string;
  language: string;
  function?: string;
  code?: string;
  steps: ExecutionStep[];
}

export interface ExecutionStep {
  id: string;
  lineNumber: number;
  description: string;
  code?: string;

  // 🆕 变量状态（按作用域组织）
  variables?: VariableScope;

  // 🆕 调用堆栈
  callStack?: string[];
}

// 🆕 变量作用域定义
export interface VariableScope {
  global?: Record<string, any>;
  local?: Record<string, any>;
  parameter?: Record<string, any>;
  closure?: Record<string, any>;
  instance?: Record<string, any>;
}

// 🆕 并发信息
export interface ConcurrencyInfo {
  has_concurrency: boolean;
  concurrent_branches?: number;
  synchronization_points?: string[];
  async_operations?: AsyncOperation[];
  total_duration_with_concurrency_ms?: number;
  total_duration_without_concurrency_ms?: number;
}

export interface AsyncOperation {
  operation: string;
  estimated_duration_ms: number;
}

export interface ExecutionTrace {
  trace_id: string;                 // 🆕 轨迹唯一标识符
  traceable_units: TraceableUnit[];

  // 🆕 Extended properties for ExecutionAnimation support
  trace_name?: string;              // Display name for the trace
  flowchart?: FlowchartData;       // Direct flowchart data access
  variables_used?: VariableScope;  // Variables used in this trace
  call_stack?: string[];           // Function call stack
  timeline_estimation?: TimelineEstimation;  // 🆕 时间轴预估信息（对象形式）
}

// 🆕 时间轴预估信息
export interface TimelineEstimation {
  total_duration_ms?: number;      // 总执行时间
  events?: TimelineEvent[];        // 时间轴事件列表
}

export interface TimelineEvent {
  event_id: string;
  timestamp_ms: number;
  operation_type?: string;
  operation_detail?: string;
  duration_tcu?: number;
  source_location?: {
    file: string;
    line?: number;
    code_snippet?: string;
  };
  input_data?: any;
  output_data?: any;
}

// ============================================================================
// Stage 5: 并发检测输出
// ============================================================================

export interface Stage5Output {
  stage: 'concurrency_detection';
  extends_stage: 'execution_inference';
  concurrency_mechanisms: ConcurrencyMechanism[];
  synchronization_points: SynchronizationPoint[];
  shared_resources: SharedResource[];
  detected_issues: ConcurrencyIssue[];
  concurrency_metrics?: ConcurrencyMetrics;
  optimization_suggestions?: OptimizationSuggestion[];
}

export interface ConcurrencyMechanism {
  type: string;  // 'CompletableFuture', 'async/await', 'Thread', 'goroutine', etc.
  language: string;
  usage_count: number;
  locations: CodeLocation[];
  description: string;
}

export interface CodeLocation {
  file: string;
  line: number;
  pattern: string;
}

export interface SynchronizationPoint {
  id: string;
  type: 'join' | 'lock' | 'semaphore' | 'barrier' | 'condition';
  location: CodeLocation;
  description: string;
  waits_for?: string[];
  timeout_ms?: number | null;
  can_deadlock: boolean;
  deadlock_risk?: number;
  deadlock_scenario?: string;
  protects?: string;
}

export interface SharedResource {
  id: string;
  name: string;
  type: string;  // 'in_memory_cache', 'counter', 'file', 'database_connection', etc.
  location: CodeLocation & { declaration?: string };
  accessed_by: string[];
  protection_mechanism: string;  // 'synchronized', 'lock', 'atomic', 'none'
  is_thread_safe: boolean;
  data_race_risk?: number;
}

export interface ConcurrencyIssue {
  id: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  type: 'deadlock' | 'data_race' | 'resource_leak' | 'starvation' | 'performance' | 'potential_deadlock';
  title: string;
  description: string;
  location?: CodeLocation & { code?: string };
  locations?: Array<CodeLocation & { lock_order?: string[] }>;
  impact: string;
  recommendation: {
    solution: string;
    code_example?: string;
  };
  confidence: number;
}

export interface ConcurrencyMetrics {
  total_concurrent_operations: number;
  async_calls: number;
  thread_pools: number;
  locks: number;
  shared_resources: number;
  potential_issues: number;
  thread_safe_percentage: number;
}

export interface OptimizationSuggestion {
  category: 'performance' | 'reliability' | 'maintainability';
  suggestion: string;
  affected_files: string[];
  estimated_improvement: string;
}
