"""
AIFlow Protocol Entities
Python TypedDict 实体定义，基于 analysis-schema-v1.0.0.json

提供类型提示支持，便于 IDE 代码补全和类型检查。

Python 版本要求: 3.11+ (使用 NotRequired)
如需支持 Python 3.8-3.10，请从 typing_extensions 导入 NotRequired。
"""

from typing import Any, List, Literal, TypedDict

# Python 3.11+ 使用内置 NotRequired
# Python 3.8-3.10 使用: from typing_extensions import NotRequired
try:
    from typing import NotRequired
except ImportError:
    from typing_extensions import NotRequired  # type: ignore


# ============================================================================
# 顶层结构
# ============================================================================

class AnalysisResult(TypedDict):
    """完整的分析结果 (顶层对象)"""
    schema_: str  # $schema 字段 (Python 使用 schema_ 避免与关键字冲突)
    version: str
    project_metadata: "ProjectMetadata"
    code_structure: "CodeStructure"
    execution_trace: "ExecutionTrace"
    behavior_metadata: NotRequired["BehaviorMetadata"]
    concurrency_info: NotRequired["ConcurrencyInfo"]
    prompt_templates: NotRequired["PromptTemplates"]


# ============================================================================
# 项目元数据 (Project Metadata)
# ============================================================================

class ProjectMetadata(TypedDict):
    """项目元数据"""
    project_name: str
    project_path: str
    language: str
    analyzed_at: str  # ISO 8601 timestamp
    framework: NotRequired[str]
    architecture_pattern: NotRequired[str]
    ai_model: NotRequired[str]
    total_lines: NotRequired[int]


# ============================================================================
# 代码结构 (Code Structure)
# ============================================================================

class CodeLocation(TypedDict):
    """代码位置"""
    file_path: str
    start_line: int
    end_line: int


class NodeMetadata(TypedDict, total=False):
    """节点元数据 (所有字段可选)"""
    ai_confidence: float
    ai_explanation: str
    code_location: CodeLocation


class NodePosition(TypedDict):
    """节点位置"""
    x: float
    y: float


class CodeNode(TypedDict):
    """代码节点"""
    id: str  # UUID v4
    label: str  # AI 生成的业务语义化名称
    stereotype: Literal["system", "module", "class", "function", "service", "component"]
    parent: NotRequired[str]  # 父节点 ID
    classes: NotRequired[List[str]]  # Cytoscape.js 样式类
    metadata: NotRequired[NodeMetadata]
    position: NotRequired[NodePosition]


class CodeEdge(TypedDict):
    """代码边"""
    id: str
    source: str  # 源节点 ID
    target: str  # 目标节点 ID
    type: Literal["dependency", "inheritance", "composition", "call"]
    label: NotRequired[str]


class CodeStructure(TypedDict):
    """代码结构"""
    nodes: List[CodeNode]
    edges: List[CodeEdge]


# ============================================================================
# 行为元数据 (Behavior Metadata)
# ============================================================================

class LaunchButton(TypedDict):
    """启动按钮"""
    id: str  # UUID v4
    node_id: str  # 关联的节点 ID
    name: str  # AI 生成的按钮名称
    type: Literal["macro", "micro"]
    description: NotRequired[str]
    icon: NotRequired[str]


class BehaviorMetadata(TypedDict):
    """行为元数据"""
    launch_buttons: NotRequired[List[LaunchButton]]


# ============================================================================
# 执行追踪 (Execution Trace)
# ============================================================================

class FlowchartStep(TypedDict):
    """流程图步骤"""
    id: str
    label: str
    type: Literal["start", "end", "process", "decision", "fork", "join"]
    data: NotRequired[Any]


class FlowchartConnection(TypedDict):
    """流程图连接"""
    id: str
    source: str  # 源步骤 ID
    target: str  # 目标步骤 ID
    type: Literal["control_flow", "data_flow"]
    label: NotRequired[str]


class FlowchartTrace(TypedDict):
    """流程图格式追踪"""
    steps: List[FlowchartStep]
    connections: List[FlowchartConnection]


class Lifeline(TypedDict):
    """生命线"""
    id: str
    label: str  # 执行实体名称
    type: str


class Message(TypedDict):
    """消息"""
    id: str
    source: str  # 源生命线 ID
    target: str  # 目标生命线 ID
    type: Literal["sync", "async", "return"]
    timestamp: float
    label: str


class SequenceTrace(TypedDict):
    """时序图格式追踪"""
    lifelines: List[Lifeline]
    messages: List[Message]


class ExecutionStep(TypedDict):
    """执行步骤"""
    id: str  # UUID v4
    order: int  # 局部顺序 (0开始)
    file_path: str
    line_number: int  # 行号 (1开始)
    code: str  # 代码内容
    timestamp: str  # ISO 8601 timestamp
    execution_order: int  # 全局唯一序号
    scope_id: str  # 所属作用域 ID
    duration: NotRequired[float]  # 执行时长 (毫秒)


class VariableChange(TypedDict):
    """变量变化"""
    timestamp: str  # ISO 8601 timestamp
    old_value: Any
    new_value: Any
    execution_order: int
    changed_at: str  # 格式: "file.py:123"


class Variable(TypedDict):
    """变量"""
    name: str
    type: str  # 变量类型
    value: Any
    memory_address: NotRequired[str]  # 十六进制字符串 (如 "0x7f8b2c3d1e40")
    size_bytes: NotRequired[int]
    is_mutable: NotRequired[bool]
    references: NotRequired[List[str]]  # 引用的其他对象 ID
    history: NotRequired[List[VariableChange]]


class VariableScope(TypedDict):
    """变量作用域"""
    id: str  # UUID v4
    scope_type: Literal["global", "local", "closure", "class", "module"]
    variables: List[Variable]
    timestamp: str  # ISO 8601 timestamp
    execution_order: int
    parent_scope_id: NotRequired[str]  # 父作用域 ID


class StackFrame(TypedDict):
    """栈帧"""
    id: str  # UUID v4
    function_name: str
    module_name: str
    file_path: str
    line_number: int
    depth: int  # 调用深度 (0 = 顶层)
    local_scope_id: str  # 关联的局部作用域 ID
    timestamp: str  # ISO 8601 timestamp
    execution_order: int
    is_recursive: NotRequired[bool]
    recursion_depth: NotRequired[int]
    arguments: NotRequired[dict]  # 函数参数
    parent_frame_id: NotRequired[str]  # 父栈帧 ID
    return_value: NotRequired[Any]


class StepByStepTrace(TypedDict):
    """单步详情格式追踪"""
    steps: List[ExecutionStep]
    variableScopes: List[VariableScope]
    callStack: List[StackFrame]


class Trace(TypedDict):
    """追踪 (支持多种格式)"""
    format: Literal["flowchart", "sequence", "step-by-step"]
    data: FlowchartTrace | SequenceTrace | StepByStepTrace


class TraceableUnit(TypedDict):
    """可追踪单元"""
    id: str  # UUID v4
    name: str  # AI 生成的功能名称
    type: Literal["single-trace", "multi-trace"]
    traces: List[Trace]
    subUnitIds: NotRequired[List[str]]  # 子单元 ID


class ExecutionTrace(TypedDict):
    """执行追踪"""
    traceable_units: List[TraceableUnit]


# ============================================================================
# 并发信息 (Concurrency Info)
# ============================================================================

class ConcurrencyFlow(TypedDict):
    """并发流"""
    id: str  # UUID v4
    type: Literal["parallel", "concurrent", "async", "sync_wait"]
    involved_units: List[str]  # 涉及的代码单元 ID
    start_point: str  # 起点节点 ID
    end_point: str  # 终点节点 ID
    dependencies: NotRequired[List[str]]  # 依赖的其他并发流 ID


class SyncPoint(TypedDict):
    """同步点"""
    id: str  # UUID v4
    location: str  # 同步点位置 (格式: "file.py:123")
    waiting_flows: List[str]  # 等待的并发流 ID
    type: Literal["barrier", "mutex", "semaphore", "join"]


class ConcurrencyInfo(TypedDict):
    """并发信息"""
    flows: NotRequired[List[ConcurrencyFlow]]
    sync_points: NotRequired[List[SyncPoint]]


# ============================================================================
# Prompt 模板记录 (Prompt Templates)
# ============================================================================

class UsedPrompt(TypedDict):
    """使用的 Prompt 模板记录"""
    id: str  # Prompt 模板 ID
    stage: Literal["project_understanding", "structure_recognition", "semantic_analysis", "execution_inference", "concurrency_detection"]
    executed_at: str  # ISO 8601 timestamp


class PromptTemplates(TypedDict):
    """Prompt 模板信息"""
    used_prompts: NotRequired[List[UsedPrompt]]


# ============================================================================
# 类型导出 (方便外部导入)
# ============================================================================

__all__ = [
    # 顶层
    "AnalysisResult",
    # 项目元数据
    "ProjectMetadata",
    # 代码结构
    "CodeNode",
    "CodeEdge",
    "CodeStructure",
    "CodeLocation",
    "NodeMetadata",
    "NodePosition",
    # 行为元数据
    "LaunchButton",
    "BehaviorMetadata",
    # 执行追踪
    "TraceableUnit",
    "Trace",
    "FlowchartTrace",
    "FlowchartStep",
    "FlowchartConnection",
    "SequenceTrace",
    "Lifeline",
    "Message",
    "StepByStepTrace",
    "ExecutionStep",
    "VariableScope",
    "Variable",
    "VariableChange",
    "StackFrame",
    "ExecutionTrace",
    # 并发信息
    "ConcurrencyFlow",
    "SyncPoint",
    "ConcurrencyInfo",
    # Prompt 模板
    "UsedPrompt",
    "PromptTemplates",
]
