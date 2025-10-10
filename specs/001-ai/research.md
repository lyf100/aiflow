# Research: AI分析指挥与可视化平台 - 技术决策

**Feature**: 001-ai | **Date**: 2025-10-09 | **Phase**: 0 - Research

## Executive Summary

本研究为"AI分析指挥与可视化平台"确立了三大核心组件的技术栈选型和关键未知问题的解决方案。核心架构采用"无外壳"MCP Tool设计，包含：**核心指令集 (Prompt Library)**、**AI适配器层 (Adapter Layer)** 和 **可视化引擎 (Visualization Engine)**。

## 1. 核心指令集 (Prompt Library) - 技术决策

### 1.1 Prompt 模板管理技术选型

**决策**：使用 **YAML + Jinja2** 作为 Prompt 模板引擎

**理由**：
- YAML 提供人类可读的层级结构，便于版本控制和团队协作
- Jinja2 提供强大的模板继承、变量替换、条件分支能力
- 支持模板片段复用（include/extend），减少重复
- 易于实现热加载和版本化管理

**替代方案拒绝**：
- JSON：缺乏注释能力，模板复用困难
- 纯文本：缺乏结构化验证，难以管理变量和条件逻辑
- LangChain PromptTemplate：引入重依赖，过度工程化

### 1.2 Prompt 版本化策略

**决策**：采用 **语义化版本 + Git LFS** 管理

**版本格式**：`{language}-{stage}-v{major}.{minor}.{patch}.yaml`
- 示例：`python-structure-analysis-v1.2.0.yaml`
- `language`：目标语言（python, javascript, java, go, rust）
- `stage`：分析阶段（structure-analysis, semantic-analysis, execution-inference, concurrency-detection）
- `version`：语义化版本

**存储结构**：
```
prompts/
├── registry.yaml              # Prompt 索引和元数据
├── python/
│   ├── structure-analysis/
│   │   ├── v1.0.0.yaml
│   │   ├── v1.1.0.yaml (current)
│   │   └── v2.0.0-beta.yaml
│   ├── semantic-analysis/
│   ├── execution-inference/
│   └── concurrency-detection/
├── javascript/
└── common/
    └── shared-fragments.yaml  # 共享模板片段
```

**热加载机制**：使用 Watchdog 监控文件变化，自动重新加载模板

### 1.3 Prompt 质量保证策略

**决策**：建立 **3 层验证机制**

**Layer 1 - 格式验证**：
- JSON Schema 验证 Prompt YAML 结构完整性
- 必需字段：`id`, `version`, `stage`, `target_language`, `input_schema`, `output_schema`, `quality_criteria`

**Layer 2 - 效果验证**（自动化测试）：
- 准备标准测试代码集（5-10 个典型项目）
- 每个 Prompt 版本必须通过所有测试用例
- 关键指标：准确率 ≥85%，一致性 ≥95%（重复执行结果相同）

**Layer 3 - 人工审核**（新版本发布前）：
- 至少 2 名技术负责人审核 Prompt 质量
- 验证业务语义准确性和用户友好度

### 1.4 AI 调度策略

**决策**：采用 **分阶段串行 + 同级并行** 的混合调度策略

**分析阶段设计**（串行依赖关系）：

**阶段 1 - 项目认知 (Project Understanding)**
- 输入：项目目录结构、README、配置文件
- 输出：项目类型、主要技术栈、架构模式、业务领域推断
- 耗时：30-60 秒

**阶段 2 - 静态结构识别 (Structure Recognition)**
- 输入：所有源代码文件、阶段 1 输出
- 输出：模块列表、类/函数定义、依赖关系图
- 策略：可并行分析多个模块（按目录或文件分组）
- 耗时：小型 1-2 分钟，中型 5-10 分钟，大型 15-30 分钟

**阶段 3 - 功能语义分析 (Semantic Analysis)**
- 输入：结构识别结果、关键代码片段、阶段 1 上下文
- 输出：每个模块/函数的业务语义命名、功能描述、启动按钮名称
- 策略：可并行分析各模块的语义
- 耗时：小型 1-2 分钟，中型 5-10 分钟，大型 20-40 分钟

**阶段 4 - 执行流程推理 (Execution Inference)**
- 输入：结构 + 语义结果，函数调用图
- 输出：execution_trace 数据（流程图、时序图、变量作用域、递归调用）
- 策略：为每个"可执行单元"（Traceable Unit）生成 traces
- 耗时：小型 1-2 分钟，中型 5-15 分钟，大型 20-50 分钟

**阶段 5 - 并发模式识别 (Concurrency Detection)**
- 输入：执行流程结果，并发关键词检测（thread, async, await, Promise, goroutine）
- 输出：concurrency_info（并发流、同步点、Fork/Join、依赖关系）
- 策略：仅对包含并发的代码单元进行深度分析
- 耗时：小型 30-60 秒，中型 2-5 分钟，大型 10-20 分钟

**调度优化策略**：
- **智能范围限定**：阶段 2-5 可基于项目规模动态限定分析范围（核心模块优先，边缘模块按需）
- **缓存复用**：阶段 1-3 结果缓存，代码未变更时直接跳过
- **增量分析**：代码变更时，仅重新分析受影响模块和依赖链
- **并行调度**：阶段 2-5 内部可对独立模块并行调用 AI

**预期总耗时**（首次完整分析）：
- 小型项目 (<1000 LOC)：2-5 分钟
- 中型项目 (1000-5000 LOC)：10-20 分钟
- 大型项目 (5000-20000 LOC)：30-60 分钟
- 超大项目 (>20000 LOC)：1-3 小时（支持断点续传）

## 2. AI适配器层 (Adapter Layer) - 技术决策

### 2.1 适配器架构设计

**决策**：采用 **插件化适配器 + 标准化协议** 架构

**核心接口定义**（Python Protocol/TypedDict）：

```python
from typing import Protocol, TypedDict, Literal

class PromptRequest(TypedDict):
    """AI 分析请求标准格式"""
    prompt_id: str              # Prompt 模板 ID
    prompt_version: str         # 版本号
    stage: Literal["structure", "semantic", "execution", "concurrency"]
    input_data: dict           # 输入数据（项目路径、代码片段、上下文）
    context: dict              # 分析上下文（前序结果、项目元数据）
    quality_criteria: dict     # 质量标准

class AnalysisResult(TypedDict):
    """AI 分析结果标准格式"""
    request_id: str
    status: Literal["success", "partial", "failed"]
    data: dict                 # 符合标准数据协议的 JSON
    metadata: dict             # AI 调用元数据（耗时、token 消耗、模型版本）
    confidence: float          # AI 置信度 (0.0-1.0)
    explanation: str           # AI 决策解释

class AIAdapter(Protocol):
    """AI 适配器标准接口"""
    def analyze(self, request: PromptRequest) -> AnalysisResult: ...
    def health_check(self) -> bool: ...
    def get_capabilities(self) -> dict: ...
```

### 2.2 支持的 AI 工具类型

**决策**：优先支持 **4 类 AI 工具**

**类型 1 - IDE 集成 AI 工具**（优先级 P1）
- VS Code Copilot、GitHub Copilot、JetBrains AI Assistant
- 集成方式：通过 IDE 扩展 API 或 Language Server Protocol (LSP)
- 适配器实现：`IDEAdapter`（通用抽象） + 具体实现（`CopilotAdapter`、`JetBrainsAdapter`）

**类型 2 - 命令行 AI 工具**（优先级 P1）
- Claude Code、Cursor、Aider
- 集成方式：通过命令行接口或 Python API
- 适配器实现：`CLIAdapter`（执行子进程，解析 JSON 输出）

**类型 3 - 云端 AI 服务**（优先级 P2）
- OpenAI API (GPT-4/GPT-4 Turbo)、Anthropic Claude API、Google Gemini API
- 集成方式：通过 REST API 或官方 SDK
- 适配器实现：`CloudAPIAdapter`（统一 HTTP 客户端 + 特定格式转换）

**类型 4 - 本地 AI 模型**（优先级 P3）
- Ollama、LM Studio、vLLM
- 集成方式：通过本地 HTTP API 或 Python 绑定
- 适配器实现：`LocalModelAdapter`

**适配器优先级选择策略**：
1. 检测 IDE 环境（VS Code、JetBrains）→ 优先使用 IDE 集成 AI
2. 检测命令行 AI 工具可用性（`which claude`、`which cursor`）→ 使用 CLI 适配器
3. 用户配置云端 API（环境变量或配置文件）→ 使用云端 API
4. 检测本地模型服务（`http://localhost:11434` Ollama）→ 使用本地模型
5. 无可用 AI 工具 → 提示用户配置或使用离线模式

### 2.3 标准化数据协议 (JSON Schema)

**决策**：基于 **JSON Schema v7** 定义严格的数据格式

**版本化策略**：
- 当前版本：`v1.0.0`
- 向后兼容至少 2 个 MAJOR 版本
- 使用 `$schema` 字段标识版本：`"$schema": "https://aiflow.dev/schemas/analysis-v1.0.0.json"`

**核心数据结构**（详细 schema 见 `contracts/analysis-schema-v1.0.0.json`）：

```json
{
  "$schema": "https://aiflow.dev/schemas/analysis-v1.0.0.json",
  "version": "1.0.0",
  "project_metadata": { ... },
  "code_structure": {
    "nodes": [
      {
        "id": "node-001",
        "label": "用户认证模块",
        "parent": "system-001",
        "classes": ["module", "security"],
        "stereotype": "service",
        "metadata": { "ai_confidence": 0.92, "ai_explanation": "..." }
      }
    ],
    "edges": [ ... ]
  },
  "behavior_metadata": {
    "launch_buttons": [
      {
        "id": "btn-001",
        "node_id": "node-001",
        "name": "处理用户登录",
        "description": "验证用户凭据并创建会话",
        "type": "macro"
      }
    ]
  },
  "execution_trace": {
    "traceable_units": [
      {
        "id": "unit-001",
        "name": "处理用户登录",
        "type": "multi-trace",
        "subUnitIds": ["unit-002", "unit-003"],
        "traces": [
          {
            "format": "flowchart",
            "steps": [ ... ],
            "connections": [ ... ]
          },
          {
            "format": "sequence",
            "lifelines": [ ... ],
            "messages": [ ... ]
          },
          {
            "format": "step-by-step",
            "variableScopes": [ ... ],
            "callStack": [ ... ]
          }
        ]
      }
    ]
  },
  "concurrency_info": { ... },
  "prompt_templates": {
    "used_prompts": [
      { "id": "python-structure-v1.1.0", "stage": "structure", "executed_at": "2025-10-09T10:00:00Z" }
    ]
  }
}
```

**格式验证工具**：
- Python：`jsonschema` 库
- 前端：`ajv` (Another JSON Schema Validator)
- CI/CD：自动化 schema 验证测试

### 2.4 适配器错误处理与降级策略

**决策**：采用 **5 级降级策略**

**Level 0 - 完整功能**：
- AI 工具正常响应，数据完整且通过验证
- 所有功能正常可用

**Level 1 - 部分降级**：
- AI 工具超时或返回不完整数据
- 尽力解析可用部分，标注缺失区域
- 提供重新分析选项

**Level 2 - 缓存模式**：
- AI 工具连接失败，但存在历史缓存
- 加载缓存结果，标注"缓存数据"和时间戳
- 提示用户数据可能过时

**Level 3 - 静态分析模式**（未来扩展）：
- 无 AI 工具可用，使用静态分析工具（tree-sitter、AST 解析）生成基础结构
- 仅提供代码结构图，无语义命名和执行追踪
- 明确标注"有限功能模式"

**Level 4 - 离线文件模式**：
- 用户导入预生成的分析结果文件（JSON）
- 完整可视化功能，但无法重新分析
- 适用于无网络环境或演示场景

**错误重试策略**：
- 超时：3 次指数退避重试（初始 5s，最大 60s）
- 格式错误：生成精炼 Prompt 重新请求（最多 2 次）
- 连接失败：切换到备用适配器或降级模式

## 3. 可视化引擎 (Visualization Engine) - 技术决策

### 3.1 混合渲染引擎架构

**决策**：采用 **Cytoscape.js (主沙盘) + D3.js (细节分析) + Monaco Editor (单步详情)** 三层架构

**架构设计**：

**Layer 1 - 行为沙盘主渲染器 (Cytoscape.js)**
- **职责**：渲染层级化代码结构图（主视图）
- **优势**：
  - 专为大型图设计，支持 5000+ 节点的流畅渲染
  - 内置层级布局算法（COSE、dagre、breadthfirst）
  - 原生支持复合节点（compound nodes），完美匹配层级结构需求
  - 丰富的交互能力（缩放、平移、展开/折叠）
- **使用场景**：
  - 系统级 → 模块级 → 函数级的层级结构图
  - 节点展开/折叠交互
  - 启动按钮附加到节点
  - 宏观联动动画（高亮多个节点、流动箭头）

**Layer 2 - 细节分析渲染器 (D3.js)**
- **职责**：渲染流程图、时序图、变量可视化
- **优势**：
  - 极高的灵活性，可定制任意可视化形式
  - 强大的动画能力（transition、interpolate）
  - 适合自定义交互和复杂数据绑定
- **使用场景**：
  - 时序图 (Sequence Diagram)：lifelines + messages
  - 流程图 (Flowchart)：steps + connections + fork/join
  - 变量作用域可视化：嵌套矩形 + 变量列表
  - 并发流可视化：多条时间轴 + 同步点

**Layer 3 - 单步详情视图 (Monaco Editor)**
- **职责**：代码编辑器 + 调试器界面
- **优势**：
  - VS Code 内核，提供专业级代码编辑体验
  - 内置语法高亮、IntelliSense、断点支持
  - 支持多语言（Python, JS, Java, Go, Rust）
  - 可扩展性强（LSP、主题、插件）
- **使用场景**：
  - 显示当前代码行（语法高亮）
  - 设置断点（条件断点、日志断点）
  - 变量面板集成（自定义 UI 组件）
  - 调用栈面板（自定义 UI 组件）

**渲染引擎协调**：
- 主结构图（Cytoscape.js）通过事件总线与 D3.js 和 Monaco Editor 同步
- 用户点击 Cytoscape.js 节点 → 触发 D3.js 渲染对应的流程图/时序图
- 用户点击"钻入详情" → Monaco Editor 打开对应代码文件，定位到行

### 3.2 动画系统设计

**决策**：使用 **Canvas + requestAnimationFrame** 实现高性能动画

**动画引擎架构**：

**核心动画管理器 (AnimationManager)**：
- 管理全局动画状态（播放、暂停、速度、当前时间）
- 调度多个并发动画流（最多 10 个）
- 提供时间回溯能力（记录历史状态快照）

**动画类型实现**：

**类型 1 - 节点高亮动画**：
- Cytoscape.js 原生支持：`node.addClass('active')` + CSS transition
- 性能：≥60 FPS

**类型 2 - 流动箭头动画**：
- Canvas 渲染（overlay layer on top of Cytoscape.js）
- 使用 SVG path + dash-offset 动画技术
- 性能：≥30 FPS（5 个并发流）

**类型 3 - 时序图消息动画**：
- D3.js transition + SVG line animation
- 消息从 source lifeline 移动到 target lifeline
- 性能：≥30 FPS

**类型 4 - 变量值变化动画**：
- Monaco Editor 集成：行号旁边显示变化指示器
- 变量面板使用 React transition 或 Vue transition
- 性能：<150ms 更新延迟

**动画控制 API**：
```typescript
interface AnimationController {
  play(): void;
  pause(): void;
  setSpeed(speed: number): void;  // 0.1x - 10x
  seekTo(time: number): void;     // 时间回溯
  stepForward(): void;            // 单步前进
  stepBackward(): void;           // 单步后退
  setBreakpoint(nodeId: string, condition?: string): void;
}
```

### 3.3 性能优化策略

**决策**：采用 **分层优化策略**

**Level 1 - 数据层优化**：
- 使用 IndexedDB 缓存分析结果（避免重复请求）
- 实现智能预加载（预测用户下一步展开的节点，提前加载数据）
- 增量更新：代码变更时仅更新受影响节点

**Level 2 - 渲染层优化**：
- **虚拟化渲染**（超大项目 >5000 节点）：
  - 仅渲染可见区域节点（viewport culling）
  - 使用 Cytoscape.js 的 `ele.visible()` 动态切换
- **LOD (Level of Detail)**：
  - 缩小视图时，隐藏节点内部细节（标签、启动按钮）
  - 放大视图时，显示完整信息
- **Canvas 分层**：
  - 静态图层（Cytoscape.js）：节点和边
  - 动画图层（Canvas overlay）：流动箭头、高亮效果
  - 交互图层（SVG overlay）：启动按钮、Tooltip

**Level 3 - 交互层优化**：
- **防抖 (debounce)** 和 **节流 (throttle)**：
  - 缩放/平移事件：throttle 16ms (60 FPS)
  - 节点搜索：debounce 300ms
- **Web Worker**：
  - 布局计算（COSE、dagre）在 Worker 中执行
  - 大数据解析在 Worker 中执行
  - 主线程仅负责渲染和交互

**Level 4 - 降级策略**（性能不足时）：
- 帧率 <15 FPS → 自动禁用动画效果
- 节点数 >10000 → 强制启用虚拟化 + LOD
- 并发流 >10 个 → 自动降级到简化视图（仅显示流数量和汇合点）

### 3.4 前端技术栈

**决策**：

**核心框架**：**React 18** (优先) 或 **Vue 3** (备选)
- 理由：React 18 并发模式适合复杂动画场景，社区生态成熟
- 如团队更熟悉 Vue 3，可选用 Vue 3 Composition API

**状态管理**：**Zustand** (React) 或 **Pinia** (Vue)
- 理由：轻量级、TypeScript 友好、性能优异

**UI 组件库**：**Ant Design** 或 **Chakra UI**
- 理由：提供丰富的表单、面板、控制器组件，减少重复开发

**路由**：**React Router** 或 **Vue Router**
- 理由：支持多视图切换（结构图视图、时序图视图、单步详情视图）

**构建工具**：**Vite** (优先) 或 **Webpack 5**
- 理由：Vite 开发体验极佳，构建速度快

**代码编辑器集成**：**@monaco-editor/react** 或 **monaco-editor-vue3**
- 理由：官方 React/Vue 绑定，开箱即用

**图形库集成**：
- Cytoscape.js：`cytoscape` + `react-cytoscapejs` 或 Vue 包装组件
- D3.js：`d3` + 自定义 React/Vue 组件包装

**类型安全**：**TypeScript 5.x**
- 理由：确保数据协议和接口的类型安全

### 3.5 桌面应用技术选型

**决策**：**Tauri** (优先) 或 **Electron** (备选)

**Tauri 优势**：
- 体积小（<5MB vs Electron 100MB+）
- 内存占用低（<50MB vs Electron 200MB+）
- 使用系统 WebView（macOS WKWebView、Windows WebView2、Linux WebKitGTK）
- Rust 后端安全性高

**Electron 备选理由**：
- 跨平台一致性更高（自带 Chromium）
- 社区生态成熟，问题解决方案丰富
- 如需特定 Chrome API 或插件，Electron 更合适

**推荐方案**：
- 优先开发 Web 版本（Vite + React/Vue）
- 后续使用 Tauri 包装为桌面应用（共享 Web 代码）
- 如遇 Tauri 兼容性问题，回退到 Electron

## 4. 开发工具链与测试策略

### 4.1 开发环境

**后端 (AI 调度 + 适配器层)**：
- **语言**：Python 3.11+
- **包管理**：Poetry (依赖管理 + 虚拟环境)
- **代码格式化**：Black + isort + Ruff
- **类型检查**：mypy --strict
- **测试框架**：pytest + pytest-asyncio + pytest-cov

**前端 (可视化引擎)**：
- **语言**：TypeScript 5.x
- **包管理**：pnpm (速度快、节省磁盘空间)
- **代码格式化**：Prettier + ESLint
- **测试框架**：Vitest (单元测试) + Playwright (E2E 测试)

### 4.2 测试策略

**单元测试覆盖率目标**：
- AI 调度引擎：≥85%
- AI 适配器层：≥85%
- 核心可视化逻辑：≥90%
- Prompt 模板验证：≥80%

**集成测试**：
- 端到端流程测试（完整分析 → 可视化渲染）
- 适配器集成测试（真实 AI 工具调用，使用 mock 模式加速）
- 数据协议验证测试（JSON Schema 验证）

**性能测试**：
- 基准测试（benchmark）：标准测试项目集（小、中、大、超大）
- 渲染性能测试：帧率监控、内存占用监控
- AI 调度性能测试：耗时统计、token 消耗统计

**可用性测试**：
- 用户体验测试（15 分钟内掌握基本操作）
- 无障碍测试（WCAG 2.1 AA 标准）

### 4.3 CI/CD 流程

**持续集成 (GitHub Actions 或 GitLab CI)**：
- 每次 commit 触发：
  - 代码格式化检查（Black, Prettier）
  - 静态类型检查（mypy, TypeScript）
  - 单元测试 + 覆盖率报告
  - JSON Schema 验证
- 每次 PR 触发：
  - 集成测试
  - 性能基准测试（与 main 分支对比）
  - 宪章合规性检查

**持续部署**：
- Web 版本自动部署到 Vercel/Netlify
- 桌面版本自动构建并发布到 GitHub Releases

## 5. 关键未知问题解决

### 5.1 AI 分析结果的可靠性如何保证？

**解决方案**：

**策略 1 - 多模型对比验证**（可选增强）：
- 对关键分析（如并发模式识别）使用 2-3 个不同 AI 模型
- 对比结果，一致性高则采纳，差异大则标注"不确定"
- 需权衡成本（增加 token 消耗）与质量收益

**策略 2 - 置信度评分机制**（必需）：
- 每个 AI 决策附带置信度分数（0.0-1.0）
- 置信度 <0.7 的结果标注为"低置信度"，提供人工标注入口
- 用户可查看 AI 的解释信息（explanation）

**策略 3 - 人工反馈循环**（未来增强）：
- 用户可纠正 AI 的错误（如修改功能命名）
- 系统记录纠正案例，用于优化 Prompt 模板
- 积累高质量训练数据，提升 Prompt 效果

### 5.2 大型项目（>20000 LOC）如何在合理时间内完成分析？

**解决方案**：

**策略 1 - 智能范围限定**：
- 优先分析核心模块（通过项目配置或 README 识别）
- 边缘模块（如 tests/, docs/）可延迟分析或跳过
- 用户可手动标记"重要模块"优先级

**策略 2 - 断点续传机制**：
- AI 调度引擎支持中断恢复
- 每个阶段完成后保存中间结果
- 失败后从最近的检查点恢复

**策略 3 - 后台任务队列**：
- 使用 Celery 或 RQ 将 AI 调用放入后台任务队列
- 前端显示进度条和 ETA（预估剩余时间）
- 支持"优先快速预览"模式（仅分析入口文件，生成简化结构图）

### 5.3 如何处理 AI 不支持的语言或框架？

**解决方案**：

**策略 1 - 降级到静态分析**（未来扩展）：
- 使用 tree-sitter 或 AST 解析器生成基础结构
- 仅提供代码结构图和依赖关系，无语义命名
- 明确标注"有限功能模式"

**策略 2 - 通用 Prompt 模板**：
- 为不支持的语言提供通用 Prompt 模板
- 基于语法相似性推断（如 Kotlin → Java Prompt）
- 质量可能下降，标注"实验性支持"

**策略 3 - 用户扩展机制**：
- 允许用户编写自定义 Prompt 模板
- 提供模板编写指南和最佳实践
- 社区贡献模板库

### 5.4 如何确保"单步运行详情"视图的变量数据准确性？

**解决方案**：

**Phase 1 (MVP) - 基于 AI 推理**：
- AI 在"执行流程推理"阶段生成每一步的变量状态快照
- 数据来源：AI 对代码的静态分析和模拟执行
- 限制：无法保证 100% 准确（AI 可能推理错误）
- 标注：明确标记"AI 推理结果"，置信度分数

**Phase 2 (未来增强) - 集成真实调试器**：
- 使用 DAP (Debug Adapter Protocol) 集成真实调试器（Python Debugger、Node.js Inspector）
- 用户可选择"连接调试器"模式，获得真实运行时数据
- 需要用户启动调试会话，复杂度增加

**推荐路径**：
- MVP 阶段仅实现 AI 推理模式
- 未来根据用户需求和反馈，考虑集成真实调试器

## 6. 总结与下一步

### 6.1 核心技术栈总结

| 组件 | 技术选型 | 理由 |
|------|---------|------|
| Prompt 模板引擎 | YAML + Jinja2 | 人类可读、强大模板能力、易于版本化 |
| AI 调度策略 | 分阶段串行 + 同级并行 | 平衡准确性和性能，支持缓存和增量分析 |
| 适配器接口 | Python Protocol + TypedDict | 标准化、类型安全、可插拔 |
| 数据协议 | JSON Schema v7 | 严格验证、版本化、生态成熟 |
| 主沙盘渲染 | Cytoscape.js | 大型图性能、层级支持、交互丰富 |
| 细节分析渲染 | D3.js | 极高灵活性、强大动画、自定义能力 |
| 单步详情视图 | Monaco Editor | VS Code 内核、专业级代码编辑体验 |
| 动画引擎 | Canvas + RAF | 高性能、支持 10 个并发流 |
| 前端框架 | React 18 / Vue 3 | 成熟生态、并发模式、TypeScript 支持 |
| 后端语言 | Python 3.11+ | AI 生态丰富、开发效率高 |
| 桌面应用 | Tauri (优先) | 体积小、性能高、安全性强 |

### 6.2 风险评估

| 风险 | 概率 | 影响 | 缓解策略 |
|------|------|------|---------|
| AI 分析准确性不足 | 中 | 高 | 置信度评分 + 人工反馈 + 多模型对比 |
| 大型项目分析耗时过长 | 高 | 中 | 智能范围限定 + 断点续传 + 后台任务队列 |
| 并发流可视化性能瓶颈 | 中 | 中 | Canvas 分层 + 降级策略 + 虚拟化渲染 |
| AI 工具连接不稳定 | 中 | 中 | 多适配器支持 + 降级模式 + 缓存机制 |
| 用户学习曲线陡峭 | 中 | 高 | 15 分钟新手引导 + 交互式教程 + 示例项目 |

### 6.3 下一步行动

✅ **Phase 0 (研究) 完成** → 进入 **Phase 1 (设计 & 合约)**

**Phase 1 输出物**：
1. `data-model.md`：核心数据模型设计（实体、关系、状态机）
2. `contracts/`：详细的 API 合约和 JSON Schema
3. `quickstart.md`：快速开始指南和示例代码

**Phase 1 关键决策点**：
- 确定数据库 schema（如果需要持久化）
- 定义 AI 适配器接口的详细方法签名
- 设计可视化引擎的组件架构和状态管理

