// AIFlow Protocol Types - JSON Schema v1.0.0

export interface AnalysisResult {
  metadata: ProjectMetadata;
  code_structure: CodeStructure;
  behavior_metadata: BehaviorMetadata;
  execution_trace: ExecutionTrace;
}

export interface ProjectMetadata {
  project_id: string;
  project_name?: string;
  timestamp: string;
  ai_model: string;
  protocol_version: string;
  analysis_stats?: {
    total_files: number;
    analyzed_files: number;
    total_nodes: number;
    total_edges: number;
    languages: Record<string, number>;
  };
}

export interface CodeStructure {
  nodes: CodeNode[];
  edges: CodeEdge[];
}

export interface CodeNode {
  id: string;
  name: string;
  type: 'class' | 'function';
  stereotype: 'system' | 'module' | 'component' | 'function';
  file_path?: string;
  language?: string;
  description?: string;
  parent_class_id?: string;
}

export interface CodeEdge {
  id: string;
  source: string;
  target: string;
  type: 'contains' | 'calls' | 'inherits' | 'implements' | 'depends_on';
}

export interface BehaviorMetadata {
  launch_buttons: LaunchButton[];
}

export interface LaunchButton {
  id: string;
  name: string;
  type: 'macro' | 'micro';
  level: 'system' | 'module' | 'component' | 'function';
  description?: string;
  icon?: string;
  parent_button_id?: string | null;
  child_button_ids?: string[];
  traceable_unit_id?: string;
  metadata?: {
    ai_confidence?: number;
    estimated_duration?: number;
    requires_input?: boolean;
    has_side_effects?: boolean;
  };
}

export interface ExecutionTrace {
  traceable_units: TraceableUnit[];
}

export interface TraceableUnit {
  id: string;
  name: string;
  description?: string;
  entry_point?: string;
  traces: Trace[];
}

export interface Trace {
  format: 'flowchart' | 'sequence' | 'step_by_step';
  data: FlowchartData | SequenceData | StepByStepData;
}

export interface FlowchartData {
  steps: FlowchartStep[];
  connections: FlowchartConnection[];
}

export interface FlowchartStep {
  id: string;
  label: string;
  type: 'start' | 'end' | 'process' | 'decision' | 'fork' | 'join';
  lineNumber?: number;
}

export interface FlowchartConnection {
  id: string;
  source: string;
  target: string;
  type: 'control_flow' | 'data_flow';
  label?: string;
}

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
  type: 'call' | 'return' | 'async' | 'create' | 'destroy';
  order: number;
}

export interface StepByStepData {
  file_path: string;
  language: string;
  code: string;
  steps: ExecutionStep[];
}

export interface ExecutionStep {
  id: string;
  lineNumber: number;
  description: string;
  variables?: Record<string, any>;
  callStack?: string[];
}
