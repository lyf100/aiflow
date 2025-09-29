# Code2Claude - 增强代码分析系统

基于 code2flow 的智能代码分析和项目映射系统，为 Claude 和 SuperClaude 提供深度项目理解能力。

## 🎯 项目简介

Code2Claude 是一个专业的代码分析工具，通过 AST 分析能力提供项目结构映射、依赖关系分析、变更跟踪和影响评估等功能。

## ✨ 核心特性

- **🔍 深度代码分析** - 基于 AST 的函数级代码分析
- **🗺️ 项目映射** - 完整的项目结构和代码地图
- **📊 依赖分析** - 调用图和依赖关系可视化
- **🔥 热点识别** - 自动识别复杂度和变更热点
- **📈 变更跟踪** - Git 历史分析和项目快照
- **🎯 影响分析** - 文件修改的影响范围评估
- **📤 多格式导出** - JSON/HTML/Markdown/CSV 导出

## 🚀 支持的语言

- Python (.py)
- JavaScript (.js)
- Ruby (.rb)
- PHP (.php)
- TypeScript (.ts) - 基础支持
- Dart (.dart) - 基础支持
- Java (.java) - 基础支持

## 📦 安装和使用

### 快速安装

```bash
# 克隆仓库
git clone https://github.com/lyf100/code2claude.git
cd code2claude

# 运行安装脚本
python install_code2claude.py
```

### 基础使用

```bash
# 映射项目结构
python -m code2claude /cc:map

# 生成依赖关系图
python -m code2claude /cc:graph

# 识别代码热点
python -m code2claude /cc:hotspot --days 30

# 分析文件影响
python -m code2claude /cc:impact src/main.py

# 追踪函数调用
python -m code2claude /cc:trace main_function

# 导出分析报告
python -m code2claude /cc:export --format html
```

## 📋 完整命令列表

### 项目分析命令
- `/cc:map` - 映射项目结构，生成代码地图
- `/cc:sync` - 同步项目变化到分析框架
- `/cc:context` - 生成给 Claude 的结构化上下文

### 可视化命令
- `/cc:graph` - 查看依赖关系图和调用图
- `/cc:hotspot` - 识别代码热点（复杂度、变更频率）

### 影响分析命令
- `/cc:impact <file>` - 影响分析：修改某文件会影响哪些模块
- `/cc:trace <function>` - 追踪函数调用链

### 版本控制命令
- `/cc:snapshot [name]` - 创建项目结构快照
- `/cc:diff <snap1> <snap2>` - 对比两个快照的结构变化

### 导出命令
- `/cc:export --format <json|markdown|html|csv>` - 导出分析数据

## 📁 输出结构

```
/项目根目录/code2claude/
├── core/                    # 核心分析模块
├── maps/                    # 项目结构地图
├── graphs/                  # 依赖关系图
├── tracking/                # 变更跟踪数据
│   └── snapshots/          # 项目快照
└── exports/                # 导出数据
```

## 🔧 高级用法

### 参数选项

```bash
# 指定项目路径
python -m code2claude /cc:map -p /path/to/project

# 详细输出
python -m code2claude /cc:hotspot --verbose

# 指定分析语言
python -m code2claude /cc:graph --language py

# 自定义时间范围
python -m code2claude /cc:hotspot --days 60
```

### 批量处理

```bash
# 一键完整分析
python -m code2claude /cc:sync && \
python -m code2claude /cc:map && \
python -m code2claude /cc:graph && \
python -m code2claude /cc:export --format html
```

## 🏗️ 架构设计

### 核心模块

- **CodeAnalyzer** - 基于 code2flow 的代码分析引擎
- **ProjectMapper** - 项目结构映射和地图生成
- **DependencyGrapher** - 依赖关系图和可视化
- **ChangeTracker** - 变更跟踪和热点识别
- **DataExporter** - 多格式数据导出

### 技术栈

- **分析引擎**: code2flow AST 分析
- **可视化**: HTML/D3.js 交互式图表
- **数据处理**: Python 标准库
- **版本控制**: Git 集成
- **导出格式**: JSON, HTML, Markdown, CSV

## 🤝 贡献指南

欢迎贡献代码和建议！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目基于 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [code2flow](https://github.com/scottrogowski/code2flow) - 核心 AST 分析引擎
- [SuperClaude](https://github.com/anthropics/claude-code) - 集成框架
- 所有贡献者和用户的支持

## 📞 联系方式

- 项目地址: https://github.com/lyf100/code2claude
- 问题反馈: https://github.com/lyf100/code2claude/issues

---

**让代码分析变得简单而强大！** 🚀
