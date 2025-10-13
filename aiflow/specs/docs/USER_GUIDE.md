# AIFlow 用户使用指南

**User Guide for AIFlow Code Behavior Sandbox**

---

## 📋 目录

1. [快速开始](#快速开始)
2. [完整工作流程](#完整工作流程)
3. [高级用法](#高级用法)
4. [故障排查](#故障排查)
5. [最佳实践](#最佳实践)

---

## 🚀 快速开始

### 前提条件

- **Python 3.11+**
- **Node.js 18+**
- **AI API Key**（至少一个）：
  - Anthropic API Key (Claude 4.5)
  - OpenAI API Key (GPT-4)
  - Google API Key (Gemini)

### 5分钟快速体验

#### Step 1: 安装依赖

```bash
# 后端
cd backend
pip install -r requirements.txt

# 前端
cd ../frontend
npm install
```

#### Step 2: 配置 API Key

创建 `backend/.env` 文件：

```bash
# 选择一个 AI 服务（推荐 Claude 4.5）
ANTHROPIC_API_KEY=sk-ant-your-api-key-here

# 可选：其他 AI 服务
# OPENAI_API_KEY=sk-your-openai-key-here
# GOOGLE_API_KEY=your-google-key-here
```

#### Step 3: 分析你的第一个项目

```python
# demo.py
import asyncio
import json
from pathlib import Path
from aiflow.prompts import PromptRenderer
from aiflow.adapters.claude import create_claude_adapter

async def analyze_project():
    # 1. 准备输入数据
    project_path = Path("path/to/your/project")

    # 2. 渲染 Prompt 模板
    renderer = PromptRenderer()
    prompt = renderer.render(
        language="python",
        stage="comprehensive_analysis",
        input_data={
            "project_name": "MyApp",
            "project_path": str(project_path),
            "file_tree": "..."  # 你的项目文件树
        }
    )

    # 3. 通过 AI 适配器执行分析
    adapter = await create_claude_adapter()
    response = await adapter.generate(prompt=prompt)

    # 4. 保存结果
    output_file = Path("analysis_result.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(response.content, f, indent=2, ensure_ascii=False)

    print(f"✅ 分析完成！结果已保存到: {output_file}")

# 运行
asyncio.run(analyze_project())
```

#### Step 4: 启动可视化前端

```bash
cd frontend
npm run dev
```

打开浏览器访问 `http://localhost:5173`，拖拽 `analysis_result.json` 文件到页面中。

---

## 📊 完整工作流程

### 流程概览

```
用户准备 → AI分析 → 数据验证 → 可视化渲染 → 交互探索
```

### 详细步骤

#### 阶段1: 准备项目数据

**目标**：收集项目的基本信息和文件结构。

**操作**：

```python
from pathlib import Path

def collect_project_info(project_path: Path):
    """收集项目信息"""
    info = {
        "project_name": project_path.name,
        "project_path": str(project_path),
        "file_tree": generate_file_tree(project_path),
        "main_files": []
    }

    # 收集关键文件
    key_files = [
        "README.md",
        "package.json",
        "requirements.txt",
        "pyproject.toml"
    ]

    for file_name in key_files:
        file_path = project_path / file_name
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                info["main_files"].append({
                    "name": file_name,
                    "content": f.read()
                })

    return info

def generate_file_tree(path: Path, prefix="", max_depth=3, current_depth=0):
    """生成文件树字符串"""
    if current_depth >= max_depth:
        return ""

    tree = ""
    items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))

    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        connector = "└── " if is_last else "├── "
        tree += f"{prefix}{connector}{item.name}\n"

        if item.is_dir() and not item.name.startswith('.'):
            extension = "    " if is_last else "│   "
            tree += generate_file_tree(item, prefix + extension, max_depth, current_depth + 1)

    return tree
```

#### 阶段2: 渲染 Prompt 模板

**目标**：根据项目语言选择合适的 Prompt 模板。

**操作**：

```python
from aiflow.prompts import PromptRenderer

renderer = PromptRenderer()

# 方式 1: 使用综合分析模板（推荐）
prompt = renderer.render(
    language="python",
    stage="comprehensive_analysis",
    input_data=project_info
)

# 方式 2: 分阶段分析
prompts = []
for stage in ["project_understanding", "structure_recognition",
              "semantic_analysis", "execution_inference",
              "concurrency_detection"]:
    prompt = renderer.render(
        language="python",
        stage=stage,
        input_data=project_info
    )
    prompts.append(prompt)
```

**选择策略**：
- **小型项目**（<1000行）：使用综合分析模板，一次完成
- **中型项目**（1000-5000行）：使用综合分析模板或分阶段
- **大型项目**（>5000行）：建议分阶段分析，每阶段结果作为下一阶段输入

#### 阶段3: 通过 AI 适配器执行分析

**目标**：调用 AI 服务完成代码分析。

**操作**：

```python
from aiflow.adapters.claude import create_claude_adapter

# 创建适配器
adapter = await create_claude_adapter(
    model_name="claude-sonnet-4-5-20250929",  # Claude 4.5
    max_tokens=8192,
    temperature=0.3  # 降低随机性，提高一致性
)

# 执行分析
try:
    response = await adapter.generate(
        prompt=prompt,
        system_prompt="你是一个专业的代码分析助手，精通多种编程语言。"
    )

    print(f"✅ 分析成功！")
    print(f"📊 Token使用: {response.usage.input_tokens + response.usage.output_tokens}")
    print(f"⏱️ 耗时: {response.metadata.get('duration', 'N/A')}秒")

    result = response.content

except Exception as e:
    print(f"❌ 分析失败: {e}")
    # 错误处理逻辑
```

**流式输出**（适用于大型项目）：

```python
async for chunk in adapter.generate_stream(prompt=prompt):
    print(chunk, end='', flush=True)
```

#### 阶段4: 验证分析结果

**目标**：确保 AI 输出符合标准数据协议。

**操作**：

```python
from aiflow.protocol import ProtocolValidator

validator = ProtocolValidator()

# 完整验证
validation_result = validator.validate_complete(result)

if validation_result.is_valid:
    print("✅ 数据验证通过")
else:
    print("❌ 数据验证失败:")
    for error in validation_result.errors:
        print(f"  - {error}")

    # 尝试自动修复
    if validation_result.warnings:
        print("\n⚠️ 警告（已自动修复）:")
        for warning in validation_result.warnings:
            print(f"  - {warning}")
```

**验证内容**：
- ✅ JSON Schema 格式验证
- ✅ UUID v4 格式验证
- ✅ ISO 8601 时间戳验证
- ✅ 引用完整性验证（10种引用类型）
- ✅ 执行顺序唯一性验证

#### 阶段5: 序列化和保存

**目标**：将分析结果保存为 JSON 文件。

**操作**：

```python
from aiflow.protocol import ProtocolSerializer

serializer = ProtocolSerializer()

# 方式 1: 保存为标准 JSON
serializer.serialize(
    data=result,
    output_path="analysis_result.json",
    compress=False,
    validate=True
)

# 方式 2: 保存为压缩 JSON（节省 70% 空间）
serializer.serialize(
    data=result,
    output_path="analysis_result.json",
    compress=True,  # 生成 .json.gz 文件
    validate=True
)

# 方式 3: 增量更新（适用于分阶段分析）
serializer.update_partial(
    file_path="analysis_result.json",
    updates={
        "execution_trace": stage4_result,
        "concurrency_info": stage5_result
    },
    validate=True
)
```

#### 阶段6: 启动可视化前端

**目标**：在浏览器中渲染交互式行为沙盘。

**操作**：

```bash
cd frontend
npm run dev
```

**加载数据**：
1. 打开浏览器访问 `http://localhost:5173`
2. 拖拽 `analysis_result.json` 到页面中
3. 或点击"加载文件"按钮选择文件

#### 阶段7: 交互式探索

**目标**：通过可视化界面理解代码行为。

**核心交互**：

**1. 浏览代码结构**
```
操作:
  - 鼠标滚轮: 缩放
  - 鼠标拖拽: 平移
  - 点击节点: 查看详情
  - 双击节点: 展开/折叠子节点
```

**2. 启动按钮交互**
```
大按钮（Macro）:
  - 点击: 启动系统级多流程联动动画
  - 观察: 多条"脉冲"同时在沙盘上流动

小按钮（Micro）:
  - 点击: 启动子模块独立流程动画
  - 观察: 单一流程的执行路径
```

**3. 执行轨迹切换**
```
视图切换:
  - 结构图 (Cytoscape): 代码层级和依赖关系
  - 时序图 (D3): 组件间的消息传递
  - 流程图 (D3): 执行步骤和分支决策
  - 单步详情 (Monaco): 代码 + 变量 + 调用栈
```

**4. 单步调试**
```
操作:
  - ⏮️ 上一步: 回到前一个执行步骤
  - ⏯️ 播放/暂停: 控制动画播放
  - ⏭️ 下一步: 前进到下一个执行步骤
  - 🔍 查看变量: 检查当前作用域的变量状态
  - 📚 查看堆栈: 查看函数调用链
```

**5. 并发流程观察**
```
多流程联动:
  - 蓝色脉冲: 主线程执行路径
  - 绿色脉冲: 异步任务执行路径
  - 红色脉冲: 错误处理路径
  - 黄色节点: 同步点（锁、信号量等）
```

---

## 🔧 高级用法

### 1. 自定义 Prompt 模板

**场景**：为特定项目优化分析效果。

**步骤**：

1. 复制现有模板
```bash
cp backend/prompts/python/comprehensive/analysis/v1.0.0.yaml \
   backend/prompts/python/comprehensive/analysis/v1.1.0.yaml
```

2. 编辑模板
```yaml
metadata:
  id: "comprehensive-python-django-v1.1.0"
  version: "1.1.0"
  description: "专门针对Django项目优化的分析模板"

template: |
  # 在这里添加Django特定的分析指令

  ## Django项目特殊处理
  1. 识别 apps/ 目录下的各个应用
  2. 分析 models.py 中的数据模型
  3. 识别 views.py 中的视图函数
  4. 分析 urls.py 中的路由配置
  ...
```

3. 注册模板
```yaml
# backend/prompts/registry.yaml
templates:
  - id: "comprehensive-python-django-v1.1.0"
    path: "python/comprehensive/analysis/v1.1.0.yaml"
    language: "python"
    stage: "comprehensive_analysis"
    version: "1.1.0"
    latest: false
```

4. 使用自定义模板
```python
prompt = renderer.render(
    language="python",
    stage="comprehensive_analysis",
    version="1.1.0",  # 指定版本
    input_data=project_info
)
```

### 2. 多模型协同分析

**场景**：使用不同 AI 模型的优势。

**策略**：

```python
# Claude 4.5: 擅长推理和语义理解
claude_adapter = await create_claude_adapter()

# GPT-4: 擅长创造性命名
openai_adapter = await create_openai_adapter()

# 阶段 1-2: 使用 Claude（结构分析）
structure_result = await claude_adapter.generate(
    prompt=structure_prompt
)

# 阶段 3: 使用 GPT-4（业务命名）
semantic_result = await openai_adapter.generate(
    prompt=semantic_prompt
)

# 合并结果
final_result = merge_results(structure_result, semantic_result)
```

### 3. 批量项目分析

**场景**：分析多个相关项目。

**实现**：

```python
import asyncio
from pathlib import Path

async def batch_analyze(projects: list[Path]):
    """批量分析多个项目"""
    tasks = []
    for project_path in projects:
        task = analyze_project(project_path)
        tasks.append(task)

    # 并发执行（注意 API 速率限制）
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 处理结果
    for project_path, result in zip(projects, results):
        if isinstance(result, Exception):
            print(f"❌ {project_path.name}: {result}")
        else:
            print(f"✅ {project_path.name}: 分析完成")
            # 保存结果
            save_result(project_path, result)

# 使用
projects = [
    Path("projects/frontend"),
    Path("projects/backend"),
    Path("projects/mobile")
]
await batch_analyze(projects)
```

### 4. 增量分析

**场景**：代码更新后，只重新分析变更部分。

**实现**：

```python
from aiflow.protocol import ProtocolSerializer

serializer = ProtocolSerializer()

# 1. 检测文件变更
changed_files = detect_changes(project_path, last_analysis_time)

# 2. 只分析变更的模块
partial_result = await analyze_partial(
    changed_files=changed_files,
    previous_result=load_previous_result()
)

# 3. 增量更新 JSON
serializer.update_partial(
    file_path="analysis_result.json",
    updates=partial_result,
    validate=True
)
```

### 5. 导出和分享

**场景**：将分析结果分享给团队成员。

**导出格式**：

```python
from aiflow.export import ResultExporter

exporter = ResultExporter()

# 导出为静态 HTML（包含可视化）
exporter.to_html(
    result_file="analysis_result.json",
    output_file="analysis_report.html"
)

# 导出为 Markdown 报告
exporter.to_markdown(
    result_file="analysis_result.json",
    output_file="analysis_report.md"
)

# 导出为 PDF
exporter.to_pdf(
    result_file="analysis_result.json",
    output_file="analysis_report.pdf"
)
```

---

## 🔍 故障排查

### 问题 1: AI 输出格式不正确

**症状**：
```
❌ 数据验证失败:
  - 节点ID '1' 不是有效的UUID v4格式
  - 时间戳 '2025-01-12 10:30:00' 不是ISO 8601格式
```

**原因**：Prompt 指令不够明确，AI 未严格遵守格式要求。

**解决方案**：

1. **增强 Prompt 约束**
```yaml
# 在 Prompt 模板中强调
<constraints>
- 所有ID必须严格使用UUID v4格式: xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
- 所有时间戳必须严格使用ISO 8601格式: 2025-01-12T10:30:00.000Z
- 不接受任何简化格式
</constraints>
```

2. **提供明确示例**
```yaml
## 输出示例

✅ 正确:
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-01-12T10:30:00.123Z"
}

❌ 错误:
{
  "id": "1",  // ❌ 不是UUID
  "timestamp": "2025-01-12 10:30:00"  // ❌ 不是ISO 8601
}
```

3. **后处理修复**
```python
import uuid
from datetime import datetime

def fix_common_issues(data):
    """自动修复常见格式问题"""
    # 修复ID格式
    if "id" in data and not is_valid_uuid(data["id"]):
        data["id"] = str(uuid.uuid4())

    # 修复时间戳格式
    if "timestamp" in data:
        try:
            dt = datetime.fromisoformat(data["timestamp"])
            data["timestamp"] = dt.isoformat() + "Z"
        except:
            data["timestamp"] = datetime.now().isoformat() + "Z"

    return data
```

### 问题 2: API 速率限制

**症状**：
```
❌ RateLimitError: Rate limit exceeded. Retry after 60 seconds.
```

**原因**：短时间内发送过多请求。

**解决方案**：

```python
from aiflow.adapters.base import BaseAIAdapter

# 配置重试策略
adapter = await create_claude_adapter(
    max_retries=5,              # 最大重试次数
    retry_delay=10,             # 初始延迟（秒）
    exponential_backoff=True    # 使用指数退避
)

# 重试逻辑
response = await adapter.generate_with_retry(prompt=prompt)
```

### 问题 3: 内存不足

**症状**：
```
MemoryError: Unable to allocate array
```

**原因**：大型项目的分析结果过大。

**解决方案**：

1. **使用压缩存储**
```python
serializer.serialize(
    data=result,
    output_path="analysis_result.json",
    compress=True  # 启用 gzip 压缩，节省 70% 空间
)
```

2. **分阶段分析**
```python
# 不要一次性分析所有模块
# 按模块逐个分析，逐步合并结果
for module in project_modules:
    partial_result = await analyze_module(module)
    merge_into_final_result(partial_result)
```

3. **限制分析深度**
```python
# 在 Prompt 中限制深度
input_data = {
    "max_depth": 5,  # 最大递归深度
    "max_nodes": 1000,  # 最大节点数
    ...
}
```

### 问题 4: 前端渲染卡顿

**症状**：节点数量 >1000 时，Cytoscape.js 渲染缓慢。

**解决方案**：

1. **启用虚拟化渲染**
```typescript
const cy = cytoscape({
  renderer: {
    hideEdgesOnViewport: true,
    hideLabelsOnViewport: true,
    textureOnViewport: true
  }
});
```

2. **分层加载**
```typescript
// 初始只加载顶层节点
const topLevelNodes = data.nodes.filter(n => !n.parent);
cy.add(topLevelNodes);

// 按需加载子节点
cy.on('tap', 'node', (evt) => {
  const node = evt.target;
  if (node.data('hasChildren') && !node.data('childrenLoaded')) {
    loadChildren(node);
  }
});
```

3. **使用 Web Worker**
```typescript
// 在 Worker 中解析和处理数据
const worker = new Worker('data-processor.js');
worker.postMessage({ data: largeData });
worker.onmessage = (event) => {
  renderGraph(event.data);
};
```

### 问题 5: AI 输出不一致

**症状**：同一项目多次分析，结果差异很大。

**原因**：AI 生成具有随机性。

**解决方案**：

1. **降低 temperature**
```python
adapter = await create_claude_adapter(
    temperature=0.1  # 降低随机性（默认 0.7）
)
```

2. **使用种子（如果 API 支持）**
```python
response = await adapter.generate(
    prompt=prompt,
    seed=42  # 固定种子确保可重复性
)
```

3. **多次采样取平均**
```python
async def consistent_analysis(prompt, num_samples=3):
    """多次采样，取最一致的结果"""
    results = []
    for _ in range(num_samples):
        result = await adapter.generate(prompt=prompt)
        results.append(result)

    # 选择最一致的结果（例如，计算相似度）
    return select_most_consistent(results)
```

---

## 💡 最佳实践

### 1. Prompt 优化技巧

**DO ✅**：
- 提供完整的输入输出示例
- 使用结构化标签（`<thinking>`, `<output>`）
- 明确所有约束条件（UUID格式、时间格式）
- 要求 AI 提供置信度和推理依据

**DON'T ❌**：
- 使用模糊的指令（"分析一下"）
- 假设 AI 知道默认格式
- 忽略边界情况
- 不验证 AI 输出

### 2. 性能优化建议

**缓存策略**：
```python
# 缓存 Prompt 模板
template_cache = {}

def load_template_cached(language, stage):
    key = f"{language}:{stage}"
    if key not in template_cache:
        template_cache[key] = load_template(language, stage)
    return template_cache[key]
```

**并发控制**：
```python
# 控制并发请求数量
from asyncio import Semaphore

semaphore = Semaphore(5)  # 最多 5 个并发请求

async def analyze_with_limit(prompt):
    async with semaphore:
        return await adapter.generate(prompt=prompt)
```

### 3. 数据管理建议

**版本控制**：
```bash
# 为每次分析创建版本号
analysis_result_v1.0.0.json
analysis_result_v1.1.0.json

# 使用 Git 管理分析结果
git add analysis_result*.json
git commit -m "chore: update code analysis"
```

**备份策略**：
```python
import shutil
from datetime import datetime

# 自动备份旧结果
if os.path.exists("analysis_result.json"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backup/analysis_result_{timestamp}.json"
    shutil.copy("analysis_result.json", backup_file)
```

### 4. 团队协作建议

**分享最佳实践**：
- 将自定义 Prompt 模板提交到团队仓库
- 文档化特定项目的分析配置
- 分享分析结果的解读技巧

**Code Review 集成**：
```bash
# 在 PR 中自动生成代码分析
name: Code Analysis

on: pull_request

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run AIFlow Analysis
        run: python scripts/analyze.py
      - name: Upload Result
        uses: actions/upload-artifact@v3
        with:
          name: analysis-result
          path: analysis_result.json
```

---

## 📚 扩展阅读

- [架构设计文档](./ARCHITECTURE.md) - 深入理解系统设计
- [Prompt 设计文档](./PROMPT_DESIGN.md) - 学习如何优化指令集
- [标准数据协议](../backend/aiflow/protocol/schemas/analysis-schema-v1.0.0.json) - 完整的 JSON Schema

---

## 🆘 获取帮助

遇到问题？试试这些资源：

1. **GitHub Issues**: [提交问题](https://github.com/yourusername/aiflow/issues)
2. **Discussions**: [社区讨论](https://github.com/yourusername/aiflow/discussions)
3. **文档**: [完整文档](https://docs.aiflow.dev)

---

**文档版本**: v1.0.0
**最后更新**: 2025-01-12
**维护者**: AIFlow Team
