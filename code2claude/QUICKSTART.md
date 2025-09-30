# ClaudeFlow 快速开始指南

## 🚀 一键安装 MCP 服务器

### 方式 1: npm 安装 (最简单)

**如果你的项目使用 npm**:

```bash
npm run install
```

**或者全局安装**:

```bash
npm install -g claudeflow-mcp
claudeflow-install
```

### 方式 2: Python 直接安装 (推荐)

**单命令完成所有配置**:

```bash
python install_mcp.py
```

**这个脚本会自动**:
- ✅ 检查 Python 版本
- ✅ 安装所有依赖包 (包括 MCP SDK)
- ✅ 自动配置 Claude Desktop
- ✅ 备份现有配置
- ✅ 验证安装

**然后只需**:
1. 重启 Claude Desktop
2. 开始使用！

---

## 💬 使用示例

安装完成后，在 Claude Code 中直接使用：

### 示例 1: 分析项目
```
请使用 analyze_project 工具分析当前项目
```

### 示例 2: 识别代码热点
```
请使用 identify_code_hotspots 工具找出这个项目的问题文件
```

### 示例 3: 影响分析
```
我想修改 src/main.py，请使用 analyze_file_impact 工具评估影响范围
```

### 示例 4: 生成依赖图
```
请使用 generate_dependency_graph 工具生成模块依赖关系图
```

---

## 🛠️ 卸载

### npm 卸载

如需卸载 MCP 服务器:

```bash
npm run uninstall
```

**或者使用全局命令**:

```bash
claudeflow-uninstall
```

**可选**: 同时删除依赖包

```bash
npm run clean
# 或
claudeflow-uninstall --remove-deps
```

### Python 直接卸载

```bash
python uninstall_mcp.py
```

**可选**: 同时删除依赖包
```bash
python uninstall_mcp.py --remove-deps
```

---

## 📋 可用工具列表

| 工具 | 功能 | 使用示例 |
|------|------|----------|
| `analyze_project` | 完整项目代码分析 | 分析项目结构和代码质量 |
| `map_project_structure` | 项目结构映射 | 生成项目组织架构 |
| `generate_dependency_graph` | 依赖关系图 | 可视化模块依赖 |
| `identify_code_hotspots` | 代码热点识别 | 找出高复杂度文件 |
| `analyze_file_impact` | 文件影响分析 | 评估修改影响范围 |
| `trace_function_calls` | 函数调用追踪 | 追踪函数调用链 |
| `create_project_snapshot` | 创建快照 | 保存项目状态 |
| `compare_snapshots` | 快照对比 | 比较版本差异 |
| `export_analysis_data` | 导出数据 | 导出分析报告 |

---

## ❓ 常见问题

### Q: 安装脚本失败怎么办？

**A**: 检查以下几点:
1. Python 版本 >= 3.8
2. 有管理员权限
3. 网络连接正常
4. 查看错误信息并按提示操作

### Q: Claude Desktop 找不到工具？

**A**: 确认以下步骤:
1. 完全退出并重启 Claude Desktop
2. 检查配置文件是否正确更新
3. 查看 Claude Desktop 日志

### Q: 配置文件在哪里？

**A**: 根据操作系统:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### Q: 如何查看日志？

**A**: Claude Desktop 日志位置:
- **Windows**: `%APPDATA%\Claude\logs\`
- **macOS**: `~/Library/Logs/Claude/`
- **Linux**: `~/.local/share/Claude/logs/`

---

## 🔧 手动安装 (高级)

如果自动安装失败，可以手动安装：

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 编辑 Claude Desktop 配置

找到配置文件并添加:

```json
{
  "mcpServers": {
    "claudeflow": {
      "command": "python",
      "args": ["-m", "claudeflow.mcp_server"],
      "env": {}
    }
  }
}
```

### 3. 重启 Claude Desktop

---

## 📚 更多资源

- **详细配置**: [MCP_SETUP.md](./MCP_SETUP.md)
- **项目说明**: [README.md](./README.md)
- **转换报告**: [MCP_CONVERSION_REPORT.md](./MCP_CONVERSION_REPORT.md)

---

## 🎉 开始探索

安装完成后，尝试以下任务：

1. **了解项目结构**: "请帮我分析这个项目的整体架构"
2. **代码质量审查**: "请识别这个项目的代码热点和潜在问题"
3. **重构规划**: "我想重构 utils.py，请评估影响并给出建议"
4. **依赖分析**: "请生成项目的依赖关系图并分析复杂度"

享受 AI 辅助开发的强大能力！🚀