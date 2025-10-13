# AIFlow - AI 分析可视化平台

<div align="center">

🚀 **无外壳 MCP Tools** · 🎯 **嵌套式行为启动** · 🌐 **智能委托策略**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-18.3-blue)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Python-3.9+-green)](https://www.python.org/)

</div>

---

## 📖 简介

**AIFlow** 是一个创新的代码分析和可视化平台，核心理念是"平台不解析代码，AI 来分析"。通过 Prompt 模板指挥 AI（Claude、GPT-4、Gemini 等）进行代码分析，生成标准 JSON 数据，然后在纯静态前端进行可视化展示。

### 核心特性

- ✅ **无外壳 MCP Tools** - 无需后端服务器，纯静态前端
- ✅ **智能委托策略** - AI 负责分析，平台负责可视化
- ✅ **技术栈无关** - 支持任何编程语言（Java, Kotlin, Python, JavaScript, TypeScript, Go, Rust 等）
- ✅ **嵌套式行为启动** - 大按钮 → 小按钮 → 微按钮的递归结构
- ✅ **多维度可视化** - 代码结构图、序列图、流程图、逐步执行

---

## 🏗️ 项目结构

```
aiflow/
├── frontend/              # 前端可视化平台（React + TypeScript）
│   ├── src/
│   │   ├── components/    # React 组件
│   │   ├── stores/        # Zustand 状态管理
│   │   ├── utils/         # 工具函数
│   │   └── types/         # TypeScript 类型
│   ├── package.json
│   └── vite.config.ts
│
├── analyzer/              # Python 代码分析器
│   └── analyze_project.py # 项目分析脚本
│
├── docs/                  # 文档
│   ├── ARCHITECTURE.md    # 架构设计
│   ├── PROMPT_DESIGN.md   # Prompt 设计指南
│   └── USER_GUIDE.md      # 用户指南
│
├── specs/                 # 规范文档
│   └── 001-ai/
│       ├── contracts/     # JSON Schema
│       └── README.md      # 功能规范
│
├── examples/              # 示例数据
│   └── README.md
│
└── README.md             # 本文件
```

---

## 🚀 快速开始

### 前置要求

- **Node.js** 18+ 和 **pnpm** 8+（前端开发）
- **Python** 3.9+（代码分析）
- 现代浏览器（Chrome 90+, Firefox 88+, Safari 14+, Edge 90+）

### 安装与运行

#### 1. 启动前端可视化平台

```bash
# 进入前端目录
cd frontend

# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev
```

浏览器自动打开 http://localhost:5173

#### 2. 使用分析器生成数据

```bash
# 进入分析器目录
cd analyzer

# 分析项目
python analyze_project.py /path/to/your/project -o analysis.json

# 示例：分析 NewPipe 项目
python analyze_project.py ../NewPipe-dev -o newpipe-analysis.json
```

#### 3. 在前端加载分析数据

1. 打开浏览器中的 AIFlow 前端
2. 点击"加载数据"按钮
3. 选择生成的 `analysis.json` 文件
4. 开始探索可视化！

---

## 🎯 核心功能

### 1. 代码结构图（Structure View）

<img src="https://via.placeholder.com/800x400?text=Code+Structure+Graph" alt="代码结构图" width="100%">

- **技术**: Cytoscape.js + Dagre 布局
- **功能**:
  - 展示代码节点（system, module, class, function）和依赖关系
  - 支持缩放、拖拽、节点高亮、展开/折叠
  - 多种布局算法（dagre, cose, circle, grid）
- **侧边栏**: 嵌套启动按钮列表

### 2. 嵌套启动按钮（Launch Buttons）

<img src="https://via.placeholder.com/300x500?text=Nested+Launch+Buttons" alt="嵌套按钮" width="300">

**创新的多层级按钮系统**：

```
系统级大按钮 (System Macro)
  ├─ 模块级大按钮 (Module Macro)
  │   ├─ 组件级小按钮 (Component Micro)
  │   │   ├─ 函数级微按钮 (Function Micro)
  │   │   └─ 函数级微按钮
  │   └─ 组件级小按钮
  └─ 模块级大按钮
```

- 每个按钮可独立启动，触发对应层级的执行动画
- AI 置信度显示
- 元数据支持（执行时间、副作用等）

### 3. 执行轨迹可视化（Execution Trace）

#### 流程图（Flowchart View）
- **技术**: D3.js
- **功能**: 展示执行流程和控制流
- **支持**: fork（并发分叉）和 join（并发汇合）节点

#### 序列图（Sequence View）
- **技术**: D3.js
- **功能**: 展示组件间的消息传递和方法调用
- **支持**: 不同消息类型（call, return, async, create, destroy）

#### 逐步执行（Step-by-Step View）
- **技术**: Monaco Editor
- **功能**: 逐行展示代码执行过程
- **支持**: 变量状态展示、调用栈展示

### 4. 动画控制器

- ▶️ 播放 / ⏸ 暂停 / ⏹ 停止
- ⏮ 后退 / ⏭ 前进（步进控制）
- 🎚️ 速度调节（0.25x - 4x）
- 📊 进度条拖动

---

## 📊 数据协议

AIFlow 使用标准的 JSON Schema v1.0.0 协议，定义了 AI 分析结果和前端可视化之间的数据格式。

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
}
```

详细协议规范请查看 `specs/001-ai/contracts/analysis-schema-v1.0.0.json`

---

## 🎨 可视化模式

| 模式 | 技术栈 | 主要功能 | 适用场景 |
|------|--------|---------|---------|
| **代码结构图** | Cytoscape.js | 节点关系、依赖分析 | 架构理解、依赖分析 |
| **序列图** | D3.js | 组件交互、消息传递 | 时序分析、交互理解 |
| **流程图** | D3.js | 控制流、并发流 | 执行流程、并发分析 |
| **逐步执行** | Monaco Editor | 代码执行、变量状态 | 调试、学习理解 |

---

## 🛠️ 分析器使用

### 基本用法

```bash
python analyzer/analyze_project.py <项目路径> [选项]
```

### 选项

- `-o, --output <文件>` - 输出文件路径（默认：项目名-analysis.json）
- `-n, --name <名称>` - 项目名称（默认：目录名）

### 示例

```bash
# 分析当前目录项目
python analyze_project.py . -o output.json

# 分析指定项目并命名
python analyze_project.py /path/to/project -n "MyProject" -o myproject.json

# 分析 NewPipe 项目
python analyze_project.py ../NewPipe-dev -o newpipe-analysis.json
```

### 支持的项目类型

- ✅ Java (Maven, Gradle)
- ✅ Kotlin (Gradle)
- ✅ Python (pip, poetry)
- ✅ JavaScript/TypeScript (Node.js, npm, pnpm)
- ✅ Go (go mod)
- ✅ Rust (Cargo)

---

## 📚 文档

- **[架构设计](docs/ARCHITECTURE.md)** - 详细的系统架构和设计决策
- **[Prompt 设计指南](docs/PROMPT_DESIGN.md)** - AI Prompt 模板设计
- **[用户指南](docs/USER_GUIDE.md)** - 完整的使用指南
- **[功能规范](specs/001-ai/README.md)** - 功能需求和规划
- **[前端 README](frontend/README.md)** - 前端开发文档

---

## 🔧 开发

### 前端开发

```bash
cd frontend

# 安装依赖
pnpm install

# 开发模式
pnpm dev

# 构建生产版本
pnpm build

# 类型检查
pnpm type-check

# 代码检查
pnpm lint

# 代码格式化
pnpm format
```

### 分析器开发

```bash
cd analyzer

# 运行分析器
python analyze_project.py <项目路径>

# 测试分析器
python -m pytest tests/
```

---

## 🎯 使用场景

- 📖 **代码学习** - 新人快速理解项目架构
- 🔍 **代码审查** - 可视化展示代码结构和依赖关系
- 🏗️ **架构分析** - 分析系统架构和模块划分
- 📊 **技术债务** - 识别复杂依赖和代码异味
- 🎓 **教学演示** - 可视化演示代码执行过程

---

## 🌟 技术亮点

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
- 4 种互补的分析视角
- 动画辅助理解

### 5. 性能优化
- Zustand 轻量级状态管理
- 虚拟化滚动（大列表）
- Canvas 渲染（高性能动画）
- gzip 压缩支持

---

## 📈 性能指标

- **首次加载**: <2s（中型项目 500-2000 节点）
- **视图切换**: <300ms
- **动画帧率**: ≥30 FPS
- **文件加载**: 100MB 内 <5s
- **内存占用**: 中型项目 <500MB

---

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

---

## 🙏 致谢

感谢以下开源项目：

- [React](https://reactjs.org/) - UI 框架
- [Zustand](https://github.com/pmndrs/zustand) - 状态管理
- [Cytoscape.js](https://js.cytoscape.org/) - 图形可视化
- [D3.js](https://d3js.org/) - 数据可视化
- [Monaco Editor](https://microsoft.github.io/monaco-editor/) - 代码编辑器
- [Vite](https://vitejs.dev/) - 构建工具

---

<div align="center">

**Made with ❤️ by AIFlow Team**

[📖 文档](docs/) · [🐛 报告问题](../../issues) · [💡 功能建议](../../issues)

</div>
