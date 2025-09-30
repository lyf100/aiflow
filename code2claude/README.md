# Code2Claude

基于 code2flow 的增强代码分析工具，专为 AI 辅助开发设计。

**🎉 现已支持 MCP (Model Context Protocol) 服务器模式！**

## ✨ 特性

- 🗺️ **项目结构映射**: 自动生成项目的完整结构图和代码组织信息
- 🔍 **深度代码分析**: AST级别的代码分析，提取函数、类、依赖关系
- 🔥 **代码热点识别**: 识别高频修改、高复杂度、过大的文件
- 📊 **依赖关系可视化**: 生成交互式依赖图表(HTML/PNG/SVG)
- 🤖 **AI友好上下文**: 生成适合AI工具消费的结构化项目信息
- 📸 **项目快照对比**: 创建快照并对比不同版本的差异
- 🎯 **影响分析**: 分析修改文件的潜在影响范围
- 🔗 **函数调用链追踪**: 追踪函数的调用关系和依赖链
- ⚙️ **灵活配置**: 支持YAML配置文件定制分析行为
- 🎨 **彩色输出**: 支持彩色终端输出，提升可读性
- 🌐 **MCP 集成**: 作为 MCP 服务器与 Claude Code 等 AI 工具无缝集成

## 🚀 两种使用模式

### 模式 1: MCP 服务器模式 (推荐) ⚡

作为 MCP 服务器运行，直接在 Claude Code 中调用所有分析功能。

**优势**:
- ✅ 无需手动运行命令
- ✅ AI 可直接调用所有工具
- ✅ 实时交互式分析
- ✅ 自动化工作流程

**一键安装**:

**方式 1: npm 安装 (最简单)**
```bash
npm run install
```

**方式 2: Python 直接安装**
```bash
python install_mcp.py
```

**仅需 3 步**:
1. 运行安装脚本（自动安装依赖 + 配置 Claude Desktop）
2. 重启 Claude Desktop
3. 开始使用！

> 详细说明: [QUICKSTART.md](./QUICKSTART.md) | [MCP_SETUP.md](./MCP_SETUP.md)

### 模式 2: 传统 CLI 模式

作为命令行工具独立使用。

**优势**:
- ✅ 独立运行，无需额外配置
- ✅ 适合脚本和自动化
- ✅ 批量处理多个项目

**快速开始**: 继续阅读下方的安装和使用说明

## 📦 安装

### 从源码安装

```bash
git clone https://github.com/yourusername/code2claude.git
cd code2claude
pip install -e .
```

### 安装依赖

```bash
pip install -r requirements.txt
```

需要的依赖:
- `pyyaml>=6.0` - YAML配置文件支持
- `colorama>=0.4.6` - 彩色终端输出
- `mcp[cli]>=1.4.0` - MCP服务器支持 (可选，仅MCP模式需要)

## 🚀 快速开始 (CLI 模式)

### 1. 映射项目结构

```bash
code2claude structure
```

这将生成:
- `code2claude/maps/structure_map.json` - 项目结构数据
- `code2claude/maps/code_map.json` - 代码映射
- `code2claude/maps/interactive_map.html` - 交互式可视化地图

### 2. 生成依赖关系图

```bash
code2claude graph
```

生成多种格式的依赖关系图表。

### 3. 识别代码热点

```bash
code2claude hotspot
```

分析最近30天(可配置)的代码变更，识别:
- 频繁修改的文件
- 高复杂度的代码
- 过大的文件

### 4. 生成AI上下文

```bash
code2claude ai-context
```

生成适合AI工具使用的项目结构化信息。

## 📚 核心命令

### 结构和映射

- `code2claude structure` (别名: `map`, `/cc:map`, `/cc:structure`)
  - 映射项目结构和代码组织

- `code2claude refresh` (别名: `sync`, `/cc:sync`, `/cc:refresh`, `/cc:update`)
  - 刷新分析数据，同步最新变化

### 分析命令

- `code2claude ai-context` (别名: `context`, `/cc:context`, `/cc:ai-context`)
  - 生成AI友好的结构化上下文

- `code2claude graph` (别名: `/cc:graph`)
  - 生成依赖关系可视化图表

- `code2claude hotspot` (别名: `/cc:hotspot`)
  - 识别代码热点（复杂度、变更频率）

- `code2claude impact <file>` (别名: `/cc:impact`)
  - 分析修改文件的影响范围

- `code2claude trace <function>` (别名: `/cc:trace`)
  - 追踪函数调用链和依赖关系

### 版本控制

- `code2claude snapshot [name]` (别名: `/cc:snapshot`)
  - 创建项目结构快照

- `code2claude diff <snap1> <snap2>` (别名: `/cc:diff`)
  - 对比两个快照的差异

### 导出和帮助

- `code2claude export` (别名: `/cc:export`)
  - 导出分析数据（支持JSON/Markdown/HTML/CSV）

- `code2claude help [command]` (别名: `/cc:help`)
  - 显示帮助信息

- `code2claude workflow` (别名: `/cc:workflow`)
  - 显示推荐的工作流程

## ⚙️ 配置文件

在项目根目录创建 `.code2claude.yml` 或 `code2claude.yml`:

```yaml
# 项目设置
project:
  name: "my-project"
  language: "py"  # py, js, ts, java, go, rb, php
  exclude:
    - "*.pyc"
    - "__pycache__"
    - ".git"
    - "node_modules"
    - "venv"

# 分析设置
analysis:
  depth: 3  # 分析深度 (1-5)
  include_comments: true
  include_tests: true
  complexity:
    warning: 10
    error: 20

# 热点分析
hotspot:
  days: 30  # 分析天数
  frequency_threshold: 5
  size_threshold: 50  # KB

# 输出设置
output:
  format: "json"  # json, markdown, html, csv
  colorful: true  # 彩色输出
  verbose: false
  show_progress: true

# 图表设置
graph:
  types:
    - "call"
    - "dependency"
  format: "html"  # png, svg, html
  max_nodes: 100

# 命令默认选项
commands:
  structure:
    interactive_map: true
  refresh:
    require_confirmation: true
  export:
    format: "json"
```

## 🔧 命令行选项

### 全局选项

- `-p, --project-path <path>` - 指定项目路径 (默认: 当前目录)
- `--format <format>` - 输出格式 (json/markdown/html/csv)
- `--language <lang>` - 指定编程语言 (py/js/rb/php)
- `--depth <n>` - 分析深度 (默认: 3)
- `--days <n>` - 热点分析天数 (默认: 30)
- `-v, --verbose` - 详细输出模式
- `--force` - 跳过确认提示

### 使用示例

```bash
# 指定项目路径
code2claude structure -p /path/to/project

# 导出为HTML格式
code2claude export --format html

# 分析最近60天的热点
code2claude hotspot --days 60

# 强制刷新（跳过确认）
code2claude refresh --force

# 详细输出模式
code2claude structure -v
```

## 📖 推荐工作流程

### 标准分析流程

1. **初始化分析**
   ```bash
   code2claude structure
   ```
   生成项目结构映射，创建基础数据

2. **生成可视化**
   ```bash
   code2claude graph
   ```
   创建依赖关系图，直观理解项目

3. **识别问题区域**
   ```bash
   code2claude hotspot
   ```
   找出需要关注的代码热点

4. **深入分析**
   ```bash
   code2claude impact core/analyzer.py
   code2claude trace main
   ```
   分析修改影响和追踪调用链

5. **生成AI上下文**
   ```bash
   code2claude ai-context
   ```
   为AI工具生成结构化项目信息

### 持续维护流程

**代码修改后:**
```bash
code2claude refresh
code2claude hotspot
```

**重大重构前:**
```bash
code2claude snapshot pre-refactor
# ... 进行重构 ...
code2claude snapshot post-refactor
code2claude diff pre-refactor post-refactor
```

### 特定场景

**新接手项目:**
```bash
structure → graph → ai-context → hotspot
```

**重构规划:**
```bash
hotspot → impact <files> → snapshot
```

**代码审查:**
```bash
trace <function> → impact <file> → graph
```

## 📁 输出目录结构

```
your-project/
├── code2claude/
│   ├── analysis.json              # 项目分析数据
│   ├── context.json               # AI上下文
│   ├── maps/
│   │   ├── structure_map.json     # 结构映射
│   │   ├── code_map.json          # 代码映射
│   │   └── interactive_map.html   # 交互式地图
│   ├── graphs/
│   │   ├── call_graph.html        # 调用关系图
│   │   └── dependency_graph.html  # 依赖关系图
│   └── tracking/
│       ├── hotspots.json          # 热点分析
│       ├── impact_*.json          # 影响分析
│       └── trace_*.json           # 调用链追踪
└── .code2claude.yml               # 配置文件(可选)
```

## 💡 提示

- **大型项目首次分析** 可能需要几分钟，请耐心等待
- **建议定期执行** `refresh` 命令保持数据最新
- **善用快照功能** (`snapshot` 和 `diff`) 追踪项目演进
- **配置文件** 可以简化重复的命令行参数
- **彩色输出** 在配置文件中可以关闭: `output.colorful: false`

## 🐛 常见问题

### 配置文件不生效?

确保配置文件名称正确:
- `.code2claude.yml` (推荐，隐藏文件)
- `.code2claude.yaml`
- `code2claude.yml`
- `code2claude.yaml`

### Git相关功能不工作?

确保项目在Git仓库中:
```bash
git init  # 如果还没有初始化Git
```

### 彩色输出不显示?

检查:
1. 是否安装了colorama: `pip install colorama`
2. 终端是否支持ANSI色彩
3. 配置文件中 `output.colorful` 是否为 `true`

## 📄 许可证

[MIT License](LICENSE)

## 🤝 贡献

欢迎提交Issue和Pull Request!

## 📮 联系方式

- GitHub: [yourusername/code2claude](https://github.com/yourusername/code2claude)
- Email: your.email@example.com

---

**Code2Claude** - 让AI更好地理解你的代码!