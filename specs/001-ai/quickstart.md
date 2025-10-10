# Quick Start Guide: AI分析指挥与可视化平台

**Feature**: 001-ai | **Date**: 2025-10-09 | **Version**: 1.0.0

## 目录

1. [安装准备](#1-安装准备)
2. [快速启动](#2-快速启动)
3. [核心概念](#3-核心概念)
4. [基础使用](#4-基础使用)
5. [进阶功能](#5-进阶功能)
6. [故障排除](#6-故障排除)

---

## 1. 安装准备

### 1.1 系统要求

**后端环境**：
- Python 3.11 或更高版本
- 8GB RAM（推荐 16GB）
- 5GB 可用磁盘空间

**前端环境**：
- Node.js 18.x 或更高版本
- 现代浏览器（Chrome 90+, Firefox 88+, Safari 14+, Edge 90+）

**AI 工具**（至少选择一种）：
- IDE 集成 AI（VS Code Copilot, JetBrains AI）
- 命令行 AI（Claude Code, Cursor, Aider）
- 云端 AI API（OpenAI, Anthropic, Google Gemini）
- 本地 AI 模型（Ollama, LM Studio）

### 1.2 安装步骤

**Step 1: 克隆仓库**

```bash
git clone https://github.com/your-org/aiflow.git
cd aiflow
```

**Step 2: 安装后端依赖**

```bash
cd backend
poetry install
# 或使用 pip
pip install -r requirements.txt
```

**Step 3: 安装前端依赖**

```bash
cd ../frontend
pnpm install
# 或使用 npm
npm install
```

**Step 4: 配置 AI 适配器**

创建配置文件 `~/.aiflow/config/adapters.yaml`：

```yaml
adapters:
  # 示例：Claude Code 适配器
  - id: "claude-code-adapter"
    type: "cli_tool"
    name: "Claude Code"
    config:
      command: "claude"
      enabled: true
    priority: 1

  # 示例：Anthropic API 适配器
  - id: "anthropic-api-adapter"
    type: "cloud_api"
    name: "Anthropic Claude API"
    config:
      api_key: "${ANTHROPIC_API_KEY}"  # 从环境变量读取
      api_base: "https://api.anthropic.com"
      model: "claude-3-opus-20240229"
      enabled: false
    priority: 2

  # 示例：Ollama 本地模型
  - id: "ollama-adapter"
    type: "local_model"
    name: "Ollama"
    config:
      api_base: "http://localhost:11434"
      model: "codellama:34b"
      enabled: false
    priority: 3
```

**Step 5: 初始化 Prompt 模板库**

```bash
cd backend
python -m aiflow.prompts.init
```

这将从 Git LFS 拉取 Prompt 模板文件并建立索引。

---

## 2. 快速启动

### 2.1 启动后端服务

```bash
cd backend
poetry run uvicorn aiflow.main:app --reload --port 8000
```

服务启动后，访问 http://localhost:8000/docs 查看 API 文档。

### 2.2 启动前端开发服务器

```bash
cd frontend
pnpm dev
```

浏览器自动打开 http://localhost:5173

### 2.3 首次分析示例项目

**方式 1 - 通过 Web UI**：

1. 打开 http://localhost:5173
2. 点击 "新建分析" 按钮
3. 选择项目路径（示例：`/path/to/your/python/project`）
4. 选择 AI 工具（系统会自动检测可用适配器）
5. 点击 "开始分析"
6. 等待分析完成（进度条实时更新）

**方式 2 - 通过 CLI**：

```bash
# 安装 CLI 工具
pip install aiflow-cli

# 分析项目
aiflow analyze /path/to/your/python/project \
  --adapter claude-code-adapter \
  --output analysis-result.json

# 启动可视化
aiflow visualize analysis-result.json
```

**方式 3 - 通过 Python API**：

```python
from aiflow import AnalysisEngine, Visualizer

# 创建分析引擎
engine = AnalysisEngine(adapter_id="claude-code-adapter")

# 执行分析
result = await engine.analyze(
    project_path="/path/to/your/python/project",
    config={
        "scope": "full",
        "enable_cache": True
    }
)

# 启动可视化
visualizer = Visualizer(result)
visualizer.serve(port=8080)
```

---

## 3. 核心概念

### 3.1 三大核心组件

**1. 核心指令集 (Prompt Library)**
- 系统的"大脑"，包含精心设计的 Prompt 模板
- 驱动 AI 进行分阶段分析
- 版本化管理，支持热加载

**2. AI 适配器层 (Adapter Layer)**
- 连接多种 AI 工具（IDE、命令行、云端、本地）
- 标准化数据格式转换
- 自动降级和容错机制

**3. 可视化引擎 (Visualization Engine)**
- **Cytoscape.js**：主沙盘渲染器（层级化代码结构图）
- **D3.js**：细节分析渲染器（流程图、时序图）
- **Monaco Editor**：单步详情视图（代码编辑器 + 调试器）

### 3.2 五大分析阶段

```
项目认知 → 结构识别 → 语义分析 → 执行推理 → 并发检测
(30-60s)   (1-30min)   (1-40min)   (1-50min)   (0.5-20min)
```

每个阶段使用专门的 Prompt 模板，结果可缓存复用。

### 3.3 层级化行为沙盘

```
系统级（System）
  ├─ 模块级（Module）
  │   ├─ 类级（Class）
  │   └─ 函数级（Function）
  └─ 启动按钮（Launch Button）
      ├─ 大按钮：宏观联动场景
      └─ 小按钮：微观子流程
```

---

## 4. 基础使用

### 4.1 导航层级结构

**展开/折叠节点**：
- 双击节点：展开下一层级
- 单击面包屑导航：返回上级层级
- 缩放/平移：鼠标滚轮缩放，拖拽平移

**搜索节点**：
- 按 `/` 打开搜索框
- 输入节点名称或功能关键词
- 按 `Enter` 定位到匹配节点

### 4.2 启动执行动画

**宏观联动场景**（大按钮）：
1. 在结构图上找到一个大模块（如"订单处理系统"）
2. 点击模块上的启动按钮（如"处理用户订单"）
3. 系统播放多流程联动动画
4. 观察子模块的激活顺序、数据流、同步点

**微观子流程**（小按钮）：
1. 双击大模块，展开内部子模块
2. 点击子模块的启动按钮（如"计算订单价格"）
3. 系统独立播放该子流程的执行动画
4. 可切换"孤立模式"和"上下文模式"

### 4.3 动画控制

**播放控制器**（底部面板）：
- ▶️ **播放/暂停**：空格键
- ⏪ **后退**：左箭头键
- ⏩ **前进**：右箭头键
- 🎚️ **速度调节**：鼠标拖动或输入数值（0.1x - 10x）

**时间回溯**：
- 拖动时间轴滑块
- 或点击时间轴上的特定时间点

**断点设置**：
- 右键点击代码单元
- 选择"设置断点"或"设置条件断点"
- 动画到达断点时自动暂停

### 4.4 钻入单步详情

**进入单步详情视图**：
1. 在动画播放或暂停时
2. 点击当前高亮的代码单元
3. 或按 `Ctrl+D`（Windows/Linux）/ `Cmd+D`（macOS）

**单步详情视图功能**：
- **代码面板**（左侧）：Monaco Editor 显示当前代码行
- **变量面板**（右侧）：当前作用域的所有变量及其值
- **调用栈面板**（底部）：完整的函数调用链
- **内存视图**（可选标签）：对象分配和引用关系

**单步执行**：
- `F10`：Step Over（单步跳过）
- `F11`：Step Into（单步进入）
- `Shift+F11`：Step Out（单步跳出）

**变量检查**：
- 点击变量展开详细结构
- 右键选择"查看历史"查看变量变化轨迹
- 右键选择"修改值"进入假设分析模式

---

## 5. 进阶功能

### 5.1 并发流可视化

**查看并发执行**：
1. 点击右上角"视图切换"
2. 选择"时序图视图"或"并发流程图"
3. 观察多个线程/协程的时间先后关系

**并发流控制**：
- **暂停全部**：暂停所有并发流
- **暂停单个流**：选择特定流暂停
- **单流聚焦**：隐藏其他流，专注于单一流

**同步点分析**：
- 时序图中的 **红色栅栏** 表示同步点（Barrier）
- 流程图中的 **菱形汇合** 表示 Join 操作

### 5.2 执行书签

**创建书签**：
1. 在动画播放到关键时刻暂停
2. 点击右上角"添加书签"图标
3. 输入书签名称和描述
4. 保存

**使用书签**：
- 左侧面板"书签"标签
- 点击书签名称立即跳转到该执行状态
- 支持书签对比（同时打开多个书签）

### 5.3 多路径对比

**对比不同分支**：
1. 点击工具栏"多路径对比"
2. 选择两个条件分支（如 `if` 和 `else`）
3. 系统并排展示两个分支的执行结果
4. 高亮差异部分

### 5.4 假设分析模式

**修改变量值观察影响**：
1. 在单步详情视图中
2. 右键点击变量 → "修改值"
3. 输入新值并点击"应用"
4. 系统标记为"假设分析模式"
5. 继续执行观察后续变化

**退出假设模式**：
- 点击顶部"退出假设分析"
- 或点击"重置为原始执行"

### 5.5 缓存管理

**查看缓存**：
```bash
aiflow cache list
```

**清除缓存**：
```bash
# 清除特定项目缓存
aiflow cache clear --project /path/to/project

# 清除所有缓存
aiflow cache clear --all
```

**缓存统计**：
```bash
aiflow cache stats
```

---

## 6. 故障排除

### 6.1 AI 适配器连接失败

**症状**：
- 错误信息："无法连接到 AI 适配器"
- 分析任务一直处于 "pending" 状态

**解决方案**：
1. 检查适配器配置是否正确（`~/.aiflow/config/adapters.yaml`）
2. 确认 AI 工具已安装并可在命令行调用
   ```bash
   # 测试 Claude Code
   claude --version

   # 测试 Ollama
   curl http://localhost:11434/api/version
   ```
3. 检查环境变量是否设置（如 `ANTHROPIC_API_KEY`）
4. 查看后端日志：
   ```bash
   tail -f ~/.aiflow/logs/backend.log
   ```

### 6.2 分析超时

**症状**：
- 分析任务运行 2 分钟后超时失败

**解决方案**：
1. **增加超时限制**（适用于大型项目）：
   ```python
   engine = AnalysisEngine(
       adapter_id="claude-code-adapter",
       timeout=300  # 增加到 5 分钟
   )
   ```

2. **启用智能范围限定**：
   ```python
   result = await engine.analyze(
       project_path="/path/to/project",
       config={
           "scope": "core_modules",  # 仅分析核心模块
           "max_nodes": 500          # 限制节点数量
       }
   )
   ```

3. **使用断点续传**：
   ```bash
   aiflow analyze /path/to/project --resume
   ```

### 6.3 可视化性能问题

**症状**：
- 结构图渲染缓慢（>10 秒）
- 动画卡顿（帧率 <15 FPS）

**解决方案**：
1. **启用虚拟化渲染**（自动检测）：
   ```javascript
   // frontend/src/config.js
   export const visualizationConfig = {
     enableVirtualization: true,  // 强制启用
     virtualThreshold: 1000       // 节点数阈值
   };
   ```

2. **降低动画质量**：
   - 设置面板 → 性能 → 启用"性能模式"
   - 减少并发流显示数量（≤5 个）

3. **检查浏览器硬件加速**：
   - Chrome: `chrome://settings` → 搜索"硬件加速"
   - 确保已启用

### 6.4 数据验证失败

**症状**：
- 错误信息："AI 返回数据验证失败"
- 分析结果无法加载

**解决方案**：
1. **查看详细验证错误**：
   ```bash
   aiflow validate analysis-result.json --verbose
   ```

2. **使用部分结果**：
   ```python
   result = await engine.analyze(
       project_path="/path/to/project",
       config={
           "allow_partial": True  # 允许部分结果
       }
   )
   ```

3. **重新分析特定阶段**：
   ```bash
   aiflow analyze /path/to/project \
     --stage semantic_analysis \
     --force
   ```

### 6.5 内存占用过高

**症状**：
- 系统提示内存不足
- 后端进程被 OOM Killer 终止

**解决方案**：
1. **启用轻量模式**：
   ```python
   engine = AnalysisEngine(
       adapter_id="claude-code-adapter",
       config={
           "lightweight_mode": True,  # 减少内存占用
           "max_cache_size": 100      # 限制缓存大小（MB）
       }
   )
   ```

2. **分批处理大型项目**：
   ```bash
   # 按目录分批分析
   aiflow analyze /path/to/project \
     --batch-mode \
     --batch-size 50
   ```

3. **增加系统 swap 空间**（Linux）：
   ```bash
   sudo fallocate -l 4G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

---

## 7. 示例工作流

### 7.1 理解陌生项目（15 分钟）

```bash
# Step 1: 启动完整分析（5-10 分钟）
aiflow analyze /path/to/unfamiliar/project

# Step 2: 打开可视化
aiflow visualize

# Step 3: 浏览系统级结构（2 分钟）
# - 查看顶层模块和架构模式
# - 识别核心业务模块

# Step 4: 钻入关键模块（3 分钟）
# - 双击"订单处理"模块
# - 查看内部子模块关系

# Step 5: 观察执行流程（5 分钟）
# - 点击"处理订单"启动按钮
# - 观察宏观联动动画
# - 钻入"计算价格"子流程查看详细逻辑
```

### 7.2 调试复杂并发问题（30 分钟）

```bash
# Step 1: 分析项目
aiflow analyze /path/to/project --focus concurrency

# Step 2: 切换到时序图视图
# - 观察多个线程的时间关系
# - 识别同步点和潜在死锁

# Step 3: 单流聚焦
# - 暂停其他流，专注于问题流
# - 设置断点在关键同步点

# Step 4: 钻入单步详情
# - 查看锁状态变量
# - 分析变量历史变化

# Step 5: 假设分析
# - 修改锁超时时间
# - 观察是否解决死锁
```

### 7.3 性能优化分析（45 分钟）

```bash
# Step 1: 性能分析模式
aiflow analyze /path/to/project --profile

# Step 2: 识别瓶颈函数
# - 查看执行时长标注
# - 找到耗时最长的函数调用

# Step 3: 对比优化前后
# - 创建执行书签（优化前）
# - 修改代码
# - 重新分析
# - 对比两个书签的执行时长

# Step 4: 并发优化评估
# - 分析可并行化的操作
# - 查看 Fork/Join 机会
# - 评估并行收益
```

---

## 8. 社区与支持

**文档**：https://docs.aiflow.dev
**GitHub**：https://github.com/your-org/aiflow
**Discord 社区**：https://discord.gg/aiflow
**问题反馈**：https://github.com/your-org/aiflow/issues

**常见问题 FAQ**：https://docs.aiflow.dev/faq
**视频教程**：https://www.youtube.com/@aiflow

---

**最后更新**: 2025-10-09 | **版本**: 1.0.0
