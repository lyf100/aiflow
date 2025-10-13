# AIFlow Frontend

AIFlow 前端可视化平台 - 基于 React + TypeScript 的现代化代码分析可视化工具。

## 技术栈

- **框架**: React 18.3 + TypeScript 5.x
- **状态管理**: Zustand 4.x
- **可视化**:
  - Cytoscape.js 3.x - 代码结构图
  - D3.js 7.x - 执行轨迹（流程图、序列图）
  - Monaco Editor - 代码逐步执行
- **构建工具**: Vite 5.x
- **包管理**: pnpm

## 快速开始

### 安装依赖

```bash
# 使用 pnpm（推荐）
pnpm install

# 或使用 npm
npm install
```

### 开发模式

```bash
pnpm dev
```

浏览器自动打开 http://localhost:5173

### 构建生产版本

```bash
pnpm build
```

构建输出在 `dist/` 目录

### 预览生产构建

```bash
pnpm preview
```

## 项目结构

```
frontend/
├── src/
│   ├── components/          # React 组件
│   │   ├── Layout/          # 布局组件
│   │   ├── Controls/        # 控制组件
│   │   ├── CodeStructureGraph/  # 代码结构图
│   │   ├── LaunchButton/    # 嵌套启动按钮
│   │   └── ExecutionTrace/  # 执行轨迹可视化
│   │
│   ├── stores/              # Zustand 状态管理
│   │   ├── analysisStore.ts      # 分析数据
│   │   └── visualizationStore.ts # UI 状态
│   │
│   ├── utils/               # 工具函数
│   │   ├── dataLoader.ts    # JSON 加载器
│   │   └── validators.ts    # 数据验证
│   │
│   ├── types/               # TypeScript 类型
│   │   └── protocol.ts      # 协议类型定义
│   │
│   ├── App.tsx              # 主应用
│   ├── main.tsx             # 入口文件
│   ├── App.css              # 主样式
│   └── index.css            # 全局样式
│
├── index.html               # HTML 模板
├── package.json             # 项目依赖
├── vite.config.ts           # Vite 配置
└── tsconfig.json            # TypeScript 配置
```

## 核心功能

### 1. 代码结构图 (Structure View)
- Cytoscape.js 实现的交互式图形可视化
- 支持缩放、拖拽、节点高亮
- 多种布局算法（dagre, cose, circle, grid）
- 展开/折叠功能

### 2. 嵌套启动按钮 (Launch Buttons)
- 递归嵌套结构（大→小→微按钮）
- 每个按钮可独立触发执行动画
- AI 置信度显示
- 元数据支持（执行时间、副作用等）

### 3. 执行轨迹可视化 (Execution Trace)
- **流程图** (Flowchart): D3.js 实现的控制流可视化
- **序列图** (Sequence): 组件间消息传递可视化
- **逐步执行** (Step-by-Step): Monaco Editor 代码执行展示

### 4. 动画控制
- 播放/暂停/停止
- 步进控制（前进/后退）
- 速度调节（0.25x - 4x）
- 进度条拖动

### 5. 数据加载
- 本地文件上传
- URL 远程加载
- gzip 压缩文件支持
- 100MB 文件大小限制

## 使用方式

### 1. 加载分析数据

#### 方式 1: 上传本地文件
1. 点击"加载数据"按钮
2. 选择 `.json` 或 `.json.gz` 文件
3. 等待加载完成

#### 方式 2: 从 URL 加载
1. 点击"从 URL 加载"
2. 输入 JSON 文件的 URL
3. 等待加载完成

### 2. 探索可视化

#### 代码结构图模式
- 使用鼠标滚轮缩放
- 拖拽查看不同区域
- 点击节点查看详情
- 侧边栏显示嵌套启动按钮

#### 序列图/流程图模式
- 点击启动按钮触发动画
- 使用动画控制器控制播放
- 步进查看每个执行步骤

#### 逐步执行模式
- 查看代码逐行执行过程
- 查看变量状态变化
- 查看调用栈信息

### 3. 导出数据

点击"导出数据"按钮，将当前分析数据保存为 JSON 文件。

## 开发命令

```bash
# 开发模式
pnpm dev

# 构建生产版本
pnpm build

# 预览生产构建
pnpm preview

# 类型检查
pnpm type-check

# 代码检查
pnpm lint

# 代码格式化
pnpm format

# 运行测试
pnpm test
```

## 浏览器兼容性

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- 不支持 IE

## 性能指标

- **首次加载**: <2s（中型项目 500-2000 节点）
- **视图切换**: <300ms
- **动画帧率**: ≥30 FPS
- **文件加载**: 100MB 内 <5s
- **内存占用**: 中型项目 <500MB

## 故障排除

### 加载文件失败
- 检查文件格式是否为有效 JSON
- 检查文件大小是否超过 100MB
- 检查文件是否符合 JSON Schema 规范

### 可视化渲染慢
- 减小节点数量（建议 <5000 节点）
- 关闭不必要的动画
- 使用更简单的布局算法

### 内存不足
- 关闭其他标签页
- 分模块分析大型项目
- 减小分析数据的深度和广度

## 相关文档

- **项目概览**: `../README.md`
- **架构设计**: `../docs/ARCHITECTURE.md`
- **用户指南**: `../docs/USER_GUIDE.md`
- **Prompt 设计**: `../docs/PROMPT_DESIGN.md`
- **JSON Schema**: `../specs/001-ai/contracts/analysis-schema-v1.0.0.json`

## License

MIT License
