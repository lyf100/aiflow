# AIFlow 架构设计文档

**Architecture Design Document for AIFlow Code Behavior Sandbox**

---

## 📋 目录

1. [设计哲学](#设计哲学)
2. [核心架构](#核心架构)
3. [数据流转](#数据流转)
4. [关键设计决策](#关键设计决策)
5. [技术选型理由](#技术选型理由)
6. [扩展性设计](#扩展性设计)
7. [性能优化策略](#性能优化策略)

---

## 🎯 设计哲学

### 1. 智能委托策略（Intelligent Delegation）

**核心理念**：平台不做解析，只做指挥。

```
传统方式：
  代码 → 自建解析器 → AST → 分析逻辑 → 结果

AIFlow 方式：
  代码 → 核心指令集 → AI工具（解析+分析+语义理解） → 标准JSON → 可视化
```

#### 为什么这样设计？

1. **专业分工**
   - AI 擅长：语义理解、业务推理、模块命名
   - 平台擅长：数据协议、可视化、用户交互

2. **跨语言支持**
   - 无需为每种语言编写解析器
   - AI 天然支持多语言理解

3. **降低维护成本**
   - 语言语法更新由 AI 模型自动适应
   - 平台只需维护指令集和数据协议

### 2. 技术栈无关性（Technology Agnostic）

**核心理念**：作为"无外壳"的 MCP 工具，与具体 AI 服务解耦。

#### SPI（Service Provider Interface）设计

```python
# 抽象接口
class BaseAIAdapter(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> AIResponse:
        pass

# 具体实现
class ClaudeAdapter(BaseAIAdapter):
    async def generate(self, prompt: str) -> AIResponse:
        # Claude-specific implementation

class OpenAIAdapter(BaseAIAdapter):
    async def generate(self, prompt: str) -> AIResponse:
        # OpenAI-specific implementation
```

#### 为什么这样设计？

1. **降低供应商锁定风险**
   - AI 服务可替换
   - 不依赖单一厂商

2. **多模型协同**
   - 不同阶段使用不同模型
   - Claude 擅长推理，GPT-4 擅长创造

3. **成本优化**
   - 按需选择性价比最高的模型
   - 支持本地开源模型

### 3. 层级与行为统一（Unified Hierarchy & Behavior）

**核心理念**：传统工具将结构和行为分离，AIFlow 深度融合。

#### 传统工具的问题

```
静态分析工具：
  ✅ 展示代码结构
  ❌ 不知道如何运行
  ❌ 无法理解业务含义

动态调试工具：
  ✅ 展示执行流程
  ❌ 缺失宏观架构视角
  ❌ 无法理解模块协同
```

#### AIFlow 的解决方案

```
统一沙盘：
  ✅ 代码结构本身是交互式的
  ✅ 每个节点都有启动按钮
  ✅ 可以在任意层级观察行为
  ✅ 宏观架构和微观实现无缝切换
```

### 4. 嵌套式行为启动（Nested Behavior Launch）

**核心创新**：多层级、可嵌套的执行轨迹。

#### 三层按钮体系

```
📦 System Level (大按钮 - Macro)
  作用: 启动系统级多流程联动
  示例: "完整用户注册流程"
  特点: 涉及多个模块协同

  ├─ 📂 Module Level (小按钮 - Micro)
  │   作用: 启动子模块独立流程
  │   示例: "邮箱验证"
  │   特点: 单一模块内的完整业务
  │
  │   └─ 🔧 Function Level (微按钮 - Function)
  │       作用: 单步执行函数逻辑
  │       示例: "validateEmail()"
  │       特点: 单个函数的执行轨迹
```

#### 数据结构设计

```typescript
interface LaunchButton {
  id: string;                      // UUID v4
  node_id: string;                // 关联的代码节点
  name: string;                   // AI 生成的业务名称
  type: "macro" | "micro";        // 按钮类型
  level: "system" | "module" | "component" | "function";

  // 嵌套关系
  parent_button_id: string | null;  // 父按钮ID
  child_button_ids: string[];       // 子按钮ID列表

  // 执行关联
  traceable_unit_id: string;        // 关联的执行轨迹

  // AI 元数据
  metadata: {
    ai_confidence: number;          // AI 推理置信度
    ai_explanation: string;         // 命名和功能推理依据
    estimated_duration: number;     // 预估执行时间（毫秒）
    requires_input: boolean;        // 是否需要用户输入
    has_side_effects: boolean;      // 是否有副作用
  };
}
```

### 5. 并发行为精确表达（Precise Concurrency Expression）

**核心理念**：现代软件充满并发，必须精确表达。

#### 三种并发表达方式

**方式 1：时序图（Sequence Diagram）**
```
适用场景: 异步消息传递、服务调用
表达能力:
  - 生命线（Lifeline）
  - 同步/异步消息
  - 返回值
  - 并行执行区域
```

**方式 2：流程图（Flowchart）**
```
适用场景: 线程分叉/汇合、并发控制
表达能力:
  - fork 节点（并发分叉）
  - join 节点（并发汇合）
  - 同步点（Sync Point）
  - 数据流向
```

**方式 3：多流程联动动画（Multi-Flow Animation）**
```
适用场景: 主结构图上的并发可视化
表达能力:
  - 多条"脉冲"同时流动
  - 不同颜色区分不同流程
  - 实时同步/异步状态
  - 线程/进程间通信
```

### 6. 全方位用户控制（Full User Control）

**核心理念**：用户不是观察者，是探索者。

#### 控制维度

| 维度 | 控制能力 | 实现方式 |
|------|---------|----------|
| **时间控制** | 播放/暂停/回溯 | 执行步骤索引 + 时间轴 |
| **空间控制** | 展开/折叠/缩放 | Cytoscape.js 交互 |
| **视角切换** | 结构图 ↔ 时序图 ↔ 流程图 | 多视图协同 |
| **细节探索** | 单步详情/变量追踪 | Monaco Editor + D3.js |
| **并发观察** | 多流程同时播放 | 动画同步引擎 |

---

## 🏗️ 核心架构

### 三层架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                   核心指令集层 (Prompt Library)              │
│                                                              │
│  ┌──────────────────────┐    ┌──────────────────────────┐  │
│  │  Prompt 模板库       │    │  Jinja2 渲染引擎         │  │
│  │  - 5阶段分析模板     │ →  │  - 模板变量替换          │  │
│  │  - 版本化管理        │    │  - 输入数据验证          │  │
│  │  - 语言特定优化      │    │  - 自定义过滤器          │  │
│  └──────────────────────┘    └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   AI 适配器层 (Adapter SPI)                  │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Claude 4.5   │  │ OpenAI GPT-4 │  │ Google Gemini│      │
│  │ Adapter      │  │ Adapter      │  │ Adapter      │      │
│  │              │  │              │  │              │      │
│  │ - 重试机制   │  │ - 流式输出   │  │ - 本地缓存   │      │
│  │ - 速率限制   │  │ - 并发控制   │  │ - 错误降级   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              标准数据协议层 (JSON Schema v1.0.0)             │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │ Protocol       │  │ Validator      │  │ Serializer   │  │
│  │ Entities       │  │                │  │              │  │
│  │                │  │ - Schema校验   │  │ - JSON序列化 │  │
│  │ - TypedDict    │  │ - 引用完整性   │  │ - gzip压缩   │  │
│  │ - TypeScript   │  │ - 时间戳校验   │  │ - 增量更新   │  │
│  └────────────────┘  └────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              可视化引擎层 (Visualization Engine)             │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Cytoscape.js (主引擎)                       │  │
│  │                                                       │  │
│  │  - 行为沙盘渲染                                       │  │
│  │  - 嵌套启动按钮                                       │  │
│  │  - 多流程联动动画                                     │  │
│  │  - 层级展开/折叠                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────┐    ┌──────────────────────────┐  │
│  │ D3.js (辅助引擎)     │    │ Monaco Editor            │  │
│  │                      │    │                          │  │
│  │ - 时序图             │    │ - 代码高亮               │  │
│  │ - 流程图             │    │ - 单步详情               │  │
│  │ - 变量追踪图         │    │ - 调用堆栈               │  │
│  │ - 调用堆栈可视化     │    │ - 变量作用域             │  │
│  └──────────────────────┘    └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 层级职责详解

#### Layer 1: 核心指令集层

**职责**：
- 管理 Prompt 模板的版本和注册
- 渲染模板并填充输入数据
- 验证模板格式和输入数据完整性

**关键组件**：

```python
# Prompt 模板管理器
class PromptTemplateManager:
    def load_template(self, language, stage, version=None):
        """从注册表加载模板"""

    def get_template_by_id(self, template_id):
        """通过ID直接获取模板"""

    def list_templates(self, filters=None):
        """列出所有可用模板"""

# Jinja2 渲染引擎
class PromptRenderer:
    def render(self, language, stage, input_data, validate_input=True):
        """渲染模板并返回完整Prompt"""

    def _register_filters(self):
        """注册自定义Jinja2过滤器"""
```

**设计模式**：
- **注册表模式**：registry.yaml 集中管理模板元数据
- **模板方法模式**：统一的渲染流程
- **策略模式**：不同语言使用不同模板策略

#### Layer 2: AI 适配器层

**职责**：
- 统一不同 AI 服务的接口
- 处理重试、速率限制、错误降级
- 提供流式和非流式两种生成模式

**关键组件**：

```python
# 抽象基类
class BaseAIAdapter(ABC):
    @abstractmethod
    async def generate(self, prompt, **kwargs) -> AIResponse:
        """非流式生成"""

    @abstractmethod
    async def generate_stream(self, prompt, **kwargs) -> AsyncIterator[str]:
        """流式生成"""

    async def generate_with_retry(self, prompt, **kwargs):
        """带重试的生成"""
        # 指数退避算法
        for attempt in range(max_retries):
            try:
                return await self.generate(prompt, **kwargs)
            except RateLimitError:
                delay = retry_delay * (2 ** attempt)
                await asyncio.sleep(delay)
```

**设计模式**：
- **适配器模式**：统一不同AI服务接口
- **工厂模式**：create_xxx_adapter() 工厂函数
- **策略模式**：重试策略、降级策略可配置

#### Layer 3: 标准数据协议层

**职责**：
- 定义统一的 JSON Schema
- 验证数据完整性和引用完整性
- 序列化/反序列化

**关键组件**：

```python
# 协议验证器
class ProtocolValidator:
    def validate_complete(self, data) -> ValidationResult:
        """8步完整验证"""
        # 1. JSON Schema 验证
        # 2. 时间戳格式验证
        # 3. UUID 格式验证
        # 4. 引用完整性验证（10种引用类型）
        # 5. 执行顺序唯一性验证

# 序列化器
class ProtocolSerializer:
    def serialize(self, data, output_path, compress=False):
        """序列化为JSON文件"""

    def update_partial(self, file_path, updates):
        """增量更新JSON"""
```

**设计模式**：
- **构建器模式**：逐步构建复杂数据结构
- **组合模式**：嵌套的节点和边结构
- **验证器模式**：多层验证管道

#### Layer 4: 可视化引擎层

**职责**：
- 渲染交互式代码结构图
- 实现嵌套启动按钮
- 播放多流程联动动画
- 展示单步执行详情

**关键组件**：

```typescript
// Cytoscape.js 主引擎
class CodeStructureGraph {
  renderGraph(analysisData: AnalysisResult): void {
    // 渲染节点和边
  }

  attachLaunchButtons(buttons: LaunchButton[]): void {
    // 附加嵌套启动按钮
  }

  playMultiFlowAnimation(traces: TraceableUnit[]): void {
    // 播放多流程联动动画
  }
}

// D3.js 辅助引擎
class ExecutionTraceVisualizer {
  renderSequenceDiagram(trace: SequenceTrace): void {
    // 渲染时序图
  }

  renderFlowchart(trace: FlowchartTrace): void {
    // 渲染流程图（支持fork/join）
  }
}

// Monaco Editor 单步详情
class StepDetailsViewer {
  showStep(step: ExecutionStep): void {
    // 显示代码 + 变量 + 调用栈
  }
}
```

**设计模式**：
- **观察者模式**：UI组件订阅数据变化
- **命令模式**：播放/暂停/回溯命令
- **状态模式**：动画播放状态管理

---

## 🔄 数据流转

### 完整数据流

```
1. 用户输入
   ├─ 项目路径
   ├─ 目标语言
   └─ 分析选项

2. Prompt 渲染
   ├─ 选择对应语言的模板
   ├─ 填充输入数据
   └─ 生成完整 Prompt

3. AI 分析
   ├─ 通过适配器发送 Prompt
   ├─ AI 执行深度分析
   └─ 返回 JSON 结果

4. 数据验证
   ├─ JSON Schema 验证
   ├─ 引用完整性验证
   └─ 业务规则验证

5. 数据存储
   ├─ 序列化为 JSON 文件
   └─ 可选 gzip 压缩

6. 前端加载
   ├─ 读取 JSON 文件
   ├─ TypeScript 类型验证
   └─ 加载到 Zustand Store

7. 可视化渲染
   ├─ Cytoscape.js 渲染结构图
   ├─ 生成嵌套启动按钮
   └─ D3.js 准备辅助图表

8. 用户交互
   ├─ 点击启动按钮
   ├─ 播放执行动画
   ├─ 查看单步详情
   └─ 切换不同视图
```

### 关键数据结构

#### 项目元数据（Project Metadata）

```typescript
interface ProjectMetadata {
  name: string;                    // 项目名称
  language: string;                // 主要语言
  version: string;                 // 项目版本
  description: string;             // AI生成的项目描述
  framework: string[];             // 使用的框架
  architecture_pattern: string[];  // 架构模式（MVC, 微服务等）
  entry_points: string[];          // 入口文件
  dependencies: string[];          // 依赖列表
  complexity_score: number;        // 复杂度评分 (0-1)
}
```

#### 代码结构（Code Structure）

```typescript
interface CodeNode {
  id: string;                      // UUID v4
  label: string;                   // AI生成的业务名称
  stereotype: "system" | "module" | "class" | "function" | "service" | "component";
  parent: string | null;           // 父节点ID（层级关系）
  file_path: string;               // 文件路径
  line_range: [number, number];    // 行号范围
  metadata: {
    visibility: "public" | "private" | "protected";
    is_async: boolean;
    is_exported: boolean;
    ai_confidence: number;
  };
}

interface CodeEdge {
  id: string;                      // UUID v4
  source: string;                  // 源节点ID
  target: string;                  // 目标节点ID
  relationship: "imports" | "calls" | "extends" | "implements" | "contains" | "depends_on";
  label: string;                   // 边的标签
  weight: number;                  // 权重（调用频率、依赖强度）
}
```

#### 启动按钮（Launch Button）

```typescript
interface LaunchButton {
  id: string;                      // UUID v4
  node_id: string;                // 关联的代码节点
  name: string;                   // AI生成的按钮名称
  description: string;            // 功能描述
  type: "macro" | "micro";        // 大按钮/小按钮
  level: "system" | "module" | "component" | "function";
  icon: string;                   // 图标名称

  // 嵌套关系
  parent_button_id: string | null;
  child_button_ids: string[];

  // 执行关联
  traceable_unit_id: string;      // 关联的执行轨迹ID

  // AI 元数据
  metadata: {
    ai_confidence: number;        // 0-1
    ai_explanation: string;
    estimated_duration: number;   // 毫秒
    requires_input: boolean;
    has_side_effects: boolean;
  };
}
```

#### 执行轨迹（Execution Trace）

```typescript
interface TraceableUnit {
  id: string;                      // UUID v4
  name: string;                   // 场景名称
  type: "i-trace";                // 多流程联动类型
  sub_unit_ids: string[];         // 子单元ID（支持嵌套）
  level: "system" | "module" | "component" | "function";

  traces: Array<FlowchartTrace | SequenceTrace | StepByStepTrace>;
}

// 流程图轨迹
interface FlowchartTrace {
  format: "flowchart";
  data: {
    steps: Array<{
      id: string;
      label: string;
      type: "start" | "end" | "process" | "decision" | "fork" | "join";
    }>;
    connections: Array<{
      id: string;
      source: string;
      target: string;
      type: "control_flow" | "data_flow";
      label: string;
    }>;
  };
}

// 时序图轨迹
interface SequenceTrace {
  format: "sequence";
  data: {
    lifelines: Array<{
      id: string;
      label: string;
      type: "service" | "component" | "thread";
    }>;
    messages: Array<{
      id: string;
      source: string;
      target: string;
      type: "sync" | "async" | "return";
      timestamp: number;         // 相对时间戳
      label: string;
    }>;
  };
}

// 单步执行轨迹
interface StepByStepTrace {
  format: "step-by-step";
  data: {
    steps: Array<{
      id: string;
      order: number;
      file_path: string;
      line_number: number;
      code: string;
      timestamp: string;         // ISO 8601
      execution_order: number;   // 全局唯一序号
      scope_id: string;          // 关联变量作用域
    }>;
    variableScopes: Array<{
      id: string;
      scope_type: "global" | "local" | "closure";
      variables: Array<{
        name: string;
        type: string;
        value: string;
      }>;
      timestamp: string;
      execution_order: number;
    }>;
    callStack: Array<{
      id: string;
      function_name: string;
      module_name: string;
      file_path: string;
      line_number: number;
      depth: number;             // 调用深度
      timestamp: string;
      execution_order: number;
    }>;
  };
}
```

---

## 🎯 关键设计决策

### 决策 1：为什么选择 JSON Schema 而非 Protocol Buffers？

**考虑因素**：
- ✅ **人类可读性**：JSON 易于阅读和调试
- ✅ **前端原生支持**：JavaScript 天然支持 JSON
- ✅ **Schema 验证成熟**：jsonschema 库功能完善
- ✅ **版本演进灵活**：易于扩展和向后兼容
- ❌ **性能较低**：但对于分析结果文件可接受

**结论**：选择 JSON Schema

### 决策 2：为什么前端不需要后端服务器？

**考虑因素**：
- ✅ **降低部署复杂度**：纯静态应用
- ✅ **提高响应速度**：本地加载 JSON 文件
- ✅ **降低运维成本**：无需维护服务器
- ✅ **隐私保护**：分析数据不经过服务器
- ❌ **无法实时分析**：需要先生成 JSON

**结论**：采用纯静态前端 + 本地 JSON 文件方案

### 决策 3：为什么使用 Cytoscape.js 而非 D3.js 作为主引擎？

**对比分析**：

| 特性 | Cytoscape.js | D3.js |
|------|--------------|-------|
| 图形渲染性能 | ⭐⭐⭐⭐⭐ 专门优化 | ⭐⭐⭐ 通用库 |
| 层级布局 | ⭐⭐⭐⭐⭐ 内置多种算法 | ⭐⭐⭐ 需要手动实现 |
| 节点交互 | ⭐⭐⭐⭐⭐ 丰富的事件系统 | ⭐⭐⭐⭐ 灵活但需编码 |
| 动画支持 | ⭐⭐⭐⭐ 内置动画引擎 | ⭐⭐⭐⭐⭐ 最强大 |
| 学习曲线 | ⭐⭐⭐⭐ 较平缓 | ⭐⭐ 较陡峭 |

**结论**：
- **主引擎**：Cytoscape.js（代码结构图 + 多流程动画）
- **辅助引擎**：D3.js（时序图/流程图/变量追踪）

### 决策 4：为什么使用 TypedDict 而非 Pydantic dataclass？

**对比分析**：

```python
# TypedDict（选择方案）
class CodeNode(TypedDict):
    id: str
    label: str
    stereotype: Literal["system", "module", "class"]

# 优点：
# - 纯类型提示，零运行时开销
# - 与 JSON 数据结构完美对应
# - mypy 类型检查支持

# Pydantic（未选择）
class CodeNode(BaseModel):
    id: str
    label: str
    stereotype: Literal["system", "module", "class"]

# 缺点：
# - 运行时验证有性能开销
# - 对象实例化成本高
# - 不如 jsonschema 验证灵活
```

**结论**：TypedDict + jsonschema 验证

### 决策 5：为什么 Prompt 模板使用 Jinja2 而非 Python f-string？

**考虑因素**：
- ✅ **逻辑与数据分离**：模板是独立文件
- ✅ **版本管理**：YAML 文件易于版本控制
- ✅ **条件和循环**：Jinja2 支持复杂逻辑
- ✅ **自定义过滤器**：扩展性强
- ✅ **多语言支持**：一份模板支持多种场景

**结论**：Jinja2 模板引擎

---

## 🔧 技术选型理由

### 后端技术栈

#### Python 3.11+
**理由**：
- 类型提示成熟（TypedDict, Literal, NotRequired）
- 异步编程支持完善（asyncio）
- AI SDK 生态丰富
- 数据处理库强大

#### Jinja2
**理由**：
- Django/Flask 同款模板引擎，成熟稳定
- 语法简洁，学习成本低
- 扩展性强，支持自定义过滤器
- 性能优秀

#### jsonschema
**理由**：
- JSON Schema 标准实现
- 验证规则表达力强
- 错误提示详细
- 社区活跃

#### Anthropic SDK
**理由**：
- Claude 4.5 推理能力强
- 长上下文支持（200K tokens）
- API 稳定可靠
- 文档完善

### 前端技术栈

#### React 18
**理由**：
- 并发渲染（Concurrent Rendering）
- 自动批处理（Automatic Batching）
- Suspense 支持
- 生态成熟

#### TypeScript 5.x
**理由**：
- 类型安全
- IDE 支持完善
- 重构友好
- 与后端 TypedDict 对应

#### Zustand
**理由**：
- 轻量级（~1KB）
- 无需 Provider 包裹
- 支持中间件
- TypeScript 支持好

#### Cytoscape.js
**理由**：
- 图形渲染性能最优
- 层级布局算法丰富
- 交互事件系统完善
- 活跃社区支持

#### D3.js
**理由**：
- 数据可视化标准
- 动画能力最强
- 自定义能力最高
- 大量示例

#### Monaco Editor
**理由**：
- VS Code 同款编辑器
- 代码高亮最准确
- 支持所有主流语言
- 性能优秀

#### Vite
**理由**：
- 开发模式极快
- 生产构建优化
- 插件生态完善
- TypeScript 原生支持

---

## 🚀 扩展性设计

### 1. 新语言支持

**扩展步骤**：
1. 在 `backend/prompts/<language>/` 创建目录
2. 为 5 个阶段创建 Prompt 模板
3. 在 `registry.yaml` 注册模板
4. 测试并优化模板

**零代码改动**：架构天然支持新语言

### 2. 新 AI 适配器

**扩展步骤**：
1. 继承 `BaseAIAdapter`
2. 实现 4 个抽象方法：
   - `generate()`
   - `generate_stream()`
   - `validate_connection()`
   - `get_model_info()`
3. 创建工厂函数 `create_xxx_adapter()`

**示例**：

```python
class DeepSeekAdapter(BaseAIAdapter):
    async def generate(self, prompt, **kwargs) -> AIResponse:
        # DeepSeek API 调用逻辑
        pass
```

### 3. 数据协议演进

**版本管理策略**：
- 采用语义化版本（Semantic Versioning）
- v1.x.x → 向后兼容的扩展
- v2.x.x → 不兼容的重大变更

**扩展机制**：
- 使用 `$schema` 字段标识版本
- 旧版本数据自动迁移到新版本
- 验证器支持多版本并存

### 4. 新可视化视图

**扩展步骤**：
1. 在 `frontend/src/components/` 创建新组件
2. 从 `analysisStore` 读取数据
3. 使用 D3.js 或其他库渲染
4. 在主界面添加切换按钮

**示例视图**：
- 依赖关系矩阵
- 复杂度热力图
- 调用链瀑布图
- 性能瓶颈火焰图

---

## ⚡ 性能优化策略

### 1. Prompt 模板缓存

```python
class PromptTemplateManager:
    def __init__(self):
        self._cache: Dict[str, PromptTemplate] = {}

    def load_template(self, language, stage, version=None):
        cache_key = f"{language}:{stage}:{version or 'latest'}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        # 加载模板
        template = self._load_from_file(...)
        self._cache[cache_key] = template
        return template
```

### 2. AI 适配器连接池

```python
class ClaudeAdapter(BaseAIAdapter):
    def __init__(self):
        self.client = AsyncAnthropic(
            max_retries=3,
            timeout=60.0,
            connection_pool_maxsize=10  # 连接池
        )
```

### 3. 前端虚拟化渲染

**大规模节点渲染优化**：

```typescript
// Cytoscape.js 视口剔除
const cy = cytoscape({
  container: document.getElementById('cy'),
  renderer: {
    hideEdgesOnViewport: true,  // 视口外隐藏边
    hideLabelsOnViewport: true, // 视口外隐藏标签
    textureOnViewport: true     // 纹理优化
  }
});
```

### 4. JSON 压缩存储

```python
class ProtocolSerializer:
    def serialize(self, data, output_path, compress=True):
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        if compress:
            # gzip 压缩，减少 70% 文件大小
            with gzip.open(f"{output_path}.gz", 'wt') as f:
                f.write(json_str)
        else:
            with open(output_path, 'w') as f:
                f.write(json_str)
```

### 5. 动画性能优化

**帧率控制**：

```typescript
class AnimationController {
  private fps = 60;
  private frameInterval = 1000 / this.fps;
  private lastFrameTime = 0;

  animate(timestamp: number) {
    if (timestamp - this.lastFrameTime < this.frameInterval) {
      requestAnimationFrame(this.animate.bind(this));
      return;
    }

    // 执行动画逻辑
    this.updateFrame();

    this.lastFrameTime = timestamp;
    requestAnimationFrame(this.animate.bind(this));
  }
}
```

### 6. Web Worker 异步处理

**大数据处理优化**：

```typescript
// 在 Web Worker 中解析和验证 JSON
const worker = new Worker('json-parser-worker.js');

worker.postMessage({ jsonData: largeJsonString });

worker.onmessage = (event) => {
  const parsedData: AnalysisResult = event.data;
  // 更新 UI
};
```

---

## 📖 参考资料

- [JSON Schema Specification](https://json-schema.org/)
- [Cytoscape.js Documentation](https://js.cytoscape.org/)
- [D3.js Documentation](https://d3js.org/)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

---

**文档版本**: v1.0.0
**最后更新**: 2025-01-12
**维护者**: AIFlow Team
