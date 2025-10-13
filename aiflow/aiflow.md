# Agent Context: 001-ai - AIFlow 可视化平台

**Last Updated**: 2025-10-12
**Feature Branch**: 001-ai
**Project Type**: 无外壳 MCP Tools + 静态前端可视化平台
**Status**: Phase 3 Frontend Complete ✅

## Quick Reference

### Languages & Versions
- **Frontend**: TypeScript 5.x + React 18
- **Protocol**: JSON Schema v1.0.0
- **Target Platform**: Modern Web Browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)

### Primary Dependencies

**Frontend**:
- React 18.3+ (UI框架，支持并发渲染)
- TypeScript 5.x (类型安全)
- Zustand 4.x (轻量级状态管理)
- Cytoscape.js 3.x (代码结构图可视化)
- D3.js 7.x (执行轨迹可视化)
- Monaco Editor (代码逐步执行展示)
- Vite 5.x (构建工具)
- pnpm (包管理器)

### Storage
- **Frontend**: LocalStorage (用户偏好) + 文件系统 (JSON分析结果)

## 项目定位

**AIFlow** 是一个"无外壳"的 MCP Tools（Model Context Protocol 工具），核心理念是：

1. **智能委托策略**：平台不解析代码，而是通过 Prompt 模板"指挥" AI 进行分析
2. **技术栈无关性**：通过 AI 适配器 SPI，支持任何 AI 服务（Claude、GPT-4、Gemini等）
3. **嵌套式行为启动**：大按钮(macro) → 小按钮(micro) → 微按钮(function) 的递归结构
4. **纯静态前端**：无需后端服务器，直接加载 AI 生成的 JSON 文件进行可视化

## 架构概览

### 核心创新

**嵌套式行为启动（Nested Behavior Launch）**
```
系统级大按钮 (System Macro Button)
  ├─ 模块级大按钮 (Module Macro Button)
  │   ├─ 组件级小按钮 (Component Micro Button)
  │   │   ├─ 函数级微按钮 (Function Micro Button)
  │   │   └─ 函数级微按钮
  │   └─ 组件级小按钮
  └─ 模块级大按钮
```

每个按钮可独立启动，触发对应层级的执行动画。

### 数据流

```
用户项目 → AI分析 (通过Prompt模板) → 标准JSON → 前端加载 → 可视化展示
```

**关键特征**：
- AI 负责所有语义分析和代码理解
- 平台仅负责数据可视化和用户交互
- JSON 作为 AI 与前端的标准协议

### 前端架构（已完成 ✅）

```
frontend/src/
├── stores/                    # Zustand 状态管理
│   ├── analysisStore.ts       # 分析数据状态（带持久化）
│   └── visualizationStore.ts  # UI控制状态（view, animation, theme）
│
├── utils/                     # 工具函数
│   ├── dataLoader.ts          # JSON加载器（文件/URL，支持gzip）
│   └── validators.ts          # 数据验证（UUID、引用完整性）
│
├── components/
│   ├── Layout/                # 布局组件
│   │   ├── AppLayout.tsx      # 主布局（Header + Sidebar + Content）
│   │   └── AppLayout.css
│   │
│   ├── Controls/              # 控制组件
│   │   ├── ViewSwitcher.tsx   # 视图切换器（4种可视化模式）
│   │   ├── ViewSwitcher.css
│   │   ├── AnimationController.tsx  # 动画控制器（播放/暂停/步进）
│   │   └── AnimationController.css
│   │
│   ├── CodeStructureGraph/    # 代码结构图（Cytoscape.js）
│   │   ├── CodeStructureGraph.tsx
│   │   └── CodeStructureGraph.css
│   │
│   ├── LaunchButton/          # 嵌套启动按钮（核心创新）
│   │   ├── LaunchButton.tsx   # 递归嵌套按钮组件
│   │   ├── LaunchButton.css
│   │   ├── LaunchButtonList.tsx  # 按钮列表管理
│   │   └── LaunchButtonList.css
│   │
│   └── ExecutionTrace/        # 执行轨迹可视化
│       ├── FlowchartViewer.tsx    # D3.js 流程图
│       ├── FlowchartViewer.css
│       ├── SequenceViewer.tsx     # D3.js 序列图
│       ├── SequenceViewer.css
│       ├── StepByStepViewer.tsx   # Monaco Editor 逐步执行
│       └── StepByStepViewer.css
│
├── types/                     # TypeScript 类型定义
│   └── protocol.ts            # JSON Schema 对应的 TypedDict
│
├── App.tsx                    # 主应用组件
├── App.css                    # 主应用样式
├── main.tsx                   # React 入口
└── index.css                  # 全局样式
```

## 数据协议

**标准格式**: JSON Schema v1.0.0
- Schema位置: `specs/001-ai/contracts/analysis-schema-v1.0.0.json`
- 向后兼容: ≥2 MAJOR 版本

### 核心数据结构

```typescript
interface AnalysisResult {
  metadata: {
    project_id: string;          // UUID v4
    project_name?: string;
    timestamp: string;           // ISO 8601
    ai_model: string;
    protocol_version: string;    // 语义化版本
  };

  code_structure: {
    nodes: CodeNode[];           // 代码节点
    edges: CodeEdge[];           // 依赖关系
  };

  behavior_metadata: {
    launch_buttons: LaunchButton[];  // 嵌套启动按钮
  };

  execution_trace: {
    traceable_units: TraceableUnit[];  // 可追踪单元
  };

  concurrency_info?: {
    concurrent_flows: ConcurrentFlow[];  // 并发流
    sync_points: SyncPoint[];            // 同步点
  };
}
```

### LaunchButton 结构（核心创新）

```typescript
interface LaunchButton {
  id: string;                    // UUID v4
  name: string;                  // 按钮名称
  type: 'macro' | 'micro';       // 大按钮/小按钮
  level: 'system' | 'module' | 'component' | 'function';
  description?: string;
  icon?: string;                 // Emoji 图标

  parent_button_id?: string;     // 父按钮ID（null = 顶层）
  child_button_ids?: string[];   // 子按钮ID列表

  traceable_unit_id?: string;    // 关联的执行轨迹

  metadata?: {
    ai_confidence?: number;      // AI 置信度 [0, 1]
    estimated_duration?: number; // 预估执行时间（毫秒）
    requires_input?: boolean;    // 是否需要用户输入
    has_side_effects?: boolean;  // 是否有副作用
  };
}
```

## 可视化模式

### 1. 代码结构图（Structure View）
- **技术**: Cytoscape.js + Dagre 布局
- **功能**:
  - 展示代码节点（system, module, class, function）和依赖关系
  - 支持缩放、拖拽、节点高亮、展开/折叠
  - 多种布局算法（dagre, cose, circle, grid）
- **侧边栏**: 嵌套启动按钮列表

### 2. 序列图（Sequence View）
- **技术**: D3.js
- **功能**:
  - 展示组件间的消息传递和方法调用
  - 参与者生命线、激活框
  - 支持不同消息类型（call, return, async, create, destroy）
- **控制**: 动画控制器

### 3. 流程图（Flowchart View）
- **技术**: D3.js
- **功能**:
  - 展示执行流程和控制流
  - 支持 fork（并发分叉）和 join（并发汇合）节点
  - 不同步骤类型（start, end, process, decision, fork, join）
- **控制**: 动画控制器

### 4. 逐步执行（Step-by-Step View）
- **技术**: Monaco Editor
- **功能**:
  - 逐行展示代码执行过程
  - 当前执行行高亮、已执行行标记
  - 变量状态展示、调用栈展示
  - 步骤列表导航
- **控制**: 动画控制器

## 核心特性

### 1. 无外壳 MCP Tools
- ✅ 无需后端服务器
- ✅ 纯静态前端加载 JSON 文件
- ✅ AI 负责全部代码分析
- ✅ 平台仅负责可视化

### 2. 嵌套式行为启动
- ✅ 递归嵌套按钮结构（大→小→微）
- ✅ 每个按钮独立启动执行动画
- ✅ AI 置信度显示
- ✅ 元数据支持（执行时间、副作用等）

### 3. 多格式可视化
- ✅ 代码结构图（Cytoscape.js）
- ✅ 序列图（D3.js）
- ✅ 流程图（D3.js）
- ✅ 逐步执行（Monaco Editor）

### 4. 动画控制
- ✅ 播放/暂停/停止
- ✅ 步进控制（前进/后退）
- ✅ 速度调节（0.25x - 4x）
- ✅ 进度条拖动

### 5. 用户体验
- ✅ 响应式设计（桌面/平板/移动）
- ✅ 主题切换（亮色/暗色）
- ✅ 文件上传/URL加载
- ✅ 数据导出
- ✅ 搜索和过滤
- ✅ 加载动画和错误处理

### 6. 性能优化
- ✅ 支持 gzip 压缩文件
- ✅ 100MB 文件大小限制
- ✅ 数据验证和错误提示
- ✅ 状态持久化（分析数据）
- ✅ 组件懒加载

## 完成状态

### Phase 1: 项目规划 ✅
- [x] 需求分析和架构设计
- [x] 技术选型
- [x] JSON Schema 协议定义
- [x] 文档编写（README, ARCHITECTURE, PROMPT_DESIGN, USER_GUIDE）

### Phase 2: 后端基础 ⏸️（暂缓）
> **注**: 由于采用"无外壳"架构，后端开发暂缓。Python 后端仅用于生成 JSON 文件，不需要 REST API 或 WebSocket 服务。

### Phase 3: 前端开发 ✅（已完成）

#### 3.1 核心层 ✅
- [x] Zustand 状态管理（analysisStore, visualizationStore）
- [x] 数据加载器（文件/URL，gzip支持）
- [x] 数据验证器（JSON Schema 验证）

#### 3.2 可视化层 ✅
- [x] CodeStructureGraph（Cytoscape.js）
- [x] LaunchButton + LaunchButtonList（嵌套按钮）
- [x] FlowchartViewer（D3.js 流程图）
- [x] SequenceViewer（D3.js 序列图）
- [x] StepByStepViewer（Monaco Editor）

#### 3.3 应用层 ✅
- [x] AppLayout（主布局）
- [x] ViewSwitcher（视图切换）
- [x] AnimationController（动画控制）
- [x] App（主应用整合）
- [x] 入口文件（main.tsx, index.html）

### Phase 4: 测试与优化 📋（待开始）
- [ ] 单元测试（Vitest）
- [ ] E2E 测试（Playwright）
- [ ] 性能优化
- [ ] 示例 JSON 数据

### Phase 5: 文档与发布 📋（待开始）
- [ ] 用户文档
- [ ] 开发者文档
- [ ] 部署指南

## 使用方式

### 快速开始

```bash
# 1. 安装依赖
cd frontend
pnpm install

# 2. 启动开发服务器
pnpm dev

# 3. 浏览器访问
# http://localhost:5173
```

### 使用流程

1. **获取分析数据**
   - 使用 AI（Claude、GPT-4等）分析项目
   - 按照 JSON Schema 规范生成分析结果
   - 保存为 `.json` 或 `.json.gz` 文件

2. **加载数据**
   - 方式1: 上传本地 JSON 文件
   - 方式2: 从 URL 加载远程文件

3. **可视化探索**
   - 切换不同视图模式
   - 点击启动按钮触发动画
   - 使用动画控制器控制播放

4. **导出结果**
   - 导出分析数据为 JSON 文件
   - 分享给团队成员

## 技术亮点

### 1. 智能委托策略
- 平台作为"指挥官"而非"解析器"
- AI 负责所有技术分析，平台负责可视化
- 技术栈完全无关，支持任何编程语言

### 2. 嵌套式行为启动
- 创新的多层级按钮系统
- 大按钮 → 小按钮 → 微按钮
- 每层独立启动，递归展开

### 3. 纯静态架构
- 无需后端服务器
- 部署简单（任何静态托管服务）
- 安全性高（无服务器攻击面）

### 4. 多维度可视化
- 结构、序列、流程、逐步执行
- 4种互补的分析视角
- 动画辅助理解

### 5. 性能优化
- Zustand 轻量级状态管理
- 虚拟化滚动（大列表）
- Canvas 渲染（高性能动画）
- gzip 压缩支持

## 性能指标

- **首次加载**: <2s（中型项目 500-2000 节点）
- **视图切换**: <300ms
- **动画帧率**: ≥30 FPS
- **文件加载**: 100MB 内 <5s
- **内存占用**: 中型项目 <500MB

## 浏览器兼容性

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- 不支持 IE

## 开发命令

```bash
# 安装依赖
pnpm install

# 开发模式
pnpm dev

# 构建生产版本
pnpm build

# 预览生产构建
pnpm preview

# 运行测试
pnpm test

# 类型检查
pnpm type-check

# 代码格式化
pnpm format

# 代码检查
pnpm lint
```

## 文件大小限制

- **JSON 文件**: 100MB
- **gzip 压缩文件**: 建议使用，可减少 70-80% 大小
- **节点数量**: 建议 <5000 节点（更大项目建议分模块分析）

## 未来计划

### 短期（1-2个月）
- [ ] 完善测试覆盖率
- [ ] 性能优化和基准测试
- [ ] 创建示例 JSON 数据集
- [ ] 编写详细使用文档

### 中期（3-6个月）
- [ ] Python 后端 JSON 生成工具
- [ ] AI Prompt 模板库
- [ ] VS Code 扩展集成
- [ ] 多项目对比功能

### 长期（6-12个月）
- [ ] 桌面应用（Tauri）
- [ ] 实时协作功能
- [ ] AI 辅助重构建议
- [ ] 插件生态系统

## Constitution 合规性

所有 6 项核心原则已满足：

- ✅ **I. AI 指挥驱动策略**: 通过 Prompt 模板指挥 AI 分析，平台不解析代码
- ✅ **II. 开放连接性**: 架构支持任何 AI 服务，技术栈无关
- ✅ **III. 智能分层**: Cytoscape.js 层级结构，行为驱动交互
- ✅ **IV. 行为嵌套**: 嵌套式启动按钮，大→小→微按钮递归结构
- ✅ **V. 并发可视化**: 序列图、Fork/Join 流程图支持并发分析
- ✅ **VI. 用户完全控制**: 动画控制器，逐步执行详细视图

## 重要说明

- 这是一个**前端可视化平台**，不包含代码分析引擎
- **AI 负责分析**，平台负责展示
- 需要符合 JSON Schema 规范的分析数据
- 建议配合 Claude、GPT-4 等 AI 工具使用
- 适合团队代码评审、架构分析、新人培训等场景

## 参考文档

- **README**: `specs/001-ai/README.md` - 项目概览
- **架构设计**: `specs/001-ai/docs/ARCHITECTURE.md` - 详细架构
- **Prompt 设计**: `specs/001-ai/docs/PROMPT_DESIGN.md` - AI 指令集设计
- **用户指南**: `specs/001-ai/docs/USER_GUIDE.md` - 使用指南
- **JSON Schema**: `specs/001-ai/contracts/analysis-schema-v1.0.0.json` - 数据协议

## License

MIT License
