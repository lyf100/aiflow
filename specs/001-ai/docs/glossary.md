# 术语表 (Glossary)

**版本**: 1.0.0
**最后更新**: 2025-10-10
**目的**: 定义 AI 分析指挥与可视化平台中使用的所有关键术语和概念

---

## A

### AI Adapter (AI 适配器)
**定义**: 连接不同 AI 工具与平台的插件式接口实现,负责将平台的标准化分析请求转换为特定 AI 工具的调用格式,并将返回结果转换为平台的标准数据协议格式。

**相关组件**: Adapter Layer, AI Scheduling Engine
**技术实现**: Python Protocol + TypedDict
**示例**: `claude-code-adapter`, `cursor-adapter`, `openai-adapter`

### AI Scheduling Engine (AI 调度引擎)
**定义**: 负责协调和管理 5 个分析阶段的执行顺序、并行化策略、重试机制和结果聚合的核心组件。

**核心功能**:
- 阶段依赖管理 (串行执行保证)
- 阶段内并行化 (提升性能)
- 断点续传支持
- 结果验证和聚合

**相关文档**: `architecture.md`, `api-contracts.md`

### Analysis Result (分析结果)
**定义**: AI 分析完成后返回的标准化数据结构,包含代码结构、执行轨迹、并发信息和行为元数据等完整信息。

**数据格式**: JSON (符合 `analysis-schema-v1.0.0.json`)
**主要字段**: `metadata`, `data.code_structure`, `data.execution_trace`, `data.concurrency_info`

### Animation Control (动画控制)
**定义**: 用户界面中用于控制执行轨迹动画播放的组件,支持播放、暂停、步进、速度调节等功能。

**技术实现**: React 组件 + Canvas + requestAnimationFrame
**性能目标**: ≥30 FPS (5 并发流)

---

## B

### Behavior Metadata (行为元数据)
**定义**: 描述代码执行行为的附加信息,包括启动按钮配置、入口点标识、可交互节点等,用于支持行为驱动的可视化交互。

**关键字段**:
- `launch_buttons`: 启动按钮配置数组
- `entry_points`: 入口点节点 ID 列表
- `interactive_nodes`: 可交互节点 ID 列表

**用途**: 支持用户点击启动按钮触发不同执行流程的可视化

### Behavioral Sandbox (行为沙盒)
**定义**: 主可视化界面的核心区域,使用 Cytoscape.js 渲染分层代码结构图,支持层级导航和行为驱动交互。

**技术栈**: Cytoscape.js (图形渲染) + Compound Nodes (嵌套支持)
**交互模式**: 点击节点 → 下钻层级 → 查看细节 → 触发动画

---

## C

### Cache Strategy (缓存策略)
**定义**: 用于提升平台性能的多层缓存机制,包括分析结果缓存、Prompt 模板缓存和 AI 响应缓存。

**缓存层级**:
- **L1 - Memory Cache**: 内存缓存 (最快访问)
- **L2 - File System Cache**: 文件系统缓存 (持久化)
- **L3 - Database Cache**: SQLite 缓存 (索引查询)

**淘汰策略**: LRU (Least Recently Used)
**目标命中率**: ≥70%

### Code Structure (代码结构)
**定义**: 分析结果中描述代码静态结构的部分,包含节点 (nodes) 和边 (edges) 的图形数据。

**核心实体**:
- **Nodes**: 代码元素 (项目、模块、类、函数等)
- **Edges**: 代码关系 (调用、继承、引用等)

**可视化**: Cytoscape.js 分层图 (hierarchical layout)

### Compound Node (复合节点)
**定义**: Cytoscape.js 中支持嵌套子节点的节点类型,用于表示包含关系 (如 Package → Module → Class → Function)。

**层级结构**:
```
Project (L1)
└── Package (L2)
    └── Module (L3)
        └── Class (L4)
            └── Function (L5)
```

### Concurrency Detection (并发检测)
**定义**: AI 分析的第 5 阶段,负责识别代码中的并发模式、同步点和潜在的竞态条件。

**检测内容**:
- 并发流 (Concurrent Flows): 并行执行的代码路径
- 同步点 (Sync Points): 线程/协程同步位置
- 资源共享 (Shared Resources): 多线程访问的共享数据

**置信度阈值**: 最低 0.60 (警告级别) | 推荐 0.80

### Confidence Score (置信度分数)
**定义**: AI 分析结果中表示 AI 对其推断准确性的自信程度的数值,范围 0.0-1.0。

**类型**:
- **Stage Confidence**: 阶段级置信度 (整体分析质量)
- **Entity Confidence**: 实体级置信度 (单个节点/边的准确性)

**验证规则**: 见 `confidence-schema.yaml` 和 `api-contracts.md` Section 8.5

### Cytoscape.js
**定义**: 开源 JavaScript 图形可视化库,用于渲染平台的主行为沙盒 (分层代码结构图)。

**选择理由**:
- 优秀的大图性能 (5000+ 节点)
- Compound nodes 支持 (嵌套层级)
- 丰富的布局算法 (hierarchical, dagre)

**官方文档**: https://js.cytoscape.org/

---

## D

### D3.js
**定义**: 数据驱动文档 (Data-Driven Documents) JavaScript 库,用于渲染平台的详情分析视图 (流程图、序列图)。

**用途**:
- Flowchart Renderer (流程图渲染器)
- Sequence Diagram Renderer (序列图渲染器)
- Custom animations (自定义动画)

**官方文档**: https://d3js.org/

### Data Protocol (数据协议)
**定义**: 平台定义的标准化 JSON 数据格式,用于 AI Adapter 和可视化引擎之间的数据交换。

**核心文件**: `shared/schemas/analysis-schema-v1.0.0.json`
**版本策略**: 语义化版本 (Semantic Versioning)
**向后兼容**: ≥2 MAJOR 版本

### Detail View (详情视图)
**定义**: 用户选择特定执行轨迹后展示的详细分析界面,包含流程图、序列图和步进详情三个子视图。

**子组件**:
- **Flowchart View**: 流程图视图 (控制流)
- **Sequence View**: 序列图视图 (时序交互)
- **Step Detail View**: 步进详情视图 (逐步执行)

**渲染引擎**: D3.js (flowchart/sequence) + Monaco Editor (step detail)

---

## E

### Edge (边)
**定义**: 代码结构图中表示两个节点之间关系的连接线,如函数调用、类继承、模块引用等。

**关键属性**:
- `id`: 唯一标识符
- `source`: 源节点 ID
- `target`: 目标节点 ID
- `edge_type`: 边类型 (calls, inherits, imports 等)
- `metadata`: 附加元数据 (调用次数、参数等)

**可视化**: Cytoscape.js 有向边 (directed edge)

### Entry Point (入口点)
**定义**: 代码执行的起始位置,通常是 `main()` 函数、HTTP 路由处理器或事件监听器等。

**标识方式**: 在 `behavior_metadata.entry_points` 数组中列出节点 ID
**视觉标记**: 特殊图标或颜色高亮
**交互**: 可作为启动按钮的执行起点

### Execution Inference (执行推断)
**定义**: AI 分析的第 4 阶段,负责推断代码的动态执行轨迹,包括控制流、数据流和函数调用序列。

**输出格式**:
- **Flowchart**: 流程图 (控制流分支)
- **Sequence**: 序列图 (对象交互时序)
- **Step-by-Step**: 逐步执行 (单步详情)

**置信度阈值**: 最低 0.60 (警告级别) | 推荐 0.80

### Execution Order (执行顺序)
**定义**: 执行轨迹中每个步骤的全局唯一递增整数,用于标识步骤的时序关系。

**约束规则**:
- 全局唯一性 (同一分析结果中不重复)
- 单调递增性 (后续步骤 > 前序步骤)
- 连续性建议 (相邻步骤差值较小,允许跳跃)

**验证**: `api-contracts.md` Section 8.3

### Execution Trace (执行轨迹)
**定义**: 描述代码动态执行路径的可追溯单元,包含流程图、序列图和步进详情三种格式。

**数据结构**:
```json
{
  "trace_id": "unique-id",
  "trace_name": "用户登录流程",
  "trigger_condition": "用户点击登录按钮",
  "flowchart": { ... },
  "sequence": { ... },
  "step_by_step": { ... }
}
```

**用途**: 支持动画播放和交互式探索

---

## F

### Flowchart (流程图)
**定义**: 执行轨迹的控制流可视化形式,展示条件分支、循环和并发 Fork/Join 模式。

**节点类型**:
- `start`: 开始节点
- `end`: 结束节点
- `process`: 处理步骤
- `decision`: 条件分支
- `loop_start`: 循环开始
- `loop_end`: 循环结束
- `fork`: 并发分叉
- `join`: 并发汇合

**渲染引擎**: D3.js

### Fork/Join Pattern (Fork/Join 模式)
**定义**: 并发编程中的经典模式,表示执行流分叉为多个并行分支,最后在汇合点同步。

**可视化**:
- **Fork 节点**: 菱形,标注 "Fork N branches"
- **Join 节点**: 菱形,标注 "Join N branches"
- **并发分支**: 并行的执行路径

**示例场景**: 并行 HTTP 请求、MapReduce、并行任务处理

---

## G

### Graceful Degradation (优雅降级)
**定义**: 当系统资源不足或服务不可用时,逐步降低功能复杂度以保持核心可用性的策略。

**5 级降级策略**:
1. **Full Mode**: 完整 AI 分析 + 完整可视化
2. **Partial Mode**: 简化 AI 分析 + 完整可视化
3. **Cache Mode**: 使用缓存结果 + 完整可视化
4. **Static Mode**: 无 AI 分析 + 静态可视化
5. **Offline Mode**: 离线预生成结果 + 静态可视化

**触发条件**: AI 服务超时、内存不足、网络故障等

---

## H

### Hierarchical Layout (分层布局)
**定义**: Cytoscape.js 的图形布局算法之一,将节点按层级关系垂直或水平排列,适用于代码结构的可视化。

**优点**:
- 清晰展示层级关系 (Package → Module → Class → Function)
- 减少边交叉
- 支持大规模图形 (1000+ 节点)

**配置示例**:
```javascript
{
  name: 'dagre',
  rankDir: 'TB', // Top to Bottom
  nodeSep: 50,
  rankSep: 100
}
```

---

## I

### Incremental Analysis (增量分析)
**定义**: 当代码发生变更时,仅重新分析修改的文件及其依赖链,而非完整重新分析整个项目的优化策略。

**优势**:
- 大幅减少分析时间 (10-100x 加速)
- 降低 AI API 成本
- 提升开发体验

**实现方式**:
- Git diff 检测变更文件
- 依赖图分析影响范围
- 缓存未变更部分的分析结果

### Interactive Node (可交互节点)
**定义**: 代码结构图中可响应用户点击、悬停等交互行为的节点,通常包含启动按钮或详情链接。

**交互行为**:
- **Click**: 下钻到子层级 / 触发执行动画
- **Hover**: 显示 Tooltip (函数签名、注释等)
- **Right-click**: 显示上下文菜单 (查看源码、复制路径等)

**标识**: `behavior_metadata.interactive_nodes` 数组

---

## J

### Jinja2
**定义**: Python 模板引擎,用于 Prompt Library 的 YAML 模板渲染,支持变量替换、条件判断和循环控制。

**使用场景**: 根据项目类型、语言、框架动态生成 AI 分析的 Prompt
**示例**:
```jinja2
分析以下 {{ language }} 项目的 {{ analysis_stage }} 阶段:
{% if framework %}
框架: {{ framework }}
{% endif %}
```

### JSON Schema
**定义**: 用于定义和验证 JSON 数据结构的规范,平台使用 JSON Schema Draft 7 定义分析结果的标准格式。

**核心文件**: `shared/schemas/analysis-schema-v1.0.0.json`
**验证库**: Python `jsonschema`, JavaScript `ajv`
**用途**: 确保 AI Adapter 返回数据的完整性和一致性

---

## L

### Launch Button (启动按钮)
**定义**: 行为沙盒中的可点击按钮,用于触发特定执行轨迹的动画播放,支持宏观流程和微观细节两种模式。

**配置字段**:
- `button_id`: 按钮唯一标识
- `label`: 按钮文本 (如 "启动登录流程")
- `trace_id`: 关联的执行轨迹 ID
- `icon`: 按钮图标
- `color`: 按钮颜色

**嵌套支持**: 宏观启动按钮 → 微观启动按钮 (多层嵌套)

### Level of Detail (LOD, 细节层级)
**定义**: 根据用户当前浏览的层级自动调整可视化细节粒度的性能优化技术。

**示例**:
- **L1 (Project)**: 仅显示 Package 级节点
- **L2 (Package)**: 显示 Module 级节点
- **L3 (Module)**: 显示 Class 级节点
- **L4 (Class)**: 显示 Function 级节点
- **L5 (Function)**: 显示完整代码细节

**性能收益**: 减少 60-80% 渲染负载

### LRU Cache (最近最少使用缓存)
**定义**: 缓存淘汰策略,当缓存满时优先移除最久未使用的条目,确保热点数据保留在缓存中。

**应用场景**: 分析结果缓存、Prompt 模板缓存
**实现**: Python `functools.lru_cache`, JavaScript `lru-cache` 库

---

## M

### Monaco Editor
**定义**: Visual Studio Code 的代码编辑器内核,用于步进详情视图的代码展示和调试器风格交互。

**功能**:
- 语法高亮 (多语言支持)
- 行号显示 + 断点标记
- 变量悬停提示 (Hover tooltips)
- 只读模式 (禁止编辑)

**官方文档**: https://microsoft.github.io/monaco-editor/

### Metadata (元数据)
**定义**: 描述分析结果整体信息的顶层字段,包含项目信息、分析配置、时间戳等。

**关键字段**:
- `project_name`: 项目名称
- `project_path`: 项目路径
- `language`: 编程语言
- `framework`: 使用的框架
- `analysis_timestamp`: 分析时间戳 (ISO 8601)
- `ai_adapter`: 使用的 AI 适配器
- `schema_version`: 数据协议版本

---

## N

### Node (节点)
**定义**: 代码结构图中的基本单元,代表代码元素如项目、包、模块、类、函数等。

**核心属性**:
- `id`: 唯一标识符
- `label`: 显示名称
- `node_type`: 节点类型 (project, package, module, class, function 等)
- `parent_id`: 父节点 ID (用于嵌套)
- `metadata`: 附加元数据 (源码位置、注释、参数等)

**可视化**: Cytoscape.js 节点 (支持 compound nodes)

---

## P

### Performance Budget (性能预算)
**定义**: 为平台各项性能指标设定的明确上限,用于指导优化工作和自动化性能测试。

**关键指标**:
- **首次渲染时间**: 小项目 <1s, 中项目 <3s, 大项目 <8s
- **层级切换时间**: 小项目 <150ms, 中项目 <300ms, 大项目 <500ms
- **动画帧率**: ≥30 FPS (5 并发流)
- **内存占用**: 中项目 ≤500MB, 大项目 ≤1GB
- **API 响应**: P95 <500ms

**参考文档**: `docs/performance-testing-guide.md`

### Prompt Library (核心指令集)
**定义**: 平台维护的 YAML 格式 Prompt 模板库,用于生成发送给 AI 工具的分析指令。

**组织方式**:
- 按语言分类 (Python, JavaScript, Java 等)
- 按分析阶段分类 (5 个阶段)
- 语义化版本控制 (如 `python-structure-v1.1.0.yaml`)

**模板引擎**: Jinja2
**存储**: Git LFS (大文件版本控制)

### Project Understanding (项目理解)
**定义**: AI 分析的第 1 阶段,负责识别项目类型、编程语言、框架和整体架构风格。

**分析内容**:
- 语言检测 (基于文件扩展名和语法)
- 框架识别 (基于依赖文件如 package.json, requirements.txt)
- 项目类型 (Web 应用、CLI 工具、库等)
- 目录结构模式

**置信度阈值**: 最低 0.70 (错误级别) | 推荐 0.85
**预计耗时**: 30-60 秒

---

## R

### Recursion Depth (递归深度)
**定义**: 函数递归调用的嵌套层数,用于检测和可视化递归模式。

**验证规则**:
- `is_recursive = true` 时,`recursion_depth` 必须 ≥ 1
- `is_recursive = false` 时,`recursion_depth` 必须 = 0 或 null

**可视化**: 调用栈视图中的缩进层级

### Resume Support (断点续传)
**定义**: AI 分析过程中如因超时、错误等中断,支持从上次成功阶段继续执行,无需重新开始。

**实现机制**:
- 每个阶段完成后持久化中间结果
- 记录当前阶段状态 (pending, in_progress, completed, failed)
- 重启时跳过已完成阶段

**状态存储**: SQLite + 文件系统

---

## S

### Semantic Analysis (语义分析)
**定义**: AI 分析的第 3 阶段,负责理解代码的业务含义,提取函数/类的功能描述和命名语义。

**分析内容**:
- 函数功能描述 (基于命名、注释、实现)
- 业务领域术语提取
- 参数和返回值的语义含义
- 代码意图推断

**置信度阈值**: 最低 0.70 (错误级别) | 推荐 0.85
**预计耗时**: 1-40 分钟

### Sequence Diagram (序列图)
**定义**: 执行轨迹的时序交互可视化形式,展示对象/模块之间的消息传递顺序。

**核心元素**:
- **Participants**: 参与对象 (类、模块、外部服务等)
- **Messages**: 消息传递 (同步调用、异步消息、返回值等)
- **Lifelines**: 生命线 (对象存在时间)
- **Activation Boxes**: 激活框 (方法执行期间)

**渲染引擎**: D3.js
**标准参考**: UML 序列图规范

### Stack Frame (栈帧)
**定义**: 函数调用栈中的单个帧,包含函数上下文、局部变量和调用信息。

**关键字段**:
- `frame_id`: 栈帧唯一标识
- `function_name`: 函数名称
- `file_path`: 源文件路径
- `line_number`: 调用行号
- `local_variables`: 局部变量快照
- `parent_frame_id`: 调用者栈帧 ID

**用途**: 步进详情视图的调用栈展示

### Step-by-Step Execution (逐步执行)
**定义**: 执行轨迹的最细粒度可视化形式,模拟调试器的单步执行,展示每一步的代码、变量和调用栈状态。

**关键数据**:
- `steps`: 执行步骤数组
- 每个步骤包含: `execution_order`, `code_snippet`, `variable_snapshot`, `call_stack`

**可视化**: Monaco Editor + 调试器 UI 风格

### Structure Recognition (结构识别)
**定义**: AI 分析的第 2 阶段,负责提取代码的静态结构,包括模块、类、函数的定义和关系。

**提取内容**:
- 模块/包结构
- 类定义和继承关系
- 函数/方法签名
- 导入/引用关系

**置信度阈值**: 最低 0.80 (错误级别) | 推荐 0.90
**预计耗时**: 1-30 分钟

### Sync Point (同步点)
**定义**: 并发执行中多个线程/协程汇合和同步的位置,如 Join、Barrier、Lock 等。

**类型**:
- `join`: Fork/Join 模式的汇合点
- `barrier`: 屏障同步 (等待所有线程到达)
- `lock_acquire`: 锁获取
- `lock_release`: 锁释放

**可视化**: 序列图中的垂直同步线

---

## T

### Trace Format (轨迹格式)
**定义**: 执行轨迹的三种标准化数据格式,对应三种可视化视图。

**三种格式**:
1. **Flowchart Format**: 流程图格式 (控制流节点和边)
2. **Sequence Format**: 序列图格式 (参与者和消息)
3. **Step-by-Step Format**: 步进格式 (执行步骤数组)

**Schema 定义**: `analysis-schema-v1.0.0.json` 中的 `execution_trace` 部分

---

## V

### Variable Scope (变量作用域)
**定义**: 变量在代码中的可见性范围,用于步进详情视图的变量追踪。

**作用域类型**:
- `global`: 全局作用域
- `module`: 模块作用域
- `class`: 类作用域
- `function`: 函数作用域
- `block`: 块作用域 (如 if/for 内部)

**关键字段**: `scope_id`, `scope_type`, `variables` (变量列表)

### Validation Level (验证级别)
**定义**: 数据验证规则的执行严格程度,决定验证失败时的处理策略。

**两种级别**:
- **error**: 错误级别 (验证失败则拒绝数据)
- **warning**: 警告级别 (验证失败仅记录日志,不阻塞)

**应用场景**: 置信度阈值验证、数据完整性检查

### Virtualization (虚拟化渲染)
**定义**: 仅渲染视口内可见的节点和边,动态加载/卸载视口外元素的性能优化技术。

**触发条件**: 节点数 > 1000
**性能收益**: 减少 70-90% DOM 元素,大幅提升帧率
**实现**: React Virtualized / 自定义 Canvas 虚拟化

---

## W

### WebSocket
**定义**: 用于前后端实时双向通信的协议,平台使用 WebSocket 传输 AI 分析的进度更新和结果流式返回。

**应用场景**:
- 实时推送分析进度 (1-5 阶段状态)
- 流式返回分析结果 (边分析边展示)
- 动画同步 (多用户协同观看)

**性能要求**: 延迟 <50ms | 并发连接 ≥100

---

## Z

### Zustand
**定义**: 轻量级 React 状态管理库,用于管理前端全局状态 (分析结果、UI 配置、动画状态等)。

**选择理由**:
- API 简洁 (相比 Redux)
- 性能优秀 (选择性订阅)
- TypeScript 友好
- 无样板代码

**官方文档**: https://zustand-demo.pmnd.rs/

---

## 缩写词表 (Abbreviations)

| 缩写 | 全称 | 中文 |
|------|------|------|
| AI | Artificial Intelligence | 人工智能 |
| API | Application Programming Interface | 应用程序接口 |
| AST | Abstract Syntax Tree | 抽象语法树 |
| CLI | Command Line Interface | 命令行接口 |
| DOM | Document Object Model | 文档对象模型 |
| E2E | End-to-End | 端到端 |
| FPS | Frames Per Second | 每秒帧数 |
| HTTP | HyperText Transfer Protocol | 超文本传输协议 |
| IDE | Integrated Development Environment | 集成开发环境 |
| JSON | JavaScript Object Notation | JavaScript 对象表示法 |
| LOD | Level of Detail | 细节层级 |
| LRU | Least Recently Used | 最近最少使用 |
| P50/P95/P99 | Percentile (50th/95th/99th) | 百分位数 (50/95/99) |
| REST | Representational State Transfer | 表现层状态转换 |
| SPA | Single Page Application | 单页应用 |
| UI | User Interface | 用户界面 |
| UML | Unified Modeling Language | 统一建模语言 |
| UX | User Experience | 用户体验 |
| YAML | YAML Ain't Markup Language | YAML 不是标记语言 |

---

## 相关文档 (Related Documentation)

- **Architecture**: `/specs/001-ai/architecture.md`
- **Data Model**: `/specs/001-ai/data-model.md`
- **API Contracts**: `/specs/001-ai/contracts/api-contracts.md`
- **JSON Schema**: `/specs/001-ai/contracts/analysis-schema-v1.0.0.json`
- **Confidence Schema**: `/specs/001-ai/prompts/confidence-schema.yaml`
- **Performance Testing**: `/specs/001-ai/docs/performance-testing-guide.md`
- **Quick Start**: `/specs/001-ai/quickstart.md`
- **Tasks**: `/specs/001-ai/tasks.md`
- **Specification**: `/specs/001-ai/spec.md`

---

**版本历史**:
- **v1.0.0** (2025-10-10): 初始术语表,涵盖所有核心概念和关键术语
