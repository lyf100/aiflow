# AIFlow Examples

示例 JSON 分析数据和使用案例。

## 目录结构

```
examples/
├── simple-project/          # 简单项目示例
│   └── analysis.json        # 小型项目的分析数据
│
├── medium-project/          # 中型项目示例
│   └── analysis.json        # 中型项目的分析数据
│
└── README.md               # 本文件
```

## 如何使用示例数据

### 1. 在前端加载示例

**方式 1: 本地文件**
```bash
cd frontend
pnpm dev
```
在浏览器中点击"加载数据"，选择 `examples/simple-project/analysis.json`

**方式 2: URL 加载**
如果示例数据部署到网络上，可以通过 URL 直接加载。

### 2. 生成自己的分析数据

使用分析器工具分析你的项目：

```bash
cd analyzer
python analyze_project.py /path/to/your/project -o output.json
```

然后在前端加载生成的 `output.json` 文件。

## 示例项目说明

### simple-project
- **节点数**: ~20 个
- **语言**: Python
- **特点**: 简单的模块结构，适合快速了解 AIFlow 功能
- **用途**: 新手入门，快速体验

### medium-project
- **节点数**: ~200 个
- **语言**: Java + Kotlin
- **特点**: 多模块架构，包含复杂依赖关系
- **用途**: 测试可视化性能，展示完整功能

## 创建自定义示例

如果你想创建自己的示例数据：

1. 使用分析器生成 JSON 数据
2. 验证 JSON 符合 Schema 规范
3. 在前端测试加载和可视化
4. 添加到 examples 目录

## JSON Schema 规范

所有示例数据必须符合 `specs/001-ai/contracts/analysis-schema-v1.0.0.json` 中定义的规范。

关键要求：
- `metadata.project_id`: UUID v4 格式
- `metadata.timestamp`: ISO 8601 格式
- `metadata.protocol_version`: 语义化版本号
- `code_structure.nodes`: 所有节点必须有唯一的 UUID
- `code_structure.edges`: 边的 source/target 必须引用存在的节点

## 故障排除

### 示例加载失败

1. **JSON 格式错误**
   - 使用 JSON 验证工具检查格式
   - 确保所有引号和括号匹配

2. **Schema 不符**
   - 检查 protocol_version 是否正确
   - 验证所有必需字段是否存在

3. **文件过大**
   - 前端支持最大 100MB 文件
   - 大文件建议使用 gzip 压缩

## 贡献示例

欢迎贡献新的示例数据！

要求：
- 真实项目或有代表性的示例项目
- JSON 数据符合最新 Schema 规范
- 包含完整的可视化元素（节点、边、按钮、轨迹）
- 添加相应的说明文档
