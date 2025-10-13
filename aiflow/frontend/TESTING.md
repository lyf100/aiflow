# AIFlow Frontend Testing Guide

## ✅ 当前状态

### 已完成的组件

1. **CodeGraph 组件** (`src/components/CodeGraph/`)
   - 基于 Cytoscape.js 的交互式代码结构图
   - Dagre 布局算法（TB方向，层次分明）
   - 节点类型样式化（class, function, system, module, component）
   - 边类型样式化（inherits, implements, calls, depends, aggregates）
   - 点击节点高亮功能

2. **LaunchButtons 组件** (`src/components/LaunchButtons/`)
   - 嵌套可折叠按钮列表
   - Macro/Micro 类型视觉区分
   - System/Module/Component/Function 层级标识
   - AI 置信度和预计时长显示
   - 递归渲染子按钮

3. **主应用 App.tsx**
   - 自动加载 `/analysis.json`
   - 视图切换（代码结构 / 执行动画）
   - 加载状态、错误状态、欢迎页面
   - 统计信息面板
   - 响应式布局

4. **状态管理** (`src/stores/analysisStore.ts`)
   - Zustand 状态管理
   - LocalStorage 持久化
   - 数据加载/清除接口

5. **类型定义** (`src/types/protocol.ts`)
   - 完整的 TypeScript 类型
   - 符合 AIFlow JSON Schema v1.0.0

## 🚀 如何测试

### 1. 启动开发服务器

```bash
cd D:/dart/flutter/aiflow/frontend
npm run dev
```

服务器地址: **http://localhost:5173/**

### 2. 验证分析数据

确认 `public/analysis.json` 存在并有效:

```bash
ls -lh public/analysis.json
# 应显示: 95K Oct 12 16:19 public/analysis.json
```

### 3. 浏览器测试清单

#### ✅ 基础功能
- [ ] 页面加载成功，无控制台错误
- [ ] 自动加载分析数据（约95KB）
- [ ] 显示项目名称: "NewPipe-dev"
- [ ] 显示协议版本: "1.0.0"
- [ ] 显示分析时间戳

#### ✅ 统计信息面板
- [ ] 文件数: 475
- [ ] 节点数: 180
- [ ] 关系数: 179
- [ ] 按钮数: 9

#### ✅ 代码结构图 (CodeGraph)
- [ ] 图谱正确渲染（Dagre 布局）
- [ ] 节点可见且有标签
- [ ] 边连接正确显示
- [ ] 节点可拖拽
- [ ] 鼠标滚轮缩放
- [ ] 点击节点高亮
- [ ] 悬停节点显示详情

#### ✅ 启动按钮 (LaunchButtons)
- [ ] 按钮列表显示（9个按钮）
- [ ] 按钮类型图标显示
- [ ] 按钮层级标签显示
- [ ] 折叠/展开功能正常
- [ ] 点击按钮触发事件
- [ ] 描述和元数据显示

#### ✅ 视图切换
- [ ] "代码结构"按钮激活状态
- [ ] "执行动画"按钮可点击
- [ ] 切换到执行动画显示占位符
- [ ] 占位符显示开发进度信息

#### ✅ 响应式设计
- [ ] 桌面视图正常（>1024px）
- [ ] 平板视图正常（768-1024px）
- [ ] 移动视图正常（<768px）
- [ ] 侧边栏在移动端折叠

## 🐛 已知问题

### 待实现功能

1. **执行动画视图** (占位符状态)
   - D3.js 流程图查看器
   - D3.js 序列图查看器
   - Monaco Editor 逐步执行
   - 动画播放控制器

2. **深度分析引擎** (未来工作)
   - 5阶段 AI 分析流水线
   - 语义理解和推理
   - 高质量数据生成

### 性能注意事项

- **当前**: 基础静态分析（10秒 - 10分钟）
- **未来**: AI 深度分析（1-12小时）
- **图谱渲染**: 180节点 + 179边 = 良好性能
- **大型项目**: >1000节点时考虑虚拟化

## 📊 测试结果模板

```markdown
## 测试日期: YYYY-MM-DD

### 环境
- 浏览器: Chrome/Firefox/Safari
- 版本: X.X.X
- 操作系统: Windows/macOS/Linux

### 测试结果
| 功能 | 状态 | 备注 |
|-----|------|------|
| 数据加载 | ✅/❌ | |
| 代码结构图 | ✅/❌ | |
| 启动按钮 | ✅/❌ | |
| 视图切换 | ✅/❌ | |
| 响应式设计 | ✅/❌ | |

### 发现的问题
1.
2.
3.

### 改进建议
1.
2.
3.
```

## 🔧 开发命令

```bash
# 安装依赖
npm install

# 开发服务器
npm run dev

# 生产构建
npm run build

# 预览生产构建
npm run preview

# TypeScript 类型检查
npx tsc --noEmit

# 代码格式化
npx prettier --write src/
```

## 📁 项目结构

```
frontend/
├── public/
│   └── analysis.json          # 95KB 分析数据
├── src/
│   ├── components/
│   │   ├── CodeGraph/         # Cytoscape.js 图谱
│   │   └── LaunchButtons/     # 启动按钮
│   ├── stores/
│   │   └── analysisStore.ts   # Zustand 状态
│   ├── types/
│   │   └── protocol.ts        # TypeScript 类型
│   ├── App.tsx                # 主应用
│   ├── App.css                # 主样式
│   ├── index.css              # 全局样式
│   └── main.tsx               # 入口文件
├── package.json
├── tsconfig.json
├── vite.config.ts
└── TESTING.md                 # 本文档
```

## 🎯 下一步工作

1. **测试当前前端** ← 当前阶段
2. **实现执行动画视图** (D3.js + Monaco Editor)
3. **优化大型项目性能** (虚拟化 + 懒加载)
4. **实现 AI 深度分析引擎** (5阶段流水线)
