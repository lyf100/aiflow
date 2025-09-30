# Code2Claude MCP 服务器配置指南

## 📦 安装步骤

### 1. 安装依赖

```bash
cd code2claude
pip install -r requirements.txt
```

这将安装：
- `pyyaml>=6.0` - YAML配置支持
- `colorama>=0.4.6` - 彩色终端输出
- `mcp[cli]>=1.4.0` - MCP SDK

### 2. 配置 Claude Desktop

编辑 Claude Desktop 配置文件：

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

添加以下配置：

```json
{
  "mcpServers": {
    "code2claude": {
      "command": "python",
      "args": [
        "-m",
        "code2claude.mcp_server"
      ],
      "env": {},
      "description": "Code2Claude - AI-powered code analysis and project mapping"
    }
  }
}
```

**注意**: 如果配置文件中已有其他 MCP 服务器，将 `code2claude` 条目添加到 `mcpServers` 对象中。

### 3. 重启 Claude Desktop

配置完成后，重启 Claude Desktop 使配置生效。

## 🔧 验证安装

在 Claude Code 中，MCP 服务器启动后会自动加载。你可以通过以下方式验证：

1. 打开 Claude Code
2. 检查是否有 "code2claude" 相关的工具可用
3. 尝试调用工具测试连接

## 🚀 可用工具

Code2Claude MCP 服务器提供以下 10 个工具：

### 1. analyze_project
**功能**: 分析项目代码结构
**参数**:
- `project_path` (必需): 项目根目录路径
- `languages` (可选): 语言列表，如 `["py", "js"]`

**返回**: 代码分析结果，包括语言分析、项目结构、依赖关系、热点和指标

**示例**:
```
请使用 analyze_project 工具分析 /path/to/project
```

### 2. map_project_structure
**功能**: 生成项目结构映射
**参数**:
- `project_path` (必需): 项目根目录路径

**返回**: 项目结构映射，包括元数据、统计、目录树、文件索引和模式

**示例**:
```
请使用 map_project_structure 工具映射 /path/to/project 的结构
```

### 3. generate_dependency_graph
**功能**: 生成依赖关系图
**参数**:
- `project_path` (必需): 项目根目录路径
- `graph_type` (可选): 图类型，默认 "module"，可选 "class", "function"

**返回**: 依赖图文件路径

**示例**:
```
请使用 generate_dependency_graph 工具为 /path/to/project 生成模块依赖图
```

### 4. identify_code_hotspots
**功能**: 识别代码热点
**参数**:
- `project_path` (必需): 项目根目录路径

**返回**: 热点列表（Git高频修改、高复杂度、大文件）

**示例**:
```
请使用 identify_code_hotspots 工具识别 /path/to/project 的代码热点
```

### 5. analyze_file_impact
**功能**: 分析文件修改影响
**参数**:
- `project_path` (必需): 项目根目录路径
- `file_path` (必需): 文件相对路径

**返回**: 影响分析（依赖、影响范围、影响级别）

**示例**:
```
请使用 analyze_file_impact 工具分析修改 src/main.py 的影响
```

### 6. trace_function_calls
**功能**: 追踪函数调用链
**参数**:
- `project_path` (必需): 项目根目录路径
- `function_name` (必需): 函数名
- `file_path` (可选): 限制搜索范围的文件路径

**返回**: 函数定义位置、调用者列表、调用链

**示例**:
```
请使用 trace_function_calls 工具追踪 process_data 函数的调用链
```

### 7. create_project_snapshot
**功能**: 创建项目快照
**参数**:
- `project_path` (必需): 项目根目录路径
- `snapshot_name` (可选): 快照名称，默认时间戳

**返回**: 快照文件路径

**示例**:
```
请使用 create_project_snapshot 工具为 /path/to/project 创建快照
```

### 8. compare_snapshots
**功能**: 比较两个快照
**参数**:
- `project_path` (必需): 项目根目录路径
- `snapshot1` (必需): 第一个快照名称
- `snapshot2` (必需): 第二个快照名称

**返回**: 快照差异（新增、删除、修改文件及统计）

**示例**:
```
请使用 compare_snapshots 工具比较快照 v1.0 和 v2.0
```

### 9. export_analysis_data
**功能**: 导出分析数据
**参数**:
- `project_path` (必需): 项目根目录路径
- `format` (可选): 格式，默认 "json"，可选 "markdown", "html", "csv"
- `output_path` (可选): 输出路径

**返回**: 导出文件路径列表

**示例**:
```
请使用 export_analysis_data 工具以 markdown 格式导出分析数据
```

## 🎯 使用场景示例

### 场景 1: 新项目代码审查
```
我需要了解这个新项目的结构和代码质量。请：
1. 使用 analyze_project 工具分析项目
2. 使用 identify_code_hotspots 工具找出潜在问题
3. 使用 map_project_structure 工具了解项目组织
```

### 场景 2: 重构前影响评估
```
我想重构 src/utils/database.py 文件，请：
1. 使用 analyze_file_impact 工具评估影响范围
2. 使用 trace_function_calls 工具追踪关键函数的调用链
3. 使用 create_project_snapshot 工具创建重构前快照
```

### 场景 3: 依赖关系分析
```
这个项目的模块依赖关系很复杂，请：
1. 使用 generate_dependency_graph 工具生成模块依赖图
2. 使用 analyze_project 工具详细分析依赖关系
3. 使用 export_analysis_data 工具导出完整报告
```

### 场景 4: 版本变更对比
```
我需要了解两个版本之间的差异，请：
1. 使用 create_project_snapshot 工具为当前版本创建快照
2. 切换到旧版本后再次创建快照
3. 使用 compare_snapshots 工具比较两个快照
```

## 🐛 故障排查

### 问题 1: MCP 服务器未显示
**原因**: 配置文件路径或格式错误
**解决**:
1. 检查配置文件路径是否正确
2. 验证 JSON 格式是否有效
3. 确认 Python 环境中已安装 mcp 包

### 问题 2: 工具调用失败
**原因**: 项目路径不存在或权限不足
**解决**:
1. 确认项目路径存在且可访问
2. 检查文件权限
3. 查看 Claude Desktop 日志获取详细错误信息

### 问题 3: 分析结果为空
**原因**: 项目中没有支持的代码文件
**解决**:
1. 确认项目中有 Python、JavaScript 等支持的代码文件
2. 检查 `.gitignore` 配置，确保代码文件未被排除
3. 使用 `languages` 参数明确指定要分析的语言

## 📝 日志和调试

MCP 服务器日志会输出到标准错误流。在 Claude Desktop 中：

**Windows**: `%APPDATA%\Claude\logs\`
**macOS**: `~/Library/Logs/Claude/`
**Linux**: `~/.local/share/Claude/logs/`

查看日志文件以获取详细的调试信息。

## 🔄 更新服务器

更新代码后，需要重启 Claude Desktop 以加载新版本：

```bash
# 1. 更新代码
git pull

# 2. 更新依赖（如有变化）
pip install -r requirements.txt

# 3. 重启 Claude Desktop
```

## 🆘 获取帮助

如遇到问题：
1. 查看本指南的故障排查部分
2. 检查 Claude Desktop 日志
3. 在项目 GitHub 提交 Issue
4. 参考 MCP 官方文档: https://modelcontextprotocol.io/