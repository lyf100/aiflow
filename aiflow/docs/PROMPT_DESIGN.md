# AIFlow 核心指令集设计文档

**Prompt Library Design Document for AIFlow**

---

## 📋 目录

1. [指令集概述](#指令集概述)
2. [设计原则](#设计原则)
3. [五阶段分析流程](#五阶段分析流程)
4. [Prompt 模板结构](#prompt-模板结构)
5. [最佳实践](#最佳实践)
6. [示例模板](#示例模板)
7. [优化技巧](#优化技巧)

---

## 🎯 指令集概述

AIFlow 的核心指令集（Prompt Library）是整个平台的"大脑"。它通过精心设计的指令模板，指挥 AI 工具完成代码分析的所有工作。

### 核心使命

1. **智能委托**：平台不解析代码，而是通过指令让 AI 完成所有分析
2. **语义理解**：AI 负责模块划分、功能命名等需要业务理解的任务
3. **标准输出**：所有 AI 分析结果必须符合标准数据协议（JSON Schema v1.0.0）

### 设计哲学

```
传统方式：
  代码 → AST解析器 → 静态分析 → 机械化输出

AIFlow 方式：
  代码 + Prompt → AI理解 → 语义化输出
```

**关键差异**：
- ❌ 传统：技术名称（`UserController.createUser()`）
- ✅ AIFlow：业务语义（`用户注册流程`）

---

## 🏗️ 设计原则

### 1. 渐进式引导（Progressive Guidance）

**原则**：从宏观到微观，逐步深入分析。

```yaml
阶段划分：
  Stage 1 (项目认知): 先理解整体
  Stage 2 (结构识别): 再识别层次
  Stage 3 (语义分析): 然后理解语义
  Stage 4 (执行推理): 接着推断行为
  Stage 5 (并发检测): 最后分析并发
```

**为什么**：
- AI 需要上下文才能做出准确推断
- 先宏观后微观，符合人类认知规律
- 每个阶段输出为下一阶段提供输入

### 2. 明确性优先（Explicit Over Implicit）

**原则**：指令必须明确、具体、无歧义。

```yaml
❌ 差的指令:
  "分析这个项目的代码结构"
  # 问题: 什么叫"结构"？输出什么格式？

✅ 好的指令:
  "识别项目中的所有模块、类、函数，并生成以下JSON格式：
   {
     "nodes": [...],
     "edges": [...]
   }
   其中每个节点必须包含id、label、stereotype、parent等字段"
```

### 3. 示例驱动（Example-Driven）

**原则**：提供完整的输入输出示例。

```yaml
指令中必须包含:
  1. 输入示例（代码片段）
  2. 期望输出（JSON示例）
  3. 边界情况处理（异常示例）
```

**为什么**：
- AI 通过示例学习比通过描述学习更准确
- 减少输出格式的不确定性
- 降低 AI "创造性发挥"的风险

### 4. 约束驱动（Constraint-Driven）

**原则**：明确告知 AI 不能做什么。

```yaml
必须包含的约束:
  - UUID 必须是 v4 格式
  - 时间戳必须是 ISO 8601 格式
  - execution_order 必须全局唯一递增
  - 节点ID必须在edges中引用时存在
  - 不要编造不存在的代码
```

### 5. 业务语义化（Business Semantics）

**原则**：优先使用业务语言而非技术术语。

```yaml
❌ 技术化命名:
  节点名称: "UserController"
  按钮名称: "createUser()"

✅ 业务语义化:
  节点名称: "用户管理模块"
  按钮名称: "创建新用户"
```

**为什么**：
- 业务人员也能理解可视化结果
- 更符合"行为沙盘"的定位
- AI 擅长理解业务语义

### 6. 可验证性（Verifiability）

**原则**：AI 输出必须可验证。

```yaml
验证机制:
  1. JSON Schema 格式验证
  2. 引用完整性验证
  3. 业务规则验证
  4. AI 必须提供 confidence 分数
```

---

## 📊 五阶段分析流程

### Stage 1: 项目认知（Project Understanding）

**目标**：理解项目的整体特征和技术背景。

**输入数据**：
```yaml
- project_path: 项目根目录
- project_name: 项目名称
- file_tree: 文件树结构
- main_files: 主要文件列表（README, package.json等）
```

**分析任务**：
1. 识别主要编程语言
2. 检测使用的框架和库
3. 推断架构模式（MVC, 微服务, 分层架构等）
4. 识别入口文件
5. 评估项目复杂度

**输出格式**：
```json
{
  "project_metadata": {
    "name": "string",
    "language": "string",
    "version": "string",
    "description": "AI生成的项目描述",
    "framework": ["string"],
    "architecture_pattern": ["string"],
    "entry_points": ["string"],
    "dependencies": ["string"],
    "complexity_score": 0.0
  }
}
```

**关键指令要点**：
```yaml
明确要求:
  - 基于 README.md 和 package.json 进行推理
  - 如果 README 不可靠，标注 "readme_reliability": "不可靠"
  - 必须给出 complexity_score (0-1)
  - 必须用中文生成 description（业务语义化）
```

### Stage 2: 结构识别（Structure Recognition）

**目标**：识别代码的层级结构和依赖关系。

**输入数据**：
```yaml
- project_metadata: Stage 1 输出
- source_files: 源代码文件列表
- file_contents: 部分文件内容
```

**分析任务**：
1. 识别系统级模块划分
2. 识别每个模块内的类和函数
3. 建立父子层级关系
4. 识别模块间的依赖关系（imports, calls）
5. 为每个节点生成业务语义化的名称

**输出格式**：
```json
{
  "code_structure": {
    "nodes": [
      {
        "id": "uuid-v4",
        "label": "用户认证模块",
        "stereotype": "module",
        "parent": null,
        "file_path": "src/auth/index.js",
        "line_range": [1, 150],
        "metadata": {
          "visibility": "public",
          "is_async": false,
          "is_exported": true,
          "ai_confidence": 0.95
        }
      }
    ],
    "edges": [
      {
        "id": "uuid-v4",
        "source": "node-id-1",
        "target": "node-id-2",
        "relationship": "imports",
        "label": "导入用户模型",
        "weight": 0.8
      }
    ]
  }
}
```

**关键指令要点**：
```yaml
明确要求:
  - label 必须是业务语义化的中文名称
  - stereotype 必须是: system | module | class | function | service | component
  - parent 字段建立层级关系
  - 所有 edge.source 和 edge.target 必须指向存在的节点ID
  - relationship 必须是: imports | calls | extends | implements | contains | depends_on
```

### Stage 3: 语义分析（Semantic Analysis）

**目标**：理解代码的业务语义，生成启动按钮。

**输入数据**：
```yaml
- project_metadata: Stage 1 输出
- code_structure: Stage 2 输出
- source_files: 源代码文件
```

**分析任务**：
1. 识别具有独立业务意义的功能单元
2. 为每个功能单元生成"启动按钮"
3. 建立按钮的嵌套关系（大按钮 → 小按钮）
4. 推断按钮的类型（macro/micro）和层级

**输出格式**：
```json
{
  "behavior_metadata": {
    "launch_buttons": [
      {
        "id": "uuid-v4",
        "node_id": "关联的代码节点ID",
        "name": "启动用户注册流程",
        "description": "完整的用户注册业务流程，包括邮箱验证和数据保存",
        "type": "macro",
        "level": "system",
        "icon": "user-plus",
        "parent_button_id": null,
        "child_button_ids": ["子按钮ID1", "子按钮ID2"],
        "traceable_unit_id": "关联的执行轨迹ID",
        "metadata": {
          "ai_confidence": 0.90,
          "ai_explanation": "基于函数名和业务逻辑推理",
          "estimated_duration": 5000,
          "requires_input": true,
          "has_side_effects": true
        }
      }
    ],
    "functional_units": [
      {
        "id": "uuid-v4",
        "name": "用户注册单元",
        "type": "business_process",
        "node_ids": ["关联节点ID列表"],
        "input_data": ["email", "password"],
        "output_data": ["user_id", "token"],
        "dependencies": ["数据库服务", "邮件服务"]
      }
    ]
  }
}
```

**关键指令要点**：
```yaml
明确要求:
  - name 必须是业务语义化的中文名称（不是技术函数名）
  - type 分为 macro（系统级）和 micro（模块级）
  - level 分为 system | module | component | function
  - parent_button_id 建立嵌套关系：
    * 顶层按钮: parent_button_id = null
    * 子按钮: parent_button_id = 父按钮ID
  - 必须提供 ai_explanation 说明推理依据
  - estimated_duration 单位为毫秒
```

### Stage 4: 执行推理（Execution Inference）

**目标**：推断代码的执行路径和调用关系。

**输入数据**：
```yaml
- project_metadata: Stage 1 输出
- code_structure: Stage 2 输出
- behavior_metadata: Stage 3 输出
- source_files: 源代码文件
```

**分析任务**：
1. 识别 3-5 个核心业务场景
2. 为每个场景推断执行路径
3. 生成三种格式的执行轨迹：
   - flowchart（流程图）
   - sequence（时序图）
   - step-by-step（单步执行）
4. 推断变量作用域和调用堆栈

**输出格式**：
```json
{
  "execution_trace": {
    "traceable_units": [
      {
        "id": "uuid-v4",
        "name": "用户登录流程",
        "type": "i-trace",
        "sub_unit_ids": [],
        "level": "system",
        "traces": [
          {
            "format": "flowchart",
            "data": {
              "steps": [
                {
                  "id": "step-uuid",
                  "label": "验证用户输入",
                  "type": "process"
                },
                {
                  "id": "fork-uuid",
                  "label": "并发检查",
                  "type": "fork"
                }
              ],
              "connections": [...]
            }
          },
          {
            "format": "sequence",
            "data": {
              "lifelines": [...],
              "messages": [...]
            }
          },
          {
            "format": "step-by-step",
            "data": {
              "steps": [...],
              "variableScopes": [...],
              "callStack": [...]
            }
          }
        ]
      }
    ]
  }
}
```

**关键指令要点**：
```yaml
明确要求:
  - 必须生成 3 种格式的 trace（flowchart, sequence, step-by-step）
  - flowchart 的 type 必须支持: start | end | process | decision | fork | join
  - sequence 的 timestamp 是相对时间戳（毫秒）
  - step-by-step 的 execution_order 必须全局唯一递增
  - variableScopes 的 scope_type 必须是: global | local | closure
  - callStack 记录函数调用的完整链路
  - 对于并发场景，必须使用 fork/join 节点
```

### Stage 5: 并发检测（Concurrency Detection）

**目标**：检测代码中的并发模式和潜在问题。

**输入数据**：
```yaml
- project_metadata: Stage 1 输出
- code_structure: Stage 2 输出
- execution_trace: Stage 4 输出
- source_files: 源代码文件
```

**分析任务**：
1. 检测并发机制（asyncio, threading, multiprocessing）
2. 识别并发流和同步点
3. 分析潜在的并发问题（竞态条件、死锁）

**输出格式**：
```json
{
  "concurrency_info": {
    "mechanisms": ["asyncio", "threading"],
    "flows": [
      {
        "id": "uuid-v4",
        "name": "异步数据库查询流",
        "type": "asyncio",
        "start_node_id": "node-id",
        "end_node_id": "node-id",
        "sync_points": ["sync-point-id"]
      }
    ],
    "sync_points": [
      {
        "id": "uuid-v4",
        "type": "lock | semaphore | barrier | event",
        "node_id": "node-id",
        "involved_flows": ["flow-id-1", "flow-id-2"],
        "description": "等待数据库连接释放"
      }
    ],
    "potential_issues": [
      {
        "type": "race_condition | deadlock | resource_leak",
        "severity": "high | medium | low",
        "location": "file:line",
        "description": "描述问题",
        "suggestion": "修复建议"
      }
    ]
  }
}
```

**关键指令要点**：
```yaml
明确要求:
  - mechanisms 必须从实际代码中检测（不能编造）
  - flows 描述并发执行的路径
  - sync_points 标识线程/协程的同步点
  - potential_issues 必须基于静态分析推理
  - severity 评级必须合理（high/medium/low）
```

---

## 📝 Prompt 模板结构

### YAML 文件格式

```yaml
# 元数据块（必需）
metadata:
  id: "project-understanding-python-v1.0.0"
  version: "1.0.0"
  stage: "project_understanding"
  target_language: "python"
  created_at: "2025-01-01T00:00:00Z"
  author: "AIFlow Team"
  description: "Python项目的项目认知阶段分析"
  estimated_tokens: 5000

# Jinja2 模板（必需）
template: |
  你是一个专精于深度源代码分析的AI助手。

  ## 任务目标
  分析以下Python项目，完成项目认知阶段的分析。

  ## 输入数据
  - 项目名称: {{ project_name }}
  - 项目路径: {{ project_path }}
  - 文件树:
  ```
  {{ file_tree }}
  ```

  ## 分析要求
  1. 识别主要编程语言和框架
  2. 推断架构模式
  3. 评估项目复杂度

  ## 输出格式
  请严格按照以下JSON Schema输出：
  ```json
  {
    "project_metadata": {
      "name": "string",
      "language": "python",
      ...
    }
  }
  ```

  ## 约束条件
  - 必须基于实际文件内容进行推理
  - 不要编造不存在的信息
  - complexity_score 范围: 0.0-1.0

# 输入数据 Schema（必需）
input_schema:
  type: object
  required:
    - project_name
    - project_path
    - file_tree
  properties:
    project_name:
      type: string
    project_path:
      type: string
    file_tree:
      type: string

# 输出数据 Schema（必需）
output_schema:
  type: object
  required:
    - project_metadata
  properties:
    project_metadata:
      type: object
      # ... 详细 schema

# 示例（可选但推荐）
examples:
  - input:
      project_name: "MyApp"
      project_path: "/path/to/project"
      file_tree: "..."
    output:
      project_metadata:
        name: "MyApp"
        language: "python"
        # ...
```

### Jinja2 变量和过滤器

**内置变量**：
```jinja2
{{ project_name }}      # 项目名称
{{ project_path }}      # 项目路径
{{ file_tree }}         # 文件树
{{ source_files }}      # 源文件列表
{{ previous_stage }}    # 上一阶段输出
```

**自定义过滤器**：
```jinja2
{{ timestamp | format_datetime }}           # 格式化时间戳
{{ data | to_json }}                        # 转换为JSON
{{ long_text | truncate(100) }}             # 截断文本
{{ source_code | highlight('python') }}     # 代码高亮
```

### 条件和循环

```jinja2
{% if project_metadata.framework %}
  识别到的框架: {{ project_metadata.framework | join(', ') }}
{% else %}
  未检测到明确的框架
{% endif %}

{% for file in source_files %}
  - 文件 {{ loop.index }}: {{ file.path }}
{% endfor %}
```

---

## 🎯 最佳实践

### 1. 结构化思考标签

**使用 XML 标签引导 AI 思考**：

```xml
<thinking>
  分析步骤：
  1. 扫描项目文件树
  2. 识别主要技术栈
  3. 推断架构模式
</thinking>

<analysis>
  基于以下证据：
  - package.json 包含 "react"
  - src/ 目录下有 components/
  - 使用了 Redux 状态管理

  结论：这是一个React单页应用
</analysis>

<output>
  {
    "project_metadata": { ... }
  }
</output>
```

### 2. 分步骤指令

```yaml
## Step 1: README可靠性评估
首先，评估README.md的可靠性：
- 可靠：内容详细、与代码一致
- 部分可靠：内容简略或部分过时
- 不可靠：缺失或严重过时

## Step 2: 静态结构分析
基于文件树和依赖文件，识别：
- 技术栈
- 目录组织方式
- 模块划分

## Step 3: 运行行为推理
推断核心业务场景的执行路径

## Step 4: 输出JSON
严格按照Schema输出
```

### 3. 示例驱动

```yaml
## 输出示例

✅ 正确示例：
{
  "nodes": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "label": "用户认证模块",
      "stereotype": "module"
    }
  ]
}

❌ 错误示例：
{
  "nodes": [
    {
      "id": "1",  // ❌ 不是UUID v4
      "label": "UserAuth",  // ❌ 不是业务语义化
      "stereotype": "mod"  // ❌ 不在允许值列表中
    }
  ]
}
```

### 4. 置信度标注

```yaml
## 推理置信度

对于每个推断，必须提供置信度分数：
- 0.9-1.0：基于明确的代码证据
- 0.7-0.9：基于合理的逻辑推理
- 0.5-0.7：基于模式匹配和经验
- 0.0-0.5：不确定的猜测（避免）

示例：
{
  "metadata": {
    "ai_confidence": 0.95,
    "ai_explanation": "基于函数签名和注释明确推断"
  }
}
```

### 5. 边界情况处理

```yaml
## 边界情况处理规则

1. 空项目：
   - 如果项目只有配置文件，标注 complexity_score = 0.1
   - nodes 数组可以为空

2. 无法识别语言：
   - 设置 language = "unknown"
   - framework = []

3. 缺失README：
   - description = "（AI基于代码推断）项目描述..."

4. 循环依赖：
   - 在 edges 中标注 "is_circular": true

5. 递归函数：
   - 在 callStack 中使用 depth 字段标识递归深度
```

---

## 📚 示例模板

### 综合分析 Prompt（v1.0.0）

这是一个单次完成所有 5 个阶段的综合模板：

```yaml
metadata:
  id: "comprehensive-project-analysis-v1.0.0"
  version: "1.0.0"
  stage: "comprehensive_analysis"
  target_language: "any"
  description: "对软件项目进行全面的多维度分析"

template: |
  <role>
  你是一个专精于深度源代码分析的AI助手，能够理解代码的结构、语义和运行行为。
  </role>

  <task>
  对以下项目进行全面分析，生成完整的标准化数据。
  </task>

  <input>
  项目名称: {{ project_name }}
  项目路径: {{ project_path }}
  文件树:
  ```
  {{ file_tree }}
  ```
  </input>

  <process>
  ## Step 1: 文档可靠性评估
  1. 解析 README.md
  2. 扫描依赖文件
  3. 评估可靠性等级

  ## Step 2: 静态结构分析
  1. 识别模块和组件
  2. 分析依赖关系
  3. 建立层级结构
  4. 生成业务语义化的节点和边

  ## Step 3: 运行行为分析
  1. 识别 3-5 个核心业务场景
  2. 推断执行路径
  3. 估算时间线（ISO 8601格式）
  4. 追踪变量作用域
  5. 检测并发模式

  ## Step 4: 并发与高级模式
  1. 检测并发机制
  2. 识别同步点
  3. 分析潜在问题
  </process>

  <output>
  请严格按照以下JSON Schema输出：
  ```json
  {
    "$schema": "https://aiflow.dev/schemas/analysis-v1.0.0.json",
    "version": "1.0.0",
    "project_metadata": { ... },
    "code_structure": { ... },
    "behavior_metadata": { ... },
    "execution_trace": { ... },
    "concurrency_info": { ... }
  }
  ```
  </output>

  <constraints>
  - 所有ID必须是UUID v4格式
  - 所有时间戳必须是ISO 8601格式
  - execution_order必须全局唯一递增
  - 节点ID必须在edges中引用前存在
  - label和name必须使用业务语义化的中文
  - 不要编造不存在的代码
  - 必须提供ai_confidence和ai_explanation
  </constraints>
```

---

## ⚡ 优化技巧

### 1. Token 优化

**问题**：Prompt 过长导致成本高、响应慢。

**解决方案**：

```yaml
1. 使用简洁的指令：
   ❌ "请你仔细分析这个项目，并且要注意..."
   ✅ "分析项目，要求："

2. 引用而非复制：
   ❌ 在Prompt中粘贴完整Schema
   ✅ "输出格式参考: analysis-schema-v1.0.0.json"

3. 分阶段而非一次性：
   ❌ 一个超长Prompt完成所有分析
   ✅ 5个中等Prompt，逐步深入

4. 使用示例而非详细描述：
   ❌ 用1000字描述输出格式
   ✅ 给1个完整的JSON示例
```

### 2. 准确性优化

**问题**：AI 输出不符合预期格式或包含错误。

**解决方案**：

```yaml
1. 明确约束：
   "UUID必须是v4格式: xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"

2. 提供反例：
   "❌ 错误: 'id': '1'  # 不是UUID
    ✅ 正确: 'id': '550e8400-e29b-41d4-a716-446655440000'"

3. 结构化标签：
   使用<thinking>、<analysis>、<output>引导思考

4. 置信度要求：
   "对于每个推断，必须提供0-1的置信度分数"

5. 证据要求：
   "在ai_explanation中说明推理依据"
```

### 3. 鲁棒性优化

**问题**：特殊项目导致 AI 输出异常。

**解决方案**：

```yaml
1. 边界情况明确：
   "如果项目为空，nodes可以为空数组"

2. 降级策略：
   "如果无法识别框架，设置framework=[]"

3. 错误恢复：
   "如果遇到无法解析的文件，跳过并在metadata中标注"

4. 默认值：
   "如果无法推断complexity_score，设置为0.5"
```

### 4. 可维护性优化

**问题**：模板难以维护和版本管理。

**解决方案**：

```yaml
1. 模块化：
   将通用部分提取为Jinja2宏：
   {% from 'common.j2' import output_format_section %}

2. 版本化：
   文件命名: stage-language-vX.Y.Z.yaml
   元数据: version字段

3. 注释：
   在模板中添加注释说明设计意图

4. 文档化：
   每个模板都有对应的设计文档

5. 测试：
   为每个模板编写单元测试
```

---

## 📖 参考资料

- [Jinja2 模板语法](https://jinja.palletsprojects.com/)
- [JSON Schema 规范](https://json-schema.org/)
- [Anthropic Prompt Engineering](https://docs.anthropic.com/claude/docs/prompt-engineering)
- [OpenAI Best Practices](https://platform.openai.com/docs/guides/prompt-engineering)

---

**文档版本**: v1.0.0
**最后更新**: 2025-01-12
**维护者**: AIFlow Team
