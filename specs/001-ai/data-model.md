# Data Model: AI分析指挥与可视化平台

**Feature**: 001-ai | **Date**: 2025-10-09 | **Phase**: 1 - Design

## 1. 核心实体定义 (Core Entities)

### 1.1 AI 调度层实体

#### PromptTemplate (核心指令集模板)

**职责**：定义用于驱动 AI 分析的 Prompt 模板

```python
@dataclass
class PromptTemplate:
    """Prompt 模板实体"""
    id: str                              # 唯一标识符，格式：{language}-{stage}-v{version}
    version: str                         # 语义化版本号 (e.g., "1.2.0")
    stage: AnalysisStage                 # 分析阶段（枚举）
    target_language: str                 # 目标编程语言 (python, javascript, etc.)
    template_content: str                # Jinja2 模板内容
    input_schema: dict                   # 输入数据 JSON Schema
    output_schema: dict                  # 期望输出数据 JSON Schema
    quality_criteria: dict               # 质量标准定义
    examples: list[dict]                 # 示例输入输出
    metadata: PromptMetadata             # 元数据（创建时间、作者、测试结果）

    def render(self, context: dict) -> str:
        """渲染 Prompt 模板"""
        pass

    def validate_input(self, data: dict) -> bool:
        """验证输入数据格式"""
        pass

    def validate_output(self, data: dict) -> bool:
        """验证输出数据格式"""
        pass

class AnalysisStage(Enum):
    """AI 分析阶段枚举"""
    PROJECT_UNDERSTANDING = "project_understanding"
    STRUCTURE_RECOGNITION = "structure_recognition"
    SEMANTIC_ANALYSIS = "semantic_analysis"
    EXECUTION_INFERENCE = "execution_inference"
    CONCURRENCY_DETECTION = "concurrency_detection"
```

#### AIAdapter (AI 适配器)

**职责**：连接外部 AI 工具，发送 Prompt 并接收分析结果

```python
@dataclass
class AIAdapter:
    """AI 适配器实体"""
    id: str                              # 适配器唯一 ID
    type: AIAdapterType                  # 适配器类型（枚举）
    name: str                            # 显示名称 (e.g., "Claude Code")
    config: AIAdapterConfig              # 配置信息（API 端点、认证等）
    status: AdapterStatus                # 适配器状态（枚举）
    capabilities: dict                   # 能力声明（支持的语言、最大 token 等）
    metadata: AdapterMetadata            # 元数据（版本、最后健康检查时间）

    async def analyze(self, request: PromptRequest) -> AnalysisResult:
        """执行 AI 分析"""
        pass

    async def health_check(self) -> bool:
        """健康检查"""
        pass

    def get_capabilities(self) -> dict:
        """获取适配器能力"""
        pass

class AIAdapterType(Enum):
    """AI 适配器类型枚举"""
    IDE_INTEGRATED = "ide_integrated"      # VS Code Copilot, JetBrains AI
    CLI_TOOL = "cli_tool"                  # Claude Code, Cursor, Aider
    CLOUD_API = "cloud_api"                # OpenAI, Anthropic, Google Gemini
    LOCAL_MODEL = "local_model"            # Ollama, LM Studio

class AdapterStatus(Enum):
    """适配器状态枚举"""
    AVAILABLE = "available"                # 可用
    BUSY = "busy"                          # 繁忙
    OFFLINE = "offline"                    # 离线
    ERROR = "error"                        # 错误状态
```

#### AnalysisJob (分析任务)

**职责**：管理完整的 AI 分析流程，协调多阶段分析

```python
@dataclass
class AnalysisJob:
    """分析任务实体"""
    id: str                              # 任务唯一 ID
    project_path: str                    # 项目路径
    status: JobStatus                    # 任务状态（枚举）
    stages: list[AnalysisStageExecution] # 各阶段执行状态
    results: AnalysisResults             # 分析结果（符合标准数据协议）
    adapter_id: str                      # 使用的适配器 ID
    metadata: JobMetadata                # 元数据（创建时间、耗时、token 消耗）
    config: AnalysisConfig               # 分析配置（范围限定、优先级）

    def execute_stage(self, stage: AnalysisStage) -> AnalysisResult:
        """执行特定分析阶段"""
        pass

    def can_resume(self) -> bool:
        """检查是否可以恢复（断点续传）"""
        pass

    def resume(self) -> None:
        """从最近的检查点恢复"""
        pass

class JobStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"                  # 待执行
    RUNNING = "running"                  # 执行中
    PAUSED = "paused"                    # 已暂停
    COMPLETED = "completed"              # 已完成
    FAILED = "failed"                    # 失败
    CANCELLED = "cancelled"              # 已取消

@dataclass
class AnalysisStageExecution:
    """单个分析阶段的执行状态"""
    stage: AnalysisStage
    status: StageStatus
    prompt_id: str                       # 使用的 Prompt 模板 ID
    start_time: datetime
    end_time: Optional[datetime]
    duration: Optional[timedelta]
    result: Optional[dict]               # 阶段输出结果
    error: Optional[str]                 # 错误信息

class StageStatus(Enum):
    """阶段状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"                  # 跳过（缓存命中）
```

#### AnalysisCache (分析缓存)

**职责**：缓存 AI 分析结果，避免重复调用

```python
@dataclass
class AnalysisCache:
    """分析缓存实体"""
    id: str                              # 缓存唯一 ID
    project_hash: str                    # 项目内容哈希（用于缓存失效检测）
    stage: AnalysisStage                 # 缓存的分析阶段
    result: dict                         # 缓存的分析结果
    created_at: datetime                 # 创建时间
    accessed_at: datetime                # 最后访问时间
    hit_count: int                       # 命中次数
    lru_priority: int                    # LRU 优先级

    def is_valid(self, current_hash: str) -> bool:
        """检查缓存是否仍然有效"""
        pass

    def touch(self) -> None:
        """更新访问时间和命中次数"""
        pass
```

### 1.2 数据协议层实体

#### CodeStructure (代码结构)

**职责**：表示层级化的代码结构，用于 Cytoscape.js 渲染

```python
@dataclass
class CodeStructure:
    """代码结构实体"""
    nodes: list[CodeNode]                # 节点列表
    edges: list[CodeEdge]                # 边列表
    metadata: StructureMetadata          # 元数据

@dataclass
class CodeNode:
    """代码节点实体"""
    id: str                              # 节点唯一 ID
    label: str                           # AI 生成的业务语义化名称
    parent: Optional[str]                # 父节点 ID（用于层级关系）
    classes: list[str]                   # Cytoscape.js 样式类
    stereotype: str                      # 节点类型（module, class, function, etc.）
    metadata: NodeMetadata               # AI 分析元数据（置信度、解释）
    position: Optional[dict]             # 节点位置（x, y）
    collapsed: bool                      # 是否折叠

@dataclass
class CodeEdge:
    """代码边实体"""
    id: str
    source: str                          # 源节点 ID
    target: str                          # 目标节点 ID
    type: EdgeType                       # 边类型（枚举）
    label: Optional[str]                 # 边标签
    metadata: EdgeMetadata

class EdgeType(Enum):
    """边类型枚举"""
    DEPENDENCY = "dependency"            # 依赖关系
    INHERITANCE = "inheritance"          # 继承关系
    COMPOSITION = "composition"          # 组合关系
    CALL = "call"                        # 调用关系
```

#### FunctionalUnit (功能单元)

**职责**：表示具备独立业务功能的代码单元，附带启动按钮

```python
@dataclass
class FunctionalUnit:
    """功能单元实体"""
    id: str                              # 功能单元唯一 ID
    node_id: str                         # 对应的 CodeNode ID
    name: str                            # AI 生成的功能名称
    description: str                     # 功能描述
    launch_button: LaunchButton          # 启动按钮配置
    type: UnitType                       # 功能单元类型（枚举）
    code_location: CodeLocation          # 代码位置信息
    metadata: UnitMetadata               # AI 分析元数据

class UnitType(Enum):
    """功能单元类型枚举"""
    MACRO = "macro"                      # 宏观功能（大模块）
    MICRO = "micro"                      # 微观功能（小模块）
    ATOMIC = "atomic"                    # 原子功能（单个函数）

@dataclass
class LaunchButton:
    """启动按钮实体"""
    id: str
    name: str                            # AI 生成的按钮名称
    description: str                     # 按钮描述
    icon: Optional[str]                  # 图标（可选）
    type: ButtonType                     # 按钮类型（枚举）

class ButtonType(Enum):
    """按钮类型枚举"""
    PRIMARY = "primary"                  # 大按钮（宏观联动）
    SECONDARY = "secondary"              # 小按钮（子流程）
```

#### ExecutionTrace (执行追踪)

**职责**：表示代码执行的追踪数据，支持多种可视化格式

```python
@dataclass
class ExecutionTrace:
    """执行追踪实体"""
    traceable_units: list[TraceableUnit] # 可执行单元列表
    metadata: TraceMetadata

@dataclass
class TraceableUnit:
    """可执行单元实体"""
    id: str                              # 可执行单元唯一 ID
    name: str                            # AI 生成的功能名称
    type: TraceType                      # 追踪类型（枚举）
    sub_unit_ids: list[str]              # 子单元 ID 数组（行为父子关系）
    traces: list[Trace]                  # 流程轨迹列表（支持多种格式）
    metadata: TraceUnitMetadata

class TraceType(Enum):
    """追踪类型枚举"""
    SINGLE_TRACE = "single_trace"        # 单线程执行
    MULTI_TRACE = "multi_trace"          # 多线程联动

@dataclass
class Trace:
    """流程轨迹实体（支持多种格式）"""
    format: TraceFormat                  # 轨迹格式（枚举）
    data: dict                           # 轨迹数据（格式依赖于 format）

class TraceFormat(Enum):
    """轨迹格式枚举"""
    FLOWCHART = "flowchart"              # 流程图格式（D3.js）
    SEQUENCE = "sequence"                # 时序图格式（D3.js）
    STEP_BY_STEP = "step_by_step"        # 单步详情格式（Monaco Editor）

# 流程图格式数据结构
@dataclass
class FlowchartTrace:
    """流程图追踪数据"""
    steps: list[FlowStep]
    connections: list[FlowConnection]

@dataclass
class FlowStep:
    """流程图步骤"""
    id: str
    label: str
    type: StepType                       # 步骤类型（枚举）
    data: dict                           # 步骤数据

class StepType(Enum):
    """步骤类型枚举"""
    START = "start"
    END = "end"
    PROCESS = "process"
    DECISION = "decision"
    FORK = "fork"                        # 并发分叉
    JOIN = "join"                        # 并发汇合

@dataclass
class FlowConnection:
    """流程图连接"""
    id: str
    source: str                          # 源步骤 ID
    target: str                          # 目标步骤 ID
    label: Optional[str]                 # 连接标签
    type: ConnectionType                 # 连接类型（枚举）

class ConnectionType(Enum):
    """连接类型枚举"""
    CONTROL_FLOW = "control_flow"        # 控制流
    DATA_FLOW = "data_flow"              # 数据流

# 时序图格式数据结构
@dataclass
class SequenceTrace:
    """时序图追踪数据"""
    lifelines: list[Lifeline]
    messages: list[Message]

@dataclass
class Lifeline:
    """时序图生命线"""
    id: str
    label: str                           # 执行实体名称（线程、服务、组件）
    type: str                            # 实体类型

@dataclass
class Message:
    """时序图消息"""
    id: str
    source: str                          # 源生命线 ID
    target: str                          # 目标生命线 ID
    type: MessageType                    # 消息类型（枚举）
    timestamp: float                     # 时间戳
    label: str                           # 消息标签

class MessageType(Enum):
    """消息类型枚举"""
    SYNC = "sync"                        # 同步调用
    ASYNC = "async"                      # 异步调用
    RETURN = "return"                    # 返回

# 单步详情格式数据结构
@dataclass
class StepByStepTrace:
    """单步运行详情追踪数据"""
    steps: list[ExecutionStep]
    variable_scopes: list[VariableScope]
    call_stack: list[StackFrame]

@dataclass
class ExecutionStep:
    """执行步骤"""
    id: str
    order: int                           # 执行顺序
    file_path: str                       # 代码文件路径
    line_number: int                     # 行号
    code: str                            # 代码内容
    timestamp: float                     # 时间戳
    duration: Optional[float]            # 执行时长
    scope_id: str                        # 所属作用域 ID

@dataclass
class VariableScope:
    """变量作用域 - 用于单步详情视图"""
    id: str                              # 作用域唯一标识符
    scope_type: ScopeType                # 作用域类型（枚举）
    parent_scope_id: Optional[str]       # 父作用域 ID（支持嵌套）
    variables: list[Variable]            # 该作用域内的变量列表
    timestamp: str                       # ISO 8601 时间戳（进入作用域时刻）
    execution_order: int                 # 执行序号（全局唯一递增）

class ScopeType(Enum):
    """作用域类型枚举"""
    GLOBAL = "global"                    # 全局作用域
    LOCAL = "local"                      # 局部作用域（函数内）
    CLOSURE = "closure"                  # 闭包作用域
    CLASS = "class"                      # 类作用域
    MODULE = "module"                    # 模块作用域

@dataclass
class Variable:
    """变量实体 - 单步详情视图中的变量状态"""
    name: str                            # 变量名
    type: str                            # 类型（Python: type().__name__）
    value: Any                           # 当前值（序列化为 JSON）
    memory_address: Optional[str]        # 内存地址（十六进制字符串，如 "0x7f8b2c3d1e40"）
    size_bytes: Optional[int]            # 内存占用（字节）
    is_mutable: bool                     # 是否可变（Python: isinstance(x, (list, dict, set))）
    references: list[str]                # 引用的其他对象 ID 列表（用于对象引用图）
    history: list[VariableChange]        # 历史变化轨迹

@dataclass
class VariableChange:
    """变量变化记录 - 用于变量历史轨迹查看"""
    timestamp: str                       # 变化时刻（ISO 8601）
    old_value: Any                       # 旧值
    new_value: Any                       # 新值
    changed_at: str                      # 修改位置（格式："file.py:123"）
    execution_order: int                 # 变化时的执行序号

@dataclass
class StackFrame:
    """调用栈帧 - 用于单步详情视图的调用栈显示"""
    id: str                              # 栈帧唯一标识符
    function_name: str                   # 函数名
    module_name: str                     # 所属模块
    file_path: str                       # 源代码文件路径
    line_number: int                     # 当前执行行号
    depth: int                           # 调用深度（0 = 顶层入口）
    is_recursive: bool                   # 是否递归调用
    recursion_depth: Optional[int]       # 递归深度（如果 is_recursive=True）
    arguments: dict[str, Any]            # 函数参数（名称 -> 值）
    local_scope_id: str                  # 关联的局部作用域 ID
    parent_frame_id: Optional[str]       # 父栈帧 ID（调用链）
    timestamp: str                       # 进入栈帧的时间戳（ISO 8601）
    execution_order: int                 # 执行序号
    return_value: Optional[Any]          # 返回值（函数返回后填充）
```

#### ConcurrencyInfo (并发信息)

**职责**：表示并发执行的流程信息

```python
@dataclass
class ConcurrencyInfo:
    """并发信息实体"""
    flows: list[ConcurrencyFlow]
    sync_points: list[SyncPoint]
    metadata: ConcurrencyMetadata

@dataclass
class ConcurrencyFlow:
    """并发流实体"""
    id: str
    type: ConcurrencyType                # 并发类型（枚举）
    involved_units: list[str]            # 涉及的代码单元 ID
    start_point: str                     # 起点节点 ID
    end_point: str                       # 终点节点 ID
    dependencies: list[str]              # 依赖的其他并发流 ID

class ConcurrencyType(Enum):
    """并发类型枚举"""
    PARALLEL = "parallel"                # 并行执行
    CONCURRENT = "concurrent"            # 并发执行
    ASYNC = "async"                      # 异步执行
    SYNC_WAIT = "sync_wait"              # 同步等待

@dataclass
class SyncPoint:
    """同步点实体"""
    id: str
    location: str                        # 同步点位置
    waiting_flows: list[str]             # 等待的并发流 ID
    type: SyncType                       # 同步类型（枚举）

class SyncType(Enum):
    """同步类型枚举"""
    BARRIER = "barrier"                  # 栅栏（所有流到达才继续）
    MUTEX = "mutex"                      # 互斥锁
    SEMAPHORE = "semaphore"              # 信号量
    JOIN = "join"                        # Join 操作
```

### 1.3 可视化层实体

#### AnimationScene (动画场景)

**职责**：管理执行动画的场景配置和状态

```python
@dataclass
class AnimationScene:
    """动画场景实体"""
    id: str
    type: SceneType                      # 场景类型（枚举）
    involved_units: list[str]            # 涉及的功能单元 ID
    duration: float                      # 动画总时长（秒）
    current_time: float                  # 当前播放时间
    status: AnimationStatus              # 动画状态（枚举）
    playback_speed: float                # 播放速度（0.1x - 10x）
    bookmarks: list[Bookmark]            # 执行书签列表

    def play(self) -> None:
        """播放动画"""
        pass

    def pause(self) -> None:
        """暂停动画"""
        pass

    def seek_to(self, time: float) -> None:
        """时间回溯"""
        pass

    def set_speed(self, speed: float) -> None:
        """设置播放速度"""
        pass

class SceneType(Enum):
    """场景类型枚举"""
    MACRO = "macro"                      # 宏观联动场景
    MICRO = "micro"                      # 微观子流程场景

class AnimationStatus(Enum):
    """动画状态枚举"""
    IDLE = "idle"
    PLAYING = "playing"
    PAUSED = "paused"
    COMPLETED = "completed"

@dataclass
class Bookmark:
    """执行书签实体"""
    id: str
    name: str                            # 书签名称
    time: float                          # 时间点
    description: str                     # 描述
    snapshot: dict                       # 状态快照
```

#### StepDetailView (单步详情视图)

**职责**：管理单步运行详情的视图状态

```python
@dataclass
class StepDetailView:
    """单步详情视图实体"""
    id: str
    current_step_id: str                 # 当前执行步骤 ID
    file_path: str                       # 当前代码文件路径
    line_number: int                     # 当前代码行号
    variable_snapshot: list[Variable]    # 当前变量快照
    call_stack: list[StackFrame]         # 当前调用栈
    memory_snapshot: Optional[MemorySnapshot] # 内存快照（可选）
    breakpoints: list[Breakpoint]        # 断点列表
    mode: DetailViewMode                 # 视图模式（枚举）

    def step_into(self) -> None:
        """单步进入"""
        pass

    def step_over(self) -> None:
        """单步跳过"""
        pass

    def step_out(self) -> None:
        """单步跳出"""
        pass

class DetailViewMode(Enum):
    """详情视图模式枚举"""
    NORMAL = "normal"                    # 正常模式
    HYPOTHETICAL = "hypothetical"        # 假设分析模式

@dataclass
class Breakpoint:
    """断点实体"""
    id: str
    file_path: str
    line_number: int
    type: BreakpointType                 # 断点类型（枚举）
    condition: Optional[str]             # 条件表达式（条件断点）
    enabled: bool                        # 是否启用

class BreakpointType(Enum):
    """断点类型枚举"""
    LINE = "line"                        # 行断点
    CONDITIONAL = "conditional"          # 条件断点
    LOG = "log"                          # 日志断点

@dataclass
class MemorySnapshot:
    """内存快照实体"""
    timestamp: float
    heap: list[HeapObject]               # 堆对象列表
    stack: list[StackObject]             # 栈对象列表
    total_memory: int                    # 总内存占用（字节）

@dataclass
class HeapObject:
    """堆对象"""
    address: str                         # 内存地址
    type: str                            # 对象类型
    size: int                            # 对象大小（字节）
    references: list[str]                # 引用的其他对象地址
```

## 2. 实体关系图 (Entity Relationship Diagram)

### 2.1 AI 调度层实体关系

```
AnalysisJob 1──*→ AnalysisStageExecution
    │
    ├──1→ AIAdapter
    ├──*→ PromptTemplate (通过 AnalysisStageExecution)
    └──1→ AnalysisResults (标准数据协议)

AnalysisCache *──1→ AnalysisStage
            ├──1→ project_hash
            └──1→ cached_result

PromptTemplate *──1→ AnalysisStage
               ├──1→ target_language
               └──*→ quality_criteria
```

### 2.2 数据协议层实体关系

```
CodeStructure 1──*→ CodeNode
              1──*→ CodeEdge

CodeNode *──1→ parent (CodeNode, optional)
         *──1→ FunctionalUnit (optional)

FunctionalUnit 1──1→ LaunchButton
               1──1→ CodeLocation
               1──*→ ExecutionTrace

ExecutionTrace 1──*→ TraceableUnit

TraceableUnit 1──*→ Trace
              *──*→ sub_unit (TraceableUnit)

ConcurrencyInfo 1──*→ ConcurrencyFlow
                1──*→ SyncPoint

ConcurrencyFlow *──*→ TraceableUnit
```

### 2.3 可视化层实体关系

```
AnimationScene 1──*→ FunctionalUnit
               1──*→ Bookmark

StepDetailView 1──1→ ExecutionStep (current)
               1──*→ Variable (snapshot)
               1──*→ StackFrame (call_stack)
               1──*→ Breakpoint
               1──1→ MemorySnapshot (optional)

Breakpoint *──1→ file_path + line_number
```

## 3. 状态机定义 (State Machines)

### 3.1 AnalysisJob 状态机

```
                 ┌─────────┐
                 │ PENDING │
                 └────┬────┘
                      │ execute()
                      ▼
            ┌─────────────────┐
            │     RUNNING     │
            └─┬───────────┬───┘
              │           │ pause()
              │           ▼
              │    ┌──────────┐
              │    │  PAUSED  │──resume()──┐
              │    └──────────┘            │
              │           │ cancel()       │
              │           ▼                ▼
    complete()│    ┌───────────┐   ┌─────────────┐
              ├───►│ COMPLETED │   │   RUNNING   │
              │    └───────────┘   └─────────────┘
         error│                            │
              ▼                            │ cancel()
         ┌────────┐                        │
         │ FAILED │◄───────────────────────┘
         └────────┘
              │ retry()
              ▼
         ┌─────────┐
         │ PENDING │
         └─────────┘
```

### 3.2 AIAdapter 状态机

```
         ┌───────────┐
         │ AVAILABLE │◄──┐
         └─────┬─────┘   │
               │ analyze()
               ▼         │ complete/timeout
         ┌──────────┐    │
         │   BUSY   │────┘
         └─────┬────┘
               │ error
               ▼
         ┌─────────┐
         │  ERROR  │──health_check()──►AVAILABLE
         └────┬────┘
              │ timeout
              ▼
         ┌──────────┐
         │ OFFLINE  │──health_check()──►AVAILABLE
         └──────────┘
```

### 3.3 AnimationScene 状态机

```
         ┌──────┐
         │ IDLE │
         └───┬──┘
             │ play()
             ▼
      ┌───────────┐
      │  PLAYING  │◄──┐
      └─────┬─────┘   │
            │         │ resume()
      pause()│         │
            ▼         │
      ┌──────────┐    │
      │  PAUSED  │────┘
      └─────┬────┘
            │ play() / seek_to(end)
            ▼
      ┌───────────┐
      │ COMPLETED │
      └───────────┘
```

## 4. 数据持久化策略

### 4.1 后端数据持久化（Python）

**存储方案**：
- **分析结果**：文件系统（JSON 文件）+ SQLite 索引
- **缓存数据**：SQLite（轻量级、无需额外服务）
- **Prompt 模板**：文件系统（YAML 文件）+ Git 版本控制

**目录结构**：
```
~/.aiflow/
├── cache/
│   └── analysis_cache.db         # SQLite 数据库
├── results/
│   └── {project_hash}/
│       ├── project_metadata.json
│       ├── code_structure.json
│       ├── execution_trace.json
│       └── concurrency_info.json
├── prompts/
│   └── registry.yaml             # Prompt 索引
└── config/
    └── adapters.yaml             # 适配器配置
```

### 4.2 前端数据持久化（Web）

**存储方案**：
- **分析结果**：IndexedDB（大数据存储，支持离线）
- **用户偏好**：LocalStorage（轻量级键值对）
- **书签和历史**：IndexedDB

**IndexedDB Schema**：
```javascript
// 数据库名称：aiflow_db
// 版本：1

// ObjectStore 1: analysis_results
{
  keyPath: "id",
  indexes: [
    { name: "project_hash", keyPath: "project_hash", unique: false },
    { name: "created_at", keyPath: "created_at", unique: false }
  ]
}

// ObjectStore 2: bookmarks
{
  keyPath: "id",
  indexes: [
    { name: "scene_id", keyPath: "scene_id", unique: false }
  ]
}

// ObjectStore 3: user_preferences
{
  keyPath: "key"
}
```

## 5. 数据验证与完整性

### 5.1 JSON Schema 验证

**策略**：
- 所有进出 AI 适配器的数据必须通过 JSON Schema 验证
- 前端接收的可视化数据必须通过 schema 验证
- Schema 版本化管理，向后兼容至少 2 个 MAJOR 版本

**验证点**：
1. Prompt 输入数据验证（`PromptTemplate.validate_input()`）
2. AI 返回结果验证（`AIAdapter.analyze()` 后）
3. 标准数据协议验证（生成最终 JSON 前）
4. 前端接收数据验证（加载 IndexedDB 数据前）

### 5.2 数据完整性检查

**检查项**：
1. **引用完整性**：
   - `CodeNode.parent` 必须指向存在的节点 ID
   - `TraceableUnit.sub_unit_ids` 必须指向存在的单元 ID
   - `FunctionalUnit.node_id` 必须指向存在的节点 ID

2. **状态一致性**：
   - `AnalysisJob` 的各阶段状态必须逻辑一致（不能跳过阶段）
   - `AnimationScene.current_time` 不能超过 `duration`

3. **数据格式**：
   - 所有时间戳使用 ISO 8601 格式
   - 所有 ID 使用 UUID v4 格式
   - 版本号使用语义化版本格式

## 6. 性能优化考虑

### 6.1 数据分页与懒加载

**策略**：
- **CodeStructure**：超过 1000 个节点时启用虚拟化渲染
- **ExecutionTrace**：超过 10000 步时启用分页加载（每页 1000 步）
- **Variable.history**：超过 100 条变化记录时按需加载

### 6.2 数据压缩

**策略**：
- 大型分析结果文件（>10MB）使用 gzip 压缩存储
- 前端 IndexedDB 存储使用浏览器原生压缩
- 网络传输使用 HTTP gzip 压缩

### 6.3 缓存策略

**多级缓存**：
1. **L1 - 内存缓存**（Python 进程内存）：
   - 最近使用的 Prompt 模板（最多 20 个）
   - 当前分析任务的中间结果

2. **L2 - 磁盘缓存**（SQLite/文件系统）：
   - 完整的分析结果（LRU 淘汰，最多 100 个项目）
   - Prompt 模板文件（持久化）

3. **L3 - 前端缓存**（IndexedDB）：
   - 用户最近访问的分析结果（最多 10 个项目）
   - 用户偏好和书签（持久化）

## 7. 总结

本数据模型设计涵盖了 AI 分析指挥与可视化平台的三大核心层：
- **AI 调度层**：管理 Prompt 模板、AI 适配器、分析任务和缓存
- **数据协议层**：定义标准化的代码结构、执行追踪、并发信息
- **可视化层**：管理动画场景、单步详情视图、用户交互状态

关键设计原则：
- **类型安全**：使用 TypedDict 和枚举确保类型安全
- **可扩展**：插件化适配器、版本化 Prompt 模板、可选字段
- **性能优先**：分页加载、懒加载、多级缓存、虚拟化渲染
- **容错性**：状态机管理、数据验证、引用完整性检查

下一步：生成详细的 API 合约和 JSON Schema 定义（`contracts/` 目录）。
