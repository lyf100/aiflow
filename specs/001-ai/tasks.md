# Tasks: AI分析指挥与可视化平台 - 层级行为沙盘系统

**Input**: Design documents from `/specs/001-ai/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: 测试任务已包含，基于 plan.md 中的测试覆盖率要求（后端 ≥85%，前端 ≥80%）

**Organization**: 任务按用户故事分组，支持独立实现和测试。遵循 TDD 方法（测试先行）。

## Format: `[ID] [P?] [Story] Description`
- **[P]**: 可并行执行（不同文件，无依赖）
- **[Story]**: 所属用户故事（US1, US2, US3, US4, INFRA）
- 包含精确的文件路径

## Path Conventions
- **Backend**: `backend/aiflow/`, `backend/prompts/`, `backend/tests/`
- **Frontend**: `frontend/src/`, `frontend/tests/`
- **Shared**: `shared/schemas/`

---

## Phase 1: Setup (项目初始化)

**Purpose**: 创建项目结构和基础配置

- [ ] T001 [P] [INFRA] 创建后端目录结构 `backend/aiflow/{adapters,prompts,analysis,protocol,api,utils}/`
- [ ] T002 [P] [INFRA] 创建前端目录结构 `frontend/src/{components,services,stores,types,utils}/`
- [ ] T003 [P] [INFRA] 创建共享目录 `shared/schemas/`
- [ ] T004 [INFRA] 初始化后端 Poetry 项目 `backend/pyproject.toml`（依赖：FastAPI, Jinja2, jsonschema, aiohttp, pytest）
- [ ] T005 [INFRA] 初始化前端 Vite + React + TypeScript 项目 `frontend/package.json`（依赖：React 18, Zustand, Cytoscape.js, D3.js, Monaco Editor）
- [ ] T006 [P] [INFRA] 配置后端代码格式化工具 `backend/.pre-commit-config.yaml`（Black, isort, Ruff, mypy）
- [ ] T007 [P] [INFRA] 配置前端代码格式化工具 `frontend/.eslintrc.js`, `frontend/.prettierrc`
- [ ] T008 [P] [INFRA] 设置 Git LFS 用于 Prompt 模板文件版本管理 `.gitattributes`
- [ ] T009 [P] [INFRA] 创建 CI/CD 配置文件 `.github/workflows/ci.yml`（代码检查、测试、构建）

**Checkpoint**: 项目结构完整，依赖安装成功，代码格式化工具正常工作

---

## Phase 2: Foundational (阻塞性前置任务)

**Purpose**: 核心基础设施，必须在所有用户故事之前完成

**⚠️ CRITICAL**: 所有用户故事工作必须等待此阶段完成

### 2.1 标准数据协议定义（优先级最高）

- [ ] T010 [INFRA] 定义标准数据协议 JSON Schema `shared/schemas/analysis-schema-v1.0.0.json`（已完成 ✅）
- [ ] T011 [P] [INFRA] 实现 JSON Schema 验证器 `backend/aiflow/protocol/validator.py`
- [ ] T012 [P] [INFRA] 实现数据序列化/反序列化 `backend/aiflow/protocol/serializer.py`
- [ ] T013 [P] [INFRA] 定义数据实体类型（Python TypedDict）`backend/aiflow/protocol/entities.py`
- [ ] T014 [P] [INFRA] 定义前端 TypeScript 类型 `frontend/src/types/protocol.ts`（镜像后端实体）
- [ ] T015 [INFRA] 实现引用完整性检查 `backend/aiflow/protocol/validator.py:validate_references()`

### 2.2 核心指令集（Prompt Library）

- [ ] T016 [INFRA] 创建 Prompt 模板注册表 `backend/prompts/registry.yaml`
- [ ] T017 [P] [INFRA] 实现 Prompt 模板管理器 `backend/aiflow/prompts/manager.py`（加载、验证、版本管理）
- [ ] T018 [P] [INFRA] 实现 Jinja2 模板渲染器 `backend/aiflow/prompts/renderer.py`
- [ ] T019 [P] [INFRA] 实现 Prompt 格式验证器 `backend/aiflow/prompts/validator.py`（JSON Schema 验证）
- [ ] T020 [INFRA] 编写初始 Prompt 模板 - Python 项目认知 `backend/prompts/python/project-understanding/v1.0.0.yaml`
- [ ] T021 [P] [INFRA] 编写 Prompt 模板 - Python 结构识别 `backend/prompts/python/structure-recognition/v1.1.0.yaml`
- [ ] T022 [P] [INFRA] 编写 Prompt 模板 - Python 语义分析 `backend/prompts/python/semantic-analysis/v1.0.0.yaml`
- [ ] T023 [P] [INFRA] 编写 Prompt 模板 - Python 执行推理 `backend/prompts/python/execution-inference/v1.0.0.yaml`
- [ ] T024 [P] [INFRA] 编写 Prompt 模板 - Python 并发检测 `backend/prompts/python/concurrency-detection/v1.0.0.yaml`
- [ ] T025 [INFRA] 实现 Prompt 初始化脚本 `backend/aiflow/prompts/init.py`（从 Git LFS 拉取）
- [ ] T025a [INFRA] 实现时间戳格式验证 `backend/aiflow/prompts/validator.py:validate_timestamp_format()`（验证所有 Prompt 模板输出的时间戳符合 ISO 8601 格式规范）

### 2.3 AI 适配器接口（SPI）

- [ ] T026 [INFRA] 定义 AI 适配器 Protocol 接口 `backend/aiflow/adapters/base.py`（AIAdapter, PromptRequest, AnalysisResult）
- [ ] T027 [P] [INFRA] 实现适配器注册表 `backend/aiflow/adapters/registry.py`
- [ ] T028 [P] [INFRA] 实现适配器选择逻辑 `backend/aiflow/adapters/registry.py:select_adapter()`
- [ ] T029 [INFRA] 实现 CLI 适配器基类 `backend/aiflow/adapters/cli_adapter.py`
- [ ] T030 [INFRA] 实现 Cloud API 适配器基类 `backend/aiflow/adapters/cloud_adapter.py`

### 2.4 AI 调度引擎核心

- [ ] T031 [INFRA] 实现 AnalysisJob 实体和状态机 `backend/aiflow/analysis/job.py`
- [ ] T032 [P] [INFRA] 实现 AnalysisEngine 核心调度器 `backend/aiflow/analysis/engine.py`
- [ ] T032a [P] [INFRA] 收集 AI 置信度分数 `backend/aiflow/analysis/engine.py:collect_confidence_scores()`（每个分析阶段结束后收集 AI 的置信度评分）
- [ ] T033 [P] [INFRA] 实现 AI 调度策略（5 阶段串行 + 同级并行）`backend/aiflow/analysis/scheduler.py`
- [ ] T034 [P] [INFRA] 实现分析缓存（SQLite + LRU）`backend/aiflow/analysis/cache.py`
- [ ] T034a [P] [INFRA] 实现适配器健康检查监控 `backend/aiflow/adapters/health_monitor.py`（定期检查适配器状态，记录响应时间和错误率）
- [ ] T034b [INFRA] 实现适配器故障降级机制 `backend/aiflow/adapters/fallback.py`（主适配器失败时自动切换到备用适配器）
- [ ] T034c [INFRA] 实现断路器模式 `backend/aiflow/adapters/circuit_breaker.py`（连续失败达到阈值时暂停调用，等待恢复）
- [ ] T035 [INFRA] 实现项目内容哈希计算 `backend/aiflow/utils/file_hash.py`（用于缓存失效检测）

### 2.5 后端 REST API 基础

- [ ] T036 [INFRA] 创建 FastAPI 主应用 `backend/aiflow/main.py`
- [ ] T037 [P] [INFRA] 配置 CORS 和中间件 `backend/aiflow/main.py:setup_middleware()`
- [ ] T038 [P] [INFRA] 实现统一错误处理 `backend/aiflow/api/error_handlers.py`
- [ ] T039 [P] [INFRA] 实现结构化日志 `backend/aiflow/utils/logger.py`
- [ ] T040 [INFRA] 配置环境变量管理 `backend/aiflow/config.py`

### 2.6 前端基础服务

- [ ] T041 [INFRA] 实现 REST API 客户端 `frontend/src/services/api.ts`
- [ ] T042 [P] [INFRA] 实现 WebSocket 客户端 `frontend/src/services/websocket.ts`
- [ ] T043 [P] [INFRA] 实现 IndexedDB 存储服务 `frontend/src/services/storage.ts`
- [ ] T044 [P] [INFRA] 实现 JSON Schema 验证（ajv）`frontend/src/utils/validation.ts`
- [ ] T045 [INFRA] 配置 Zustand 状态管理 `frontend/src/stores/index.ts`

**Checkpoint**: 基础设施就绪 - 用户故事实现可以并行开始

---

## Phase 3: User Story 1 - AI驱动的代码结构分析与可视化 (Priority: P1) 🎯 MVP

**Goal**: 开发者可快速理解陌生代码项目，通过 AI 自动分析生成层级化、业务语义化的代码结构图

**Independent Test**: 用户提供代码项目路径 → 选择 AI 工具 → 点击"开始分析" → 系统返回可交互的、带业务语义标签的层级结构图，验证节点/分组/连接关系正确

### 3.1 测试先行（TDD）

- [ ] T046 [P] [US1] 单元测试 - Claude Code 适配器 `backend/tests/unit/test_cli_adapter_claude.py`
- [ ] T047 [P] [US1] 单元测试 - AI 调度引擎（5 阶段流程）`backend/tests/unit/test_analysis_engine.py`
- [ ] T048 [P] [US1] 集成测试 - 完整分析流程（小型 Python 项目）`backend/tests/integration/test_full_analysis.py`
- [ ] T049 [P] [US1] 合约测试 - GET /api/analysis/{project_id} `backend/tests/contract/test_analysis_api.py`
- [ ] T050 [P] [US1] 前端单元测试 - StructureGraph 组件 `frontend/tests/unit/components/StructureGraph.test.tsx`

### 3.2 后端实现 - AI 适配器（概念验证）

- [ ] T051 [US1] 实现 Claude Code CLI 适配器 `backend/aiflow/adapters/cli_adapter.py:ClaudeCodeAdapter`（依赖 T029）
- [ ] T052 [US1] 实现适配器健康检查 `backend/aiflow/adapters/cli_adapter.py:health_check()`
- [ ] T053 [US1] 实现适配器能力声明 `backend/aiflow/adapters/cli_adapter.py:get_capabilities()`
- [ ] T054 [US1] 实现错误重试逻辑（指数退避）`backend/aiflow/adapters/base.py:retry_with_backoff()`

### 3.3 后端实现 - AI 调度完整流程

- [ ] T055 [US1] 实现阶段 1 - 项目认知 `backend/aiflow/analysis/scheduler.py:execute_project_understanding()`
- [ ] T056 [US1] 实现阶段 2 - 结构识别 `backend/aiflow/analysis/scheduler.py:execute_structure_recognition()`
- [ ] T057 [US1] 实现阶段 3 - 语义分析 `backend/aiflow/analysis/scheduler.py:execute_semantic_analysis()`
- [ ] T058 [US1] 实现分析结果验证 `backend/aiflow/analysis/engine.py:validate_result()`（JSON Schema 验证）
- [ ] T059 [US1] 实现断点续传机制 `backend/aiflow/analysis/job.py:resume()`

### 3.4 后端实现 - REST API

- [ ] T060 [P] [US1] 实现 POST /api/analysis 触发分析 `backend/aiflow/api/routes/analysis.py:create_analysis()`
- [ ] T061 [P] [US1] 实现 GET /api/analysis/{project_id} 获取结果 `backend/aiflow/api/routes/analysis.py:get_analysis()`
- [ ] T062 [P] [US1] 实现 GET /api/jobs/{job_id} 查询任务状态 `backend/aiflow/api/routes/jobs.py:get_job_status()`
- [ ] T063 [US1] 实现异步任务队列集成（Celery，可选）`backend/aiflow/analysis/tasks.py`

### 3.5 前端实现 - 结构图可视化（Cytoscape.js）

- [ ] T064 [P] [US1] 实现 Cytoscape.js 渲染器组件 `frontend/src/components/StructureGraph/CytoscapeRenderer.tsx`
- [ ] T065 [P] [US1] 实现节点渲染（复合节点支持）`frontend/src/components/StructureGraph/NodeRenderer.tsx`
- [ ] T066 [P] [US1] 实现边渲染（依赖、继承、调用）`frontend/src/components/StructureGraph/EdgeRenderer.tsx`
- [ ] T067 [US1] 实现布局算法选择（COSE, dagre, breadthfirst）`frontend/src/components/StructureGraph/LayoutManager.ts`
- [ ] T068 [US1] 实现缩放/平移交互 `frontend/src/components/StructureGraph/InteractionHandler.ts`
- [ ] T069 [US1] 实现展开/折叠节点（双击）`frontend/src/components/StructureGraph/NodeExpansion.ts`
- [ ] T070 [P] [US1] 实现面包屑导航组件 `frontend/src/components/Common/Breadcrumb.tsx`
- [ ] T071 [US1] 实现虚拟化渲染（>1000 节点）`frontend/src/components/StructureGraph/VirtualizationManager.ts`

### 3.6 前端实现 - 启动按钮

- [ ] T072 [US1] 实现 LaunchButton 组件 `frontend/src/components/StructureGraph/LaunchButton.tsx`
- [ ] T073 [US1] 附加按钮到 Cytoscape.js 节点（overlay layer）`frontend/src/components/StructureGraph/ButtonOverlay.tsx`
- [ ] T074 [US1] 实现按钮点击事件处理 `frontend/src/components/StructureGraph/LaunchButton.tsx:handleClick()`
- [ ] T075 [US1] 区分大按钮/小按钮样式 `frontend/src/components/StructureGraph/LaunchButton.tsx:getButtonStyle()`

### 3.7 前端实现 - UI 集成

- [ ] T076 [US1] 实现分析状态 store `frontend/src/stores/analysisStore.ts`
- [ ] T077 [US1] 实现分析触发 UI `frontend/src/components/AnalysisControl/StartAnalysis.tsx`（项目路径选择、AI 工具选择）
- [ ] T078 [US1] 实现进度条和 ETA 显示 `frontend/src/components/AnalysisControl/ProgressBar.tsx`
- [ ] T079 [US1] 实现错误处理和降级提示 `frontend/src/components/AnalysisControl/ErrorHandler.tsx`

**Checkpoint**: 用户故事 1 完整可测试 - MVP 就绪，可独立部署演示

---

## Phase 4: User Story 2 - 宏观流程联动可视化 (Priority: P2)

**Goal**: 开发者点击大模块的"大按钮"，观察系统如何协调多个子模块进行联动执行，通过动画展示数据流和控制流

**Independent Test**: 在结构图上点击"订单处理系统"的"处理用户订单"按钮 → 系统播放多流程联动动画 → 验证子模块激活顺序、数据流、同步点正确展示

### 4.1 测试先行（TDD）

- [ ] T080 [P] [US2] 单元测试 - 动画管理器 `frontend/tests/unit/services/AnimationManager.test.ts`
- [ ] T081 [P] [US2] 单元测试 - Canvas 动画层 `frontend/tests/unit/components/AnimationControl/CanvasAnimationLayer.test.tsx`
- [ ] T082 [P] [US2] E2E 测试 - 宏观联动动画播放 `frontend/tests/e2e/playwright/macroAnimation.spec.ts`

### 4.2 后端实现 - 执行追踪生成（阶段 4）

- [ ] T083 [US2] 实现阶段 4 - 执行流程推理 `backend/aiflow/analysis/scheduler.py:execute_execution_inference()`
- [ ] T084 [US2] 生成 execution_trace 数据（FlowchartTrace 格式）`backend/aiflow/protocol/entities.py:generate_flowchart_trace()`
- [ ] T085 [US2] 生成 behavior_metadata（启动按钮配置）`backend/aiflow/protocol/entities.py:generate_behavior_metadata()`

### 4.3 后端实现 - WebSocket 动画控制

- [ ] T086 [US2] 实现 WebSocket /ws/animation/{scene_id} `backend/aiflow/api/websocket/animation.py`
- [ ] T087 [US2] 实现动画状态广播 `backend/aiflow/api/websocket/animation.py:broadcast_state()`
- [ ] T088 [US2] 实现动画控制命令处理（play, pause, seek）`backend/aiflow/api/websocket/animation.py:handle_command()`

### 4.4 前端实现 - 动画系统

- [ ] T089 [US2] 实现 AnimationManager `frontend/src/services/animation.ts`（播放、暂停、时间回溯）
- [ ] T090 [US2] 实现 AnimationScene 实体 `frontend/src/types/protocol.ts:AnimationScene`
- [ ] T091 [US2] 实现播放速度调节（0.1x - 10x）`frontend/src/services/animation.ts:setSpeed()`
- [ ] T092 [US2] 实现时间轴管理 `frontend/src/services/animation.ts:Timeline`
- [ ] T093 [US2] 集成 WebSocket 实时更新 `frontend/src/services/websocket.ts:subscribeToAnimation()`

### 4.5 前端实现 - Canvas 动画层

- [ ] T094 [US2] 实现 Canvas overlay（在 Cytoscape.js 之上）`frontend/src/components/AnimationControl/CanvasOverlay.tsx`
- [ ] T095 [US2] 实现节点高亮动画（CSS transition）`frontend/src/components/AnimationControl/NodeHighlight.ts`
- [ ] T096 [US2] 实现流动箭头动画（SVG path + dash-offset）`frontend/src/components/AnimationControl/FlowingArrow.ts`
- [ ] T097 [US2] 实现多流程联动动画（最多 5 个并发流）`frontend/src/components/AnimationControl/MultiFlowAnimation.ts`
- [ ] T098 [US2] 实现并发流颜色区分 `frontend/src/components/AnimationControl/FlowColorManager.ts`
- [ ] T099 [US2] 性能优化（requestAnimationFrame，≥30 FPS）`frontend/src/components/AnimationControl/PerformanceOptimizer.ts`

### 4.6 前端实现 - 播放控制器 UI

- [ ] T100 [US2] 实现 PlaybackController 组件 `frontend/src/components/AnimationControl/PlaybackController.tsx`
- [ ] T101 [P] [US2] 实现播放/暂停按钮（空格键快捷键）`frontend/src/components/AnimationControl/PlayPauseButton.tsx`
- [ ] T102 [P] [US2] 实现快进/后退按钮（箭头键）`frontend/src/components/AnimationControl/NavigationButtons.tsx`
- [ ] T103 [P] [US2] 实现速度调节滑块 `frontend/src/components/AnimationControl/SpeedControl.tsx`
- [ ] T104 [P] [US2] 实现时间轴显示 `frontend/src/components/AnimationControl/Timeline.tsx`
- [ ] T105 [US2] 实现执行总结面板 `frontend/src/components/AnimationControl/ExecutionSummary.tsx`

### 4.7 前端实现 - 动画状态管理

- [ ] T106 [US2] 实现动画 store `frontend/src/stores/animationStore.ts`
- [ ] T107 [US2] 实现钻入子模块逻辑 `frontend/src/stores/animationStore.ts:drillIntoSubmodule()`
- [ ] T108 [US2] 实现动画时间同步 `frontend/src/stores/animationStore.ts:syncTime()`

**Checkpoint**: 用户故事 2 完整可测试 - 宏观联动动画正常工作，US1 和 US2 独立运行

---

## Phase 5: User Story 3 - 微观子流程独立执行 (Priority: P3)

**Goal**: 开发者展开大模块，看到内部子模块的"小按钮"，可独立启动子流程执行，聚焦理解特定逻辑

**Independent Test**: 展开"订单处理系统" → 点击"计算订单价格"的小按钮 → 系统独立播放该子流程动画 → 验证仅该子模块内部组件被激活，支持孤立模式和上下文模式切换

### 5.1 测试先行（TDD）

- [ ] T109 [P] [US3] 单元测试 - 子流程独立执行逻辑 `frontend/tests/unit/services/SubflowExecution.test.ts`
- [ ] T110 [P] [US3] E2E 测试 - 微观子流程动画 `frontend/tests/e2e/playwright/microAnimation.spec.ts`

### 5.2 后端实现 - 行为嵌套数据

- [ ] T111 [US3] 生成 subUnitIds 行为父子关系 `backend/aiflow/protocol/entities.py:TraceableUnit.subUnitIds`
- [ ] T112 [US3] 实现调用链追溯数据 `backend/aiflow/protocol/entities.py:generate_call_chain()`

### 5.3 前端实现 - 子流程执行

- [ ] T113 [US3] 实现子流程独立启动 `frontend/src/services/animation.ts:launchSubflow()`
- [ ] T114 [US3] 实现孤立模式视图 `frontend/src/components/AnimationControl/IsolatedMode.tsx`
- [ ] T115 [US3] 实现上下文模式视图 `frontend/src/components/AnimationControl/ContextMode.tsx`
- [ ] T116 [US3] 实现视图模式切换 `frontend/src/components/AnimationControl/ViewModeToggle.tsx`
- [ ] T117 [US3] 实现向上追溯功能 `frontend/src/components/AnimationControl/TraceUpward.tsx`（显示完整调用链）
- [ ] T118 [US3] 实现嵌套调用可视化（递归支持）`frontend/src/components/AnimationControl/NestedCallVisualization.tsx`

### 5.4 前端实现 - 子流程总结

- [ ] T119 [US3] 实现子流程执行总结组件 `frontend/src/components/AnimationControl/SubflowSummary.tsx`（输入参数、输出结果、内部状态）
- [ ] T120 [US3] 实现"在大流程中查看"跳转 `frontend/src/components/AnimationControl/ViewInMacro.tsx`

**Checkpoint**: 用户故事 3 完整可测试 - 微观子流程独立执行正常，US1-3 独立运行

---

## Phase 6: User Story 4 - 单步运行详情视图深度分析 (Priority: P4)

**Goal**: 开发者在动画暂停时点击代码单元，进入"单步运行详情"视图，查看代码行/变量值/调用栈/内存快照，支持逐行单步执行和假设分析

**Independent Test**: 在动画中暂停 → 点击当前激活代码单元 → 打开单步详情视图 → 验证 Monaco Editor 显示代码、变量面板显示变量、调用栈面板显示函数链、支持 Step Into/Over/Out、变量修改和历史查看

### 6.1 测试先行（TDD）

- [ ] T121 [P] [US4] 单元测试 - Monaco Editor 集成 `frontend/tests/unit/components/StepDetailView/CodeEditor.test.tsx`
- [ ] T122 [P] [US4] 单元测试 - 变量面板 `frontend/tests/unit/components/StepDetailView/VariablePanel.test.tsx`
- [ ] T123 [P] [US4] E2E 测试 - 单步执行流程 `frontend/tests/e2e/playwright/stepByStepExecution.spec.ts`

### 6.2 后端实现 - 单步追踪数据（阶段 4 增强）

- [ ] T124 [US4] 生成 StepByStepTrace 数据 `backend/aiflow/protocol/entities.py:generate_step_by_step_trace()`（包含 timestamp（ISO 8601格式）和 execution_order 字段）
- [ ] T125 [US4] 生成 variableScopes 结构 `backend/aiflow/protocol/entities.py:VariableScope`（包含 scope_type 枚举（global, local, closure, class, module）、timestamp（ISO 8601）、execution_order）
- [ ] T126 [US4] 生成 callStack 数据 `backend/aiflow/protocol/entities.py:StackFrame`（包含 module_name、is_recursive、recursion_depth、local_scope_id、parent_frame_id、timestamp（ISO 8601）、execution_order）
- [ ] T127 [US4] 生成变量历史轨迹 `backend/aiflow/protocol/entities.py:Variable.history`（使用 execution_order 而非 step_id，timestamp 为 ISO 8601 格式）
- [ ] T128 [US4] 生成递归调用栈数据 `backend/aiflow/protocol/entities.py:StackFrame.depth`（使用 is_recursive + recursion_depth 字段，支持递归深度跟踪）

### 6.3 前端实现 - Monaco Editor 集成

- [ ] T129 [US4] 集成 Monaco Editor `frontend/src/components/StepDetailView/CodeEditor.tsx`（使用 @monaco-editor/react）
- [ ] T130 [US4] 配置语法高亮（Python, JavaScript, TypeScript, Java）`frontend/src/components/StepDetailView/CodeEditor.tsx:configureLanguages()`
- [ ] T131 [US4] 实现当前行高亮 `frontend/src/components/StepDetailView/CodeEditor.tsx:highlightCurrentLine()`
- [ ] T132 [US4] 实现断点设置（行断点）`frontend/src/components/StepDetailView/CodeEditor.tsx:setBreakpoint()`
- [ ] T133 [US4] 实现条件断点设置 `frontend/src/components/StepDetailView/ConditionalBreakpoint.tsx`
- [ ] T134 [US4] 实现跳转到代码行 `frontend/src/components/StepDetailView/CodeEditor.tsx:jumpToLine()`

### 6.4 前端实现 - 变量和调用栈面板

- [ ] T135 [US4] 实现 VariablePanel 组件 `frontend/src/components/StepDetailView/VariablePanel.tsx`
- [ ] T136 [US4] 实现变量展开（对象/数组/树）`frontend/src/components/StepDetailView/VariableExpander.tsx`
- [ ] T137 [US4] 实现变量值编辑（假设分析）`frontend/src/components/StepDetailView/VariableEditor.tsx`
- [ ] T138 [US4] 实现变量历史轨迹查看 `frontend/src/components/StepDetailView/VariableHistory.tsx`
- [ ] T139 [US4] 实现 CallStackPanel 组件 `frontend/src/components/StepDetailView/CallStackPanel.tsx`
- [ ] T140 [US4] 实现调用栈帧点击跳转 `frontend/src/components/StepDetailView/CallStackPanel.tsx:jumpToFrame()`

### 6.5 前端实现 - 单步执行控制

- [ ] T141 [US4] 实现 Step Into（F11）`frontend/src/services/stepExecution.ts:stepInto()`
- [ ] T142 [US4] 实现 Step Over（F10）`frontend/src/services/stepExecution.ts:stepOver()`
- [ ] T143 [US4] 实现 Step Out（Shift+F11）`frontend/src/services/stepExecution.ts:stepOut()`
- [ ] T144 [US4] 实现执行步骤导航（前进/后退）`frontend/src/services/stepExecution.ts:navigate()`
- [ ] T145 [US4] 实现断点暂停机制 `frontend/src/services/stepExecution.ts:checkBreakpoint()`
- [ ] T146 [US4] 实现条件断点求值 `frontend/src/services/stepExecution.ts:evaluateCondition()`

### 6.6 前端实现 - 与主结构图双向同步

- [ ] T147 [US4] 实现详情视图 → 主结构图同步 `frontend/src/stores/animationStore.ts:syncToMainGraph()`
- [ ] T148 [US4] 实现主结构图 → 详情视图同步 `frontend/src/stores/animationStore.ts:syncToDetailView()`
- [ ] T149 [US4] 实现跨层级自动展开 `frontend/src/components/StructureGraph/AutoExpand.ts`

### 6.7 前端实现 - 内存视图（可选）

- [ ] T150 [P] [US4] 实现 MemoryPanel 组件 `frontend/src/components/StepDetailView/MemoryPanel.tsx`
- [ ] T151 [P] [US4] 实现堆对象列表展示 `frontend/src/components/StepDetailView/HeapObjectList.tsx`
- [ ] T152 [US4] 实现对象引用图（D3.js force graph）`frontend/src/components/StepDetailView/ObjectReferenceGraph.tsx`
- [ ] T153 [US4] 实现内存快照对比 `frontend/src/components/StepDetailView/MemoryComparison.tsx`

### 6.8 前端实现 - 假设分析模式

- [ ] T154 [US4] 实现假设分析模式标识 `frontend/src/stores/stepDetailStore.ts:hypotheticalMode`
- [ ] T155 [US4] 实现变量修改应用 `frontend/src/services/stepExecution.ts:applyVariableChange()`
- [ ] T156 [US4] 实现后续执行重新计算 `frontend/src/services/stepExecution.ts:recalculate()`
- [ ] T157 [US4] 实现退出假设模式 `frontend/src/services/stepExecution.ts:exitHypotheticalMode()`
- [ ] T158 [US4] 实现假设分析异常捕获和回退 `frontend/src/services/stepExecution.ts:handleHypotheticalError()`

**Checkpoint**: 用户故事 4 完整可测试 - 单步详情视图功能完整，US1-4 全部独立运行

---

## Phase 7: 并发流可视化增强 (基于 US2 扩展)

**Purpose**: 完成并发检测（阶段 5）和并发流可视化（时序图、流程图、同步点）

### 7.1 测试先行

- [ ] T159 [P] [US2] 单元测试 - 并发检测 `backend/tests/unit/test_concurrency_detection.py`
- [ ] T160 [P] [US2] 单元测试 - 时序图渲染 `frontend/tests/unit/components/DetailViews/SequenceView.test.tsx`
- [ ] T161 [P] [US2] E2E 测试 - 并发流可视化 `frontend/tests/e2e/playwright/concurrencyVisualization.spec.ts`

### 7.2 后端实现 - 并发检测（阶段 5）

- [ ] T162 [US2] 实现阶段 5 - 并发模式识别 `backend/aiflow/analysis/scheduler.py:execute_concurrency_detection()`
- [ ] T163 [US2] 生成 concurrency_info 数据 `backend/aiflow/protocol/entities.py:ConcurrencyInfo`
- [ ] T164 [US2] 识别并发类型（parallel, concurrent, async, sync_wait）`backend/aiflow/protocol/entities.py:detect_concurrency_type()`
- [ ] T165 [US2] 生成同步点数据 `backend/aiflow/protocol/entities.py:SyncPoint`

### 7.3 前端实现 - 流程图渲染（D3.js）

- [ ] T166 [US2] 实现 FlowchartView 组件 `frontend/src/components/DetailViews/FlowchartView.tsx`
- [ ] T167 [US2] 渲染 steps（start, end, process, decision, fork, join）`frontend/src/components/DetailViews/FlowchartSteps.tsx`
- [ ] T168 [US2] 渲染 connections（control_flow, data_flow）`frontend/src/components/DetailViews/FlowchartConnections.tsx`
- [ ] T169 [US2] 实现 Fork/Join 并发网关标识 `frontend/src/components/DetailViews/ForkJoinGateway.tsx`
- [ ] T170 [US2] 实现流程图缩放/平移 `frontend/src/components/DetailViews/FlowchartZoom.ts`
- [ ] T171 [US2] 实现当前步骤高亮动画 `frontend/src/components/DetailViews/FlowchartHighlight.ts`

### 7.4 前端实现 - 时序图渲染（D3.js）

- [ ] T172 [US2] 实现 SequenceView 组件 `frontend/src/components/DetailViews/SequenceView.tsx`
- [ ] T173 [US2] 渲染 lifelines（垂直生命线）`frontend/src/components/DetailViews/Lifelines.tsx`
- [ ] T174 [US2] 渲染 messages（同步/异步/返回）`frontend/src/components/DetailViews/Messages.tsx`
- [ ] T175 [US2] 实现时间轴（垂直方向）`frontend/src/components/DetailViews/TimeAxis.tsx`
- [ ] T176 [US2] 标注关键时间点和等待时长 `frontend/src/components/DetailViews/TimestampLabels.tsx`
- [ ] T177 [US2] 实现消息传递动画 `frontend/src/components/DetailViews/MessageAnimation.ts`

### 7.5 前端实现 - 并发流视图

- [ ] T178 [US2] 实现 ConcurrencyView 组件 `frontend/src/components/DetailViews/ConcurrencyView.tsx`
- [ ] T179 [US2] 集成时序图和流程图 `frontend/src/components/DetailViews/ConcurrencyView.tsx:integrateViews()`
- [ ] T180 [US2] 实现同步点可视化（栅栏、互斥锁、信号量、Join）`frontend/src/components/DetailViews/SyncPointMarker.tsx`
- [ ] T181 [US2] 实现单流聚焦模式 `frontend/src/components/DetailViews/SingleFlowFocus.tsx`
- [ ] T182 [US2] 实现对齐时间轴功能 `frontend/src/components/DetailViews/AlignTimeline.tsx`
- [ ] T183 [US2] 实现并发流独立控制（暂停全部/暂停单个）`frontend/src/components/DetailViews/FlowControl.tsx`

**Checkpoint**: 并发流可视化完整 - 时序图、流程图、同步点正常工作

---

## Phase 8: 进阶功能 (跨用户故事)

**Purpose**: 执行书签、假设分析、多路径对比、全局搜索等增强功能

### 8.1 测试先行

- [ ] T184 [P] [POLISH] 单元测试 - 执行书签 `frontend/tests/unit/stores/bookmarkStore.test.ts`
- [ ] T185 [P] [POLISH] 单元测试 - 多路径对比 `frontend/tests/unit/services/PathComparison.test.ts`
- [ ] T186 [P] [POLISH] E2E 测试 - 全局搜索 `frontend/tests/e2e/playwright/globalSearch.spec.ts`

### 8.2 执行书签

- [ ] T187 [P] [POLISH] 实现 Bookmark 实体和 IndexedDB 存储 `frontend/src/stores/bookmarkStore.ts`
- [ ] T188 [P] [POLISH] 实现创建书签 UI `frontend/src/components/Common/CreateBookmark.tsx`
- [ ] T189 [P] [POLISH] 实现书签列表面板 `frontend/src/components/Common/BookmarkList.tsx`
- [ ] T190 [POLISH] 实现书签跳转功能 `frontend/src/stores/bookmarkStore.ts:jumpToBookmark()`
- [ ] T191 [POLISH] 实现书签对比视图（并排展示）`frontend/src/components/Common/BookmarkComparison.tsx`

### 8.3 多路径对比

- [ ] T192 [POLISH] 实现多路径对比 UI `frontend/src/components/PathComparison/PathComparisonView.tsx`
- [ ] T193 [POLISH] 实现分支选择功能 `frontend/src/components/PathComparison/BranchSelector.tsx`
- [ ] T194 [POLISH] 实现差异高亮（变量值、执行路径）`frontend/src/components/PathComparison/DiffHighlighter.tsx`
- [ ] T195 [POLISH] 实现路径切换动画 `frontend/src/components/PathComparison/PathSwitchAnimation.ts`

### 8.4 全局搜索和过滤

- [ ] T196 [P] [POLISH] 实现全局搜索功能 `frontend/src/services/search.ts`（函数调用、变量修改、事件）
- [ ] T197 [P] [POLISH] 实现节点搜索 UI `frontend/src/components/Common/SearchBar.tsx`
- [ ] T198 [P] [POLISH] 实现执行历史搜索 `frontend/src/services/search.ts:searchExecutionHistory()`
- [ ] T199 [POLISH] 实现搜索结果高亮和跳转 `frontend/src/services/search.ts:highlightAndJump()`

**Checkpoint**: 进阶功能完整 - 书签、对比、搜索正常工作

---

## Phase 9: 性能优化和打磨

**Purpose**: 性能优化、用户体验打磨、错误处理改进

### 9.1 性能优化

- [ ] T200 [P] [POLISH] 前端性能分析和优化（Chrome DevTools Profiler）`docs/performance-report.md`
- [ ] T201 [P] [POLISH] 虚拟化渲染优化（Cytoscape.js viewport culling）`frontend/src/components/StructureGraph/VirtualizationManager.ts`（优化 T071）
- [ ] T202 [P] [POLISH] Canvas 动画优化（减少重绘、分层渲染）`frontend/src/components/AnimationControl/CanvasOptimizer.ts`
- [ ] T203 [P] [POLISH] IndexedDB 查询优化（索引优化）`frontend/src/services/storage.ts`（优化 T043）
- [ ] T204 [P] [POLISH] 后端性能分析（cProfile, line_profiler）`docs/backend-performance-report.md`
- [ ] T205 [P] [POLISH] AI 调度并行优化（并行调用独立模块）`backend/aiflow/analysis/scheduler.py`（优化 T033）
- [ ] T206 [P] [POLISH] 缓存策略优化（提高命中率到 ≥70%）`backend/aiflow/analysis/cache.py`（优化 T034）
- [ ] T207 [POLISH] 内存泄漏排查和修复 `docs/memory-leak-analysis.md`

### 9.2 用户体验打磨

- [ ] T208 [P] [POLISH] 新手引导教程（15 分钟）`frontend/src/components/Onboarding/Tutorial.tsx`
- [ ] T209 [P] [POLISH] 交互式示例项目（预加载分析结果）`frontend/public/examples/`
- [ ] T210 [P] [POLISH] 错误提示优化（友好提示和解决建议）`frontend/src/components/Common/ErrorToast.tsx`
- [ ] T211 [P] [POLISH] 加载动画和进度提示 `frontend/src/components/Common/LoadingAnimation.tsx`
- [ ] T212 [P] [POLISH] 响应式设计（支持不同屏幕尺寸）`frontend/src/styles/responsive.css`
- [ ] T213 [P] [POLISH] 无障碍支持（WCAG 2.1 AA）`frontend/src/utils/accessibility.ts`
- [ ] T214 [P] [POLISH] 主题切换（亮色/暗色模式）`frontend/src/stores/uiStore.ts:themeMode`

**Checkpoint**: 性能优化完成 - 满足所有性能目标（中型项目首次渲染 <3秒，层级切换 P95 <300ms，动画 ≥30 FPS）

---

## Phase 10: 测试补充和文档

**Purpose**: 完整测试覆盖、文档完善、CI/CD 搭建

### 10.1 测试补充

- [ ] T215 [P] [POLISH] 后端单元测试补充（覆盖率 ≥85%）`backend/tests/unit/`
- [ ] T216 [P] [POLISH] 前端单元测试补充（覆盖率 ≥80%）`frontend/tests/unit/`
- [ ] T217 [P] [POLISH] E2E 测试补充（覆盖所有关键流程）`frontend/tests/e2e/playwright/`
- [ ] T218 [P] [POLISH] 性能基准测试（标准测试项目集）`backend/tests/benchmarks/`
- [ ] T219 [POLISH] 可用性测试（5-10 名用户）`docs/usability-test-report.md`

### 10.2 文档完善

- [ ] T220 [P] [POLISH] API 文档完善（OpenAPI）`backend/openapi.yaml`
- [ ] T221 [P] [POLISH] Prompt 模板编写指南 `docs/prompt-guide.md`
- [ ] T222 [P] [POLISH] 适配器开发指南 `docs/adapter-development.md`
- [ ] T223 [P] [POLISH] 贡献指南 `CONTRIBUTING.md`
- [ ] T224 [P] [POLISH] 架构设计文档（ADR）`docs/architecture/`

### 10.3 CI/CD 搭建

- [ ] T225 [P] [POLISH] GitHub Actions 配置（代码检查、测试、构建）`.github/workflows/ci.yml`（扩展 T009）
- [ ] T226 [P] [POLISH] 自动化测试（每次 commit 触发）`.github/workflows/test.yml`
- [ ] T227 [P] [POLISH] 自动化部署（Vercel/Netlify）`.github/workflows/deploy.yml`
- [ ] T228 [POLISH] 性能基准对比（与 main 分支对比）`.github/workflows/benchmark.yml`

**Checkpoint**: 测试和文档完整 - 覆盖率达标，CI/CD 正常工作

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 无依赖 - 可立即开始
- **Foundational (Phase 2)**: 依赖 Phase 1 完成 - **阻塞所有用户故事**
- **User Stories (Phase 3-6)**: 全部依赖 Phase 2 完成
  - US1-4 可并行开始（如有团队容量）
  - 或按优先级顺序（P1 → P2 → P3 → P4）
- **Concurrent Viz (Phase 7)**: 依赖 US2 部分完成（扩展 US2 的并发能力）
- **Advanced Features (Phase 8)**: 依赖 US1-4 完成
- **Polish (Phase 9-10)**: 依赖所有功能完成

### User Story Dependencies

- **User Story 1 (P1)**: Phase 2 完成后即可开始 - 无其他依赖（MVP）
- **User Story 2 (P2)**: Phase 2 完成后即可开始 - 与 US1 独立，但扩展 US1 的结构图
- **User Story 3 (P3)**: Phase 2 + US2 部分完成 - 需要 US2 的动画系统
- **User Story 4 (P4)**: Phase 2 + US2 部分完成 - 需要 US2 的动画暂停功能

### Within Each User Story

- 测试先行（TDD）：测试 → 实现
- 后端优先：适配器 → 调度 → API → 前端
- 分层实现：数据层 → 服务层 → UI 层
- 独立测试：每个故事完成后独立验证

### Parallel Opportunities

**Phase 1 (Setup)**: T001-T003 并行，T006-T009 并行

**Phase 2 (Foundational)**:
- T011-T015 并行（数据协议）
- T017-T019 并行（Prompt 管理）
- T020-T024 并行（Prompt 模板）
- T027-T028 并行（适配器注册）
- T032-T034 并行（AI 调度）
- T037-T039 并行（API 基础）
- T041-T044 并行（前端服务）

**Phase 3 (US1)**:
- T046-T050 并行（测试）
- T060-T062 并行（REST API）
- T064-T066 并行（结构图渲染）
- T101-T104 并行（播放控制器 UI，在 US2 中）

**Phase 4-10**: 类似并行机会，标记 [P] 的任务均可并行

**跨用户故事并行**（如有多人团队）：
- Phase 2 完成后，US1 和 US2 可并行开始
- US1 T064-T071（结构图）与 US2 T089-T099（动画系统）并行
- US3 和 US4 可在 US2 基础完成后并行

---

## Parallel Example: User Story 1

```bash
# 后端测试并行（T046-T049）
Task: "单元测试 - Claude Code 适配器 backend/tests/unit/test_cli_adapter_claude.py"
Task: "单元测试 - AI 调度引擎 backend/tests/unit/test_analysis_engine.py"
Task: "集成测试 - 完整分析流程 backend/tests/integration/test_full_analysis.py"
Task: "合约测试 - GET /api/analysis/{project_id} backend/tests/contract/test_analysis_api.py"

# REST API 并行（T060-T062）
Task: "实现 POST /api/analysis backend/aiflow/api/routes/analysis.py:create_analysis()"
Task: "实现 GET /api/analysis/{project_id} backend/aiflow/api/routes/analysis.py:get_analysis()"
Task: "实现 GET /api/jobs/{job_id} backend/aiflow/api/routes/jobs.py:get_job_status()"

# 前端结构图渲染并行（T064-T066）
Task: "实现 Cytoscape.js 渲染器 frontend/src/components/StructureGraph/CytoscapeRenderer.tsx"
Task: "实现节点渲染 frontend/src/components/StructureGraph/NodeRenderer.tsx"
Task: "实现边渲染 frontend/src/components/StructureGraph/EdgeRenderer.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only) 🎯

1. **Phase 1**: Setup（T001-T009）
2. **Phase 2**: Foundational（T010-T045）- **CRITICAL 阻塞**
3. **Phase 3**: User Story 1（T046-T079）
4. **STOP and VALIDATE**: 独立测试 US1（用户可分析代码项目并查看结构图）
5. **Deploy/Demo**: MVP 就绪，可演示核心价值

### Incremental Delivery

1. **Foundation Ready**: Phase 1 + Phase 2 → 基础设施完整
2. **MVP (US1)**: 独立测试 → 部署/演示（核心价值：AI 驱动的代码结构可视化）
3. **US2 (宏观联动)**: 独立测试 → 部署/演示（增加价值：动画展示多流程协同）
4. **US3 (微观子流程)**: 独立测试 → 部署/演示（增加价值：聚焦特定逻辑）
5. **US4 (单步详情)**: 独立测试 → 部署/演示（最终价值：调试器级深度分析）
6. **Polish**: 性能优化、进阶功能、文档完善

### Parallel Team Strategy

**单人团队**：按优先级顺序实施（Phase 1 → 2 → US1 → US2 → US3 → US4 → Polish）

**多人团队**：
1. **全员合作**: Phase 1 + Phase 2（Foundation 必须完成）
2. **并行开发**（Phase 2 完成后）:
   - Developer A: US1（T046-T079）
   - Developer B: US2（T080-T108）并行实施 US2 独立部分
   - Developer C: Phase 7 并发可视化（T159-T183）
3. **顺序集成**: US3 → US4（依赖 US2 动画系统）
4. **全员合作**: Phase 8-10（Polish）

### 用户提供的额外任务上下文整合

根据用户提供的任务列表，已在各阶段中整合：

1. **定义"标准数据协议"**: Phase 2.1（T010-T015）✅
2. **设计并撰写"核心指令集"**: Phase 2.2（T016-T025）✅
3. **设计 AI 适配器接口（SPI）**: Phase 2.3（T026-T030）✅
4. **开发概念验证适配器**: Phase 3.2（T051-T054）- Claude Code 适配器 ✅
5. **开发"层级行为沙盘"引擎（Cytoscape.js）**:
   - 5a. 嵌套/可展开结构图: Phase 3.5（T064-T071）✅
   - 5b. 大/小启动按钮: Phase 3.6（T072-T075）✅
   - 5c. 多流程联动动画: Phase 4.5（T094-T099）✅
6. **开发"单步运行详情"渲染器（D3.js + Monaco Editor）**:
   - 6a. 流程图/时序图: Phase 7.3-7.4（T166-T177）✅
   - 6b. 时间轴/暂停/变量检查: Phase 6.3-6.4（T129-T140）✅
7. **端到端集成与用户测试**: Phase 10（T215-T228）✅

---

## Notes

- **[P] 任务**: 不同文件，无依赖，可并行执行
- **[Story] 标签**: 映射任务到用户故事，便于追踪
- **每个用户故事**: 独立可完成和测试
- **TDD 方法**: 测试先行，确保测试失败后再实现
- **提交频率**: 每个任务或逻辑组完成后提交
- **检查点**: 每个用户故事完成后独立验证
- **避免**: 模糊任务、同文件冲突、破坏独立性的跨故事依赖

**总任务数**: 228 个任务
**用户故事分布**:
- US1 (MVP): 34 个任务（T046-T079）
- US2 (宏观联动): 29 个任务（T080-T108）
- US3 (微观子流程): 12 个任务（T109-T120）
- US4 (单步详情): 38 个任务（T121-T158）
- 并发可视化（US2 扩展）: 25 个任务（T159-T183）
- 进阶功能（Polish）: 16 个任务（T184-T199）
- 性能优化（Polish）: 14 个任务（T200-T214）
- 测试和文档（Polish）: 14 个任务（T215-T228）
- 基础设施（INFRA）: 45 个任务（T001-T045）

**建议 MVP 范围**: Phase 1 + Phase 2 + Phase 3 (User Story 1)，共 88 个任务
**并行机会**: 约 120 个任务标记 [P]，可显著加速实施

---

**Generated**: 2025-10-09 | **Status**: Ready for Implementation
