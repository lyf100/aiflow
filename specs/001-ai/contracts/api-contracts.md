# API Contracts: AI分析指挥与可视化平台

**Feature**: 001-ai | **Date**: 2025-10-09 | **Version**: 1.0.0

## 1. AI 适配器接口 (AIAdapter Interface)

### 1.1 核心接口定义

**Python Protocol 定义**：

```python
from typing import Protocol, TypedDict, Literal, Optional
from datetime import datetime

class PromptRequest(TypedDict):
    """AI 分析请求标准格式"""
    request_id: str                      # 请求唯一 ID (UUID v4)
    prompt_id: str                       # Prompt 模板 ID
    prompt_version: str                  # 版本号（语义化版本）
    stage: Literal["project_understanding", "structure_recognition",
                   "semantic_analysis", "execution_inference",
                   "concurrency_detection"]
    input_data: dict                     # 输入数据（项目路径、代码片段、上下文）
    context: dict                        # 分析上下文（前序结果、项目元数据）
    quality_criteria: dict               # 质量标准

class AnalysisResult(TypedDict):
    """AI 分析结果标准格式"""
    request_id: str                      # 对应的请求 ID
    status: Literal["success", "partial", "failed"]
    data: dict                           # 符合标准数据协议的 JSON
    metadata: ResultMetadata             # AI 调用元数据
    confidence: float                    # AI 置信度 (0.0-1.0)
    explanation: str                     # AI 决策解释

class ResultMetadata(TypedDict):
    """结果元数据"""
    adapter_id: str                      # 适配器 ID
    ai_model: str                        # AI 模型名称（如 "gpt-4-turbo", "claude-3-opus"）
    execution_time: float                # 执行时长（秒）
    token_usage: TokenUsage              # Token 消耗统计
    timestamp: str                       # 时间戳（ISO 8601）

class TokenUsage(TypedDict):
    """Token 使用统计"""
    prompt_tokens: int                   # Prompt token 数量
    completion_tokens: int               # 生成 token 数量
    total_tokens: int                    # 总 token 数量

class AIAdapter(Protocol):
    """AI 适配器标准接口"""

    async def analyze(self, request: PromptRequest) -> AnalysisResult:
        """
        执行 AI 分析

        Args:
            request: AI 分析请求

        Returns:
            AnalysisResult: 分析结果

        Raises:
            AdapterTimeoutError: 调用超时（默认 120 秒）
            AdapterConnectionError: 连接失败
            AdapterValidationError: 数据验证失败
        """
        ...

    async def health_check(self) -> bool:
        """
        健康检查

        Returns:
            bool: True 表示适配器可用，False 表示不可用
        """
        ...

    def get_capabilities(self) -> dict:
        """
        获取适配器能力声明

        Returns:
            dict: 能力声明，包含：
                - supported_languages: list[str] - 支持的编程语言
                - max_tokens: int - 最大 token 限制
                - supports_streaming: bool - 是否支持流式响应
                - rate_limit: dict - 速率限制信息
        """
        ...
```

### 1.2 请求示例

**项目认知阶段 (Project Understanding)**：

```json
{
  "request_id": "req-001-abc123",
  "prompt_id": "python-project-understanding-v1.0.0",
  "prompt_version": "1.0.0",
  "stage": "project_understanding",
  "input_data": {
    "project_path": "/path/to/project",
    "directory_tree": "...",
    "readme_content": "...",
    "config_files": {
      "requirements.txt": "...",
      "setup.py": "..."
    }
  },
  "context": {},
  "quality_criteria": {
    "min_confidence": 0.7,
    "required_fields": ["project_type", "main_language", "framework"]
  }
}
```

**结构识别阶段 (Structure Recognition)**：

```json
{
  "request_id": "req-002-def456",
  "prompt_id": "python-structure-recognition-v1.1.0",
  "prompt_version": "1.1.0",
  "stage": "structure_recognition",
  "input_data": {
    "source_files": [
      {
        "path": "src/auth/service.py",
        "content": "..."
      },
      {
        "path": "src/auth/models.py",
        "content": "..."
      }
    ]
  },
  "context": {
    "project_understanding": {
      "project_type": "web_api",
      "main_language": "python",
      "framework": "fastapi"
    }
  },
  "quality_criteria": {
    "min_confidence": 0.8,
    "min_nodes": 5,
    "max_nodes": 1000
  }
}
```

### 1.3 响应示例

**成功响应**：

```json
{
  "request_id": "req-001-abc123",
  "status": "success",
  "data": {
    "project_type": "web_api",
    "main_language": "python",
    "framework": "fastapi",
    "architecture_pattern": "layered",
    "business_domain": "authentication_service"
  },
  "metadata": {
    "adapter_id": "claude-code-adapter",
    "ai_model": "claude-3-opus-20240229",
    "execution_time": 12.5,
    "token_usage": {
      "prompt_tokens": 2500,
      "completion_tokens": 800,
      "total_tokens": 3300
    },
    "timestamp": "2025-10-09T10:30:00Z"
  },
  "confidence": 0.92,
  "explanation": "项目使用 FastAPI 框架构建 RESTful API，采用分层架构（路由层、服务层、数据访问层），主要业务领域为用户认证服务。"
}
```

**部分成功响应**：

```json
{
  "request_id": "req-002-def456",
  "status": "partial",
  "data": {
    "nodes": [
      {
        "id": "node-001",
        "label": "用户认证模块",
        "stereotype": "module",
        "metadata": {
          "ai_confidence": 0.88
        }
      }
    ],
    "edges": [],
    "missing_sections": ["concurrency_info"]
  },
  "metadata": {
    "adapter_id": "openai-gpt4-adapter",
    "ai_model": "gpt-4-turbo",
    "execution_time": 18.3,
    "token_usage": {
      "prompt_tokens": 5000,
      "completion_tokens": 1200,
      "total_tokens": 6200
    },
    "timestamp": "2025-10-09T10:35:00Z"
  },
  "confidence": 0.75,
  "explanation": "成功识别核心模块结构，但部分依赖关系因代码复杂性未能完全推断。"
}
```

**失败响应**：

```json
{
  "request_id": "req-003-ghi789",
  "status": "failed",
  "data": {},
  "metadata": {
    "adapter_id": "ollama-adapter",
    "ai_model": "codellama-34b",
    "execution_time": 60.0,
    "token_usage": {
      "prompt_tokens": 0,
      "completion_tokens": 0,
      "total_tokens": 0
    },
    "timestamp": "2025-10-09T10:40:00Z"
  },
  "confidence": 0.0,
  "explanation": "AI 调用超时，未能完成分析。建议重试或切换到其他适配器。"
}
```

## 2. 前端可视化 API

### 2.1 数据加载接口

**GET /api/analysis/{project_id}**

获取完整的分析结果数据。

**请求**：
- Method: GET
- Path: `/api/analysis/{project_id}`
- Query Parameters:
  - `version` (optional): 数据版本号（默认最新版本）
  - `include_cache` (optional): 是否包含缓存元数据（默认 false）

**响应**：
- Status: 200 OK
- Content-Type: application/json
- Body: 完整的标准数据协议 JSON（符合 `analysis-schema-v1.0.0.json`）

**示例**：

```http
GET /api/analysis/proj-abc123?version=1.0.0 HTTP/1.1
Host: localhost:8000
Accept: application/json
```

```json
{
  "$schema": "https://aiflow.dev/schemas/analysis-v1.0.0.json",
  "version": "1.0.0",
  "project_metadata": {
    "project_name": "auth-service",
    "project_path": "/path/to/project",
    "language": "python",
    "framework": "fastapi",
    "analyzed_at": "2025-10-09T10:00:00Z"
  },
  "code_structure": {
    "nodes": [...],
    "edges": [...]
  },
  "execution_trace": {
    "traceable_units": [...]
  }
}
```

### 2.2 增量更新接口

**POST /api/analysis/{project_id}/incremental**

触发增量分析（仅重新分析变更部分）。

**请求**：
- Method: POST
- Path: `/api/analysis/{project_id}/incremental`
- Content-Type: application/json
- Body:
  ```json
  {
    "changed_files": [
      "/path/to/changed/file1.py",
      "/path/to/changed/file2.py"
    ],
    "force_full": false
  }
  ```

**响应**：
- Status: 202 Accepted（异步任务）
- Content-Type: application/json
- Body:
  ```json
  {
    "job_id": "job-123",
    "status": "pending",
    "estimated_duration": 120.0,
    "created_at": "2025-10-09T11:00:00Z"
  }
  ```

### 2.3 任务状态查询接口

**GET /api/jobs/{job_id}**

查询分析任务状态。

**请求**：
- Method: GET
- Path: `/api/jobs/{job_id}`

**响应**：
- Status: 200 OK
- Content-Type: application/json
- Body:
  ```json
  {
    "job_id": "job-123",
    "status": "running",
    "progress": 0.45,
    "current_stage": "semantic_analysis",
    "stages": [
      {
        "stage": "project_understanding",
        "status": "completed",
        "duration": 30.0
      },
      {
        "stage": "structure_recognition",
        "status": "completed",
        "duration": 60.0
      },
      {
        "stage": "semantic_analysis",
        "status": "running",
        "estimated_remaining": 40.0
      }
    ],
    "created_at": "2025-10-09T11:00:00Z",
    "updated_at": "2025-10-09T11:02:00Z"
  }
  ```

### 2.4 动画控制接口

**WebSocket /ws/animation/{scene_id}**

实时动画控制 WebSocket 连接。

**消息格式（客户端 → 服务端）**：

```json
{
  "action": "play",
  "scene_id": "scene-001",
  "speed": 1.0
}
```

**支持的 action**：
- `play`: 播放动画
- `pause`: 暂停动画
- `seek`: 时间回溯
- `set_speed`: 设置播放速度
- `step_forward`: 单步前进
- `step_backward`: 单步后退

**消息格式（服务端 → 客户端）**：

```json
{
  "event": "animation_update",
  "scene_id": "scene-001",
  "current_time": 15.5,
  "active_nodes": ["node-001", "node-003"],
  "active_flows": ["flow-001"],
  "variable_snapshot": {
    "scope_id": "scope-001",
    "variables": [...]
  }
}
```

## 3. Prompt 模板接口

### 3.1 模板注册

Prompt 模板通过 YAML 文件注册，存储在 `prompts/registry.yaml`。

**registry.yaml 示例**：

```yaml
version: "1.0.0"
templates:
  - id: "python-structure-recognition-v1.1.0"
    version: "1.1.0"
    stage: "structure_recognition"
    target_language: "python"
    file_path: "prompts/python/structure-recognition/v1.1.0.yaml"
    status: "active"
    created_at: "2025-10-01T00:00:00Z"
    updated_at: "2025-10-05T10:00:00Z"
    test_results:
      accuracy: 0.89
      consistency: 0.96
      last_tested: "2025-10-05T10:00:00Z"

  - id: "javascript-semantic-analysis-v1.0.0"
    version: "1.0.0"
    stage: "semantic_analysis"
    target_language: "javascript"
    file_path: "prompts/javascript/semantic-analysis/v1.0.0.yaml"
    status: "active"
    created_at: "2025-09-15T00:00:00Z"
    updated_at: "2025-09-15T00:00:00Z"
```

### 3.2 模板文件格式

**prompts/python/structure-recognition/v1.1.0.yaml 示例**：

```yaml
id: "python-structure-recognition-v1.1.0"
version: "1.1.0"
stage: "structure_recognition"
target_language: "python"
description: "Python 项目代码结构识别，生成层级化节点和边关系"

input_schema:
  type: "object"
  required: ["source_files"]
  properties:
    source_files:
      type: "array"
      items:
        type: "object"
        properties:
          path: { type: "string" }
          content: { type: "string" }

output_schema:
  type: "object"
  required: ["nodes", "edges"]
  properties:
    nodes:
      type: "array"
      items:
        $ref: "#/definitions/CodeNode"
    edges:
      type: "array"
      items:
        $ref: "#/definitions/CodeEdge"

quality_criteria:
  min_confidence: 0.8
  min_nodes: 5
  max_nodes: 1000
  required_node_types: ["module", "class", "function"]

template: |
  你是一个专业的 Python 代码分析专家。请分析以下 Python 项目的代码结构，生成层级化的节点和边关系。

  ## 输入数据
  {% for file in source_files %}
  ### {{ file.path }}
  ```python
  {{ file.content }}
  ```
  {% endfor %}

  ## 分析要求
  1. 识别所有模块（Module）、类（Class）、函数（Function）
  2. 生成业务语义化的节点名称（如"用户认证模块"而非"AuthService"）
  3. 标识节点间的依赖关系（dependency）、继承关系（inheritance）、调用关系（call）
  4. 为每个节点提供置信度分数（0.0-1.0）和决策解释

  ## 输出格式
  请严格按照以下 JSON Schema 输出：
  {{ output_schema | tojson }}

  ## 示例输出
  ```json
  {
    "nodes": [
      {
        "id": "node-001",
        "label": "用户认证模块",
        "parent": null,
        "classes": ["module", "security"],
        "stereotype": "module",
        "metadata": {
          "ai_confidence": 0.92,
          "ai_explanation": "该模块负责处理用户登录、注销和会话管理",
          "code_location": {
            "file_path": "src/auth/service.py",
            "start_line": 1,
            "end_line": 150
          }
        }
      }
    ],
    "edges": [
      {
        "id": "edge-001",
        "source": "node-001",
        "target": "node-002",
        "type": "dependency",
        "label": "使用"
      }
    ]
  }
  ```

  现在，请开始分析。

examples:
  - input:
      source_files:
        - path: "src/auth.py"
          content: |
            class AuthService:
                def login(self, username, password):
                    pass
    output:
      nodes:
        - id: "node-001"
          label: "用户认证服务"
          stereotype: "class"
          metadata:
            ai_confidence: 0.88
      edges: []
```

## 4. 缓存管理接口

### 4.1 缓存查询

**GET /api/cache/{project_hash}**

查询是否存在有效缓存。

**响应**：

```json
{
  "cache_exists": true,
  "cache_id": "cache-abc123",
  "project_hash": "sha256-...",
  "stage": "structure_recognition",
  "created_at": "2025-10-08T10:00:00Z",
  "hit_count": 5,
  "is_valid": true
}
```

### 4.2 缓存失效

**DELETE /api/cache/{cache_id}**

手动使缓存失效。

**响应**：

```json
{
  "success": true,
  "cache_id": "cache-abc123",
  "deleted_at": "2025-10-09T12:00:00Z"
}
```

## 5. 错误处理规范

### 5.1 错误响应格式

所有 API 错误使用统一格式：

```json
{
  "error": {
    "code": "ADAPTER_TIMEOUT",
    "message": "AI 适配器调用超时（120 秒）",
    "details": {
      "adapter_id": "claude-code-adapter",
      "request_id": "req-001-abc123",
      "timeout_seconds": 120
    },
    "timestamp": "2025-10-09T11:00:00Z",
    "retry_after": 60
  }
}
```

### 5.2 错误码定义

| 错误码 | HTTP 状态 | 描述 | 是否可重试 |
|--------|----------|------|----------|
| `ADAPTER_TIMEOUT` | 504 | AI 适配器调用超时 | ✅ |
| `ADAPTER_CONNECTION_ERROR` | 503 | 无法连接到 AI 适配器 | ✅ |
| `ADAPTER_VALIDATION_ERROR` | 422 | AI 返回数据验证失败 | ❌ |
| `PROJECT_NOT_FOUND` | 404 | 项目不存在 | ❌ |
| `INVALID_REQUEST` | 400 | 请求参数错误 | ❌ |
| `RATE_LIMIT_EXCEEDED` | 429 | 超过速率限制 | ✅ |
| `INTERNAL_ERROR` | 500 | 内部服务器错误 | ✅ |

## 6. 版本兼容性

### 6.1 API 版本控制

API 使用路径版本控制：
- `/api/v1/...` - 当前稳定版本
- `/api/v2/...` - 下一个主版本（破坏性变更）

### 6.2 数据格式版本

数据格式通过 `$schema` 字段标识版本：
- `https://aiflow.dev/schemas/analysis-v1.0.0.json` - 当前版本
- 向后兼容至少 2 个 MAJOR 版本

### 6.3 弃用策略

- 破坏性 API 变更必须提前 6 个月通知
- 弃用的 API 使用 `Deprecated` HTTP 头标识
- 弃用的字段使用 `deprecated: true` 标注

```json
{
  "old_field": "value",
  "deprecated": true,
  "use_instead": "new_field"
}
```

## 7. 性能要求

### 7.1 响应时间

- 数据加载接口：P95 <500ms，P99 <1s
- 增量更新触发：P95 <100ms（异步任务）
- 任务状态查询：P95 <200ms
- WebSocket 消息延迟：<50ms

### 7.2 并发支持

- 单服务器支持 ≥100 并发连接
- WebSocket 支持 ≥50 并发动画会话
- 分析任务队列支持 ≥10 并发任务

### 7.3 数据大小限制

- 单次请求最大 body 大小：10MB
- WebSocket 消息最大大小：1MB
- 分析结果文件最大大小：100MB（启用分页）

## 8. AI 分析结果验证规则

### 8.1 数据完整性验证

所有 AI 适配器返回的分析结果必须通过以下验证层级：

#### 8.1.1 JSON Schema 验证（强制）

**验证时机**: AI 适配器返回后立即验证

**验证工具**: `jsonschema` Python 库 + `analysis-schema-v1.0.0.json`

**验证内容**:
- 必需字段存在性检查
- 字段类型正确性验证
- 枚举值合法性检查
- 格式约束验证（如 ISO 8601 时间戳、UUID v4、正则表达式模式）

**示例代码**:
```python
from jsonschema import validate, ValidationError
import json

def validate_analysis_result(result: dict, schema_path: str) -> tuple[bool, str]:
    """
    验证 AI 分析结果是否符合 JSON Schema

    Args:
        result: AI 返回的分析结果
        schema_path: JSON Schema 文件路径

    Returns:
        (is_valid, error_message): 验证结果和错误信息
    """
    try:
        with open(schema_path, 'r') as f:
            schema = json.load(f)

        validate(instance=result, schema=schema)
        return True, ""
    except ValidationError as e:
        return False, f"JSON Schema 验证失败: {e.message} at path {e.json_path}"
```

**失败处理**:
- 验证失败时返回 `AdapterValidationError`
- 记录详细验证错误到日志
- 拒绝该分析结果，不进入后续处理流程

#### 8.1.2 引用完整性验证（强制）

**验证时机**: JSON Schema 验证通过后

**验证规则**:

1. **节点引用完整性**
   - `CodeEdge.source` 和 `CodeEdge.target` 必须引用 `code_structure.nodes` 中存在的节点 ID
   - `CodeNode.parent` 必须引用 `code_structure.nodes` 中存在的父节点 ID
   - 不允许循环父子关系（无环图约束）

2. **轨迹单元引用完整性**
   - `LaunchButton.node_id` 必须引用 `code_structure.nodes` 中存在的节点 ID
   - `TraceableUnit.subUnitIds` 必须引用 `execution_trace.traceable_units` 中存在的子单元 ID
   - 不允许循环依赖关系

3. **作用域引用完整性**
   - `Step.scope_id` 必须引用 `variableScopes` 中存在的作用域 ID
   - `VariableScope.parent_scope_id` 必须引用 `variableScopes` 中存在的父作用域 ID
   - `StackFrame.local_scope_id` 必须引用 `variableScopes` 中存在的作用域 ID
   - `StackFrame.parent_frame_id` 必须引用 `callStack` 中存在的父栈帧 ID

4. **并发流引用完整性**
   - `ConcurrencyFlow.involved_units` 必须引用 `code_structure.nodes` 或 `execution_trace.traceable_units` 中存在的单元 ID
   - `SyncPoint.waiting_flows` 必须引用 `concurrency_info.flows` 中存在的并发流 ID

**示例代码**:
```python
def validate_references(data: dict) -> tuple[bool, list[str]]:
    """
    验证引用完整性

    Returns:
        (is_valid, error_messages): 验证结果和错误信息列表
    """
    errors = []

    # 构建节点 ID 集合
    node_ids = {node['id'] for node in data.get('code_structure', {}).get('nodes', [])}

    # 验证边引用
    for edge in data.get('code_structure', {}).get('edges', []):
        if edge['source'] not in node_ids:
            errors.append(f"Edge {edge['id']} source '{edge['source']}' does not exist")
        if edge['target'] not in node_ids:
            errors.append(f"Edge {edge['id']} target '{edge['target']}' does not exist")

    # 验证父节点引用
    for node in data.get('code_structure', {}).get('nodes', []):
        if 'parent' in node and node['parent']:
            if node['parent'] not in node_ids:
                errors.append(f"Node {node['id']} parent '{node['parent']}' does not exist")

    # 验证循环依赖
    if has_circular_parent_references(data.get('code_structure', {}).get('nodes', [])):
        errors.append("Circular parent-child relationships detected in code_structure")

    # ... 其他引用验证规则 ...

    return len(errors) == 0, errors
```

**失败处理**:
- 验证失败时返回 `AdapterValidationError`
- 记录所有引用错误到日志
- 提示 AI 适配器修复引用错误并重新生成

#### 8.1.3 业务逻辑验证（警告级别）

**验证时机**: 引用完整性验证通过后

**验证规则**:

1. **合理性检查**
   - 节点数量在预期范围内（5-5000 个节点）
   - 边数量与节点数量比例合理（边/节点 ≤ 3）
   - 层级深度合理（≤ 10 层）

2. **置信度检查**
   - 所有 AI 决策的置信度分数在 [0.0, 1.0] 范围内
   - 平均置信度 ≥ 0.6（低于阈值时生成警告）
   - 置信度 < 0.5 的节点标记为"不确定"

3. **语义一致性检查**
   - 节点名称不应为空或仅包含通用名称（如"Function", "Module"）
   - 节点类型（stereotype）与代码位置一致（如 module 对应目录，class 对应类定义）

**示例代码**:
```python
def validate_business_logic(data: dict) -> list[str]:
    """
    业务逻辑验证（警告级别）

    Returns:
        warnings: 警告信息列表
    """
    warnings = []

    # 节点数量检查
    node_count = len(data.get('code_structure', {}).get('nodes', []))
    if node_count < 5:
        warnings.append(f"Node count {node_count} is suspiciously low (expected ≥5)")
    elif node_count > 5000:
        warnings.append(f"Node count {node_count} is very high (expected ≤5000)")

    # 置信度检查
    confidences = [
        node.get('metadata', {}).get('ai_confidence', 1.0)
        for node in data.get('code_structure', {}).get('nodes', [])
    ]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

    if avg_confidence < 0.6:
        warnings.append(f"Average AI confidence {avg_confidence:.2f} is below threshold (0.6)")

    low_confidence_nodes = [
        node['id'] for node in data.get('code_structure', {}).get('nodes', [])
        if node.get('metadata', {}).get('ai_confidence', 1.0) < 0.5
    ]
    if low_confidence_nodes:
        warnings.append(f"{len(low_confidence_nodes)} nodes have low confidence (<0.5): {low_confidence_nodes[:5]}...")

    # ... 其他业务逻辑验证 ...

    return warnings
```

**警告处理**:
- 警告不阻止分析结果使用
- 记录警告到日志和元数据
- 在可视化界面中标注警告区域

### 8.2 时间戳格式验证

**严格要求**: 所有时间戳字段必须符合 ISO 8601 格式规范

**适用字段**:
- `project_metadata.analyzed_at`
- `prompt_templates.used_prompts[*].executed_at`
- `Step.timestamp`
- `VariableScope.timestamp`
- `VariableChange.timestamp`
- `StackFrame.timestamp`
- `ResultMetadata.timestamp`

**验证规则**:
```python
import re
from datetime import datetime

ISO_8601_PATTERN = re.compile(
    r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$'
)

def validate_timestamp_format(timestamp: str) -> bool:
    """
    验证时间戳是否符合 ISO 8601 格式

    Args:
        timestamp: 时间戳字符串

    Returns:
        True if valid ISO 8601 format, False otherwise

    Examples:
        Valid:
        - "2025-10-10T14:30:00Z"
        - "2025-10-10T14:30:00.123Z"
        - "2025-10-10T14:30:00+08:00"
        - "2025-10-10T14:30:00.123+08:00"

        Invalid:
        - "2025-10-10 14:30:00" (space instead of 'T')
        - "2025-10-10T14:30:00" (missing timezone)
        - "1633889400" (Unix timestamp)
    """
    if not ISO_8601_PATTERN.match(timestamp):
        return False

    # Additional validation: parse to ensure valid date/time
    try:
        datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return True
    except ValueError:
        return False
```

**失败处理**:
- 时间戳格式错误时返回 `AdapterValidationError`
- 记录所有格式错误的字段路径
- 提示 AI 适配器修正时间戳格式

### 8.3 Execution Order 验证

**验证目的**: 确保全局执行序号的一致性和正确性

**验证规则**:

1. **全局唯一性**
   - 所有 `execution_order` 值在同一分析结果中全局唯一
   - 不允许重复的 `execution_order` 值

2. **单调递增性**
   - `execution_order` 值必须随时间严格递增
   - 按 `timestamp` 排序后，`execution_order` 必须同样递增

3. **连续性检查（警告级别）**
   - 检测 `execution_order` 是否连续（0, 1, 2, 3...）
   - 允许存在跳跃（如 0, 1, 5, 6...），但生成警告

**示例代码**:
```python
def validate_execution_order(data: dict) -> tuple[bool, list[str], list[str]]:
    """
    验证 execution_order 的全局一致性

    Returns:
        (is_valid, errors, warnings): 验证结果、错误列表、警告列表
    """
    errors = []
    warnings = []

    # 收集所有 execution_order 及其来源
    execution_orders = []

    # 从 steps 中收集
    for trace_unit in data.get('execution_trace', {}).get('traceable_units', []):
        for trace in trace_unit.get('traces', []):
            if trace.get('format') == 'step-by-step':
                for step in trace['data'].get('steps', []):
                    execution_orders.append({
                        'order': step['execution_order'],
                        'timestamp': step['timestamp'],
                        'source': f"step {step['id']}"
                    })

    # 从 variableScopes 中收集
    # 从 callStack 中收集
    # ... (类似逻辑)

    # 检查唯一性
    order_values = [item['order'] for item in execution_orders]
    duplicates = [x for x in set(order_values) if order_values.count(x) > 1]
    if duplicates:
        errors.append(f"Duplicate execution_order values found: {duplicates}")

    # 检查单调递增性
    sorted_by_time = sorted(execution_orders, key=lambda x: x['timestamp'])
    for i in range(1, len(sorted_by_time)):
        if sorted_by_time[i]['order'] <= sorted_by_time[i-1]['order']:
            errors.append(
                f"execution_order is not monotonically increasing: "
                f"{sorted_by_time[i-1]['source']} (order={sorted_by_time[i-1]['order']}) "
                f"comes before {sorted_by_time[i]['source']} (order={sorted_by_time[i]['order']}) "
                f"but has same or higher order value"
            )

    # 检查连续性（警告级别）
    sorted_orders = sorted(order_values)
    gaps = []
    for i in range(1, len(sorted_orders)):
        if sorted_orders[i] - sorted_orders[i-1] > 1:
            gaps.append((sorted_orders[i-1], sorted_orders[i]))

    if gaps:
        warnings.append(f"Non-continuous execution_order detected: gaps at {gaps[:5]}...")

    return len(errors) == 0, errors, warnings
```

**失败处理**:
- 唯一性或单调性错误时返回 `AdapterValidationError`
- 连续性警告不阻止使用
- 记录所有验证结果到日志

### 8.4 递归调用栈验证

**验证目的**: 确保递归调用栈的正确性和一致性

**验证规则**:

1. **递归标识一致性**
   - 当 `StackFrame.is_recursive = true` 时，必须提供 `recursion_depth` 字段
   - 当 `StackFrame.is_recursive = false` 时，`recursion_depth` 应为 0 或不存在

2. **递归深度合理性**
   - `recursion_depth` 必须为非负整数
   - `recursion_depth` 应与实际递归层级一致（通过 `parent_frame_id` 追溯验证）

3. **递归终止检查（警告级别）**
   - 检测递归深度是否超过合理阈值（如 >100 层）
   - 生成警告提示潜在的无限递归

**示例代码**:
```python
def validate_recursive_call_stack(call_stack: list[dict]) -> tuple[bool, list[str], list[str]]:
    """
    验证递归调用栈的正确性

    Returns:
        (is_valid, errors, warnings): 验证结果、错误列表、警告列表
    """
    errors = []
    warnings = []

    for frame in call_stack:
        is_recursive = frame.get('is_recursive', False)
        recursion_depth = frame.get('recursion_depth')

        # 递归标识一致性检查
        if is_recursive and recursion_depth is None:
            errors.append(
                f"StackFrame {frame['id']} has is_recursive=true but missing recursion_depth"
            )
        elif not is_recursive and recursion_depth is not None and recursion_depth != 0:
            errors.append(
                f"StackFrame {frame['id']} has is_recursive=false but recursion_depth={recursion_depth}"
            )

        # 递归深度合理性检查
        if recursion_depth is not None:
            if recursion_depth < 0:
                errors.append(
                    f"StackFrame {frame['id']} has negative recursion_depth={recursion_depth}"
                )
            elif recursion_depth > 100:
                warnings.append(
                    f"StackFrame {frame['id']} has very deep recursion_depth={recursion_depth} (potential infinite recursion)"
                )

    return len(errors) == 0, errors, warnings
```

**失败处理**:
- 递归标识或深度错误时返回 `AdapterValidationError`
- 深度警告不阻止使用
- 在可视化界面中标注深递归区域

### 8.5 置信度阈值验证

**验证目的**: 确保 AI 分析质量达到最低可接受标准

**阶段性置信度阈值**:

| 分析阶段 | 最低置信度阈值 | 推荐置信度阈值 | 验证级别 |
|---------|---------------|---------------|---------|
| Project Understanding | 0.70 | 0.85 | 强制 |
| Structure Recognition | 0.80 | 0.90 | 强制 |
| Semantic Analysis | 0.70 | 0.85 | 强制 |
| Execution Inference | 0.60 | 0.80 | 警告 |
| Concurrency Detection | 0.60 | 0.80 | 警告 |

**验证规则**:

1. **整体置信度验证**
   - `AnalysisResult.confidence` 必须 ≥ 阶段最低阈值
   - 低于阈值时返回验证错误或警告（根据验证级别）

2. **节点级置信度验证**
   - 关键节点（stereotype = "system", "module"）的 `ai_confidence` 必须 ≥ 0.8
   - 普通节点的 `ai_confidence` 推荐 ≥ 0.7
   - 低置信度节点（< 0.5）标记为"不确定"

3. **置信度分布检查（警告级别）**
   - 计算置信度分布的标准差
   - 标准差过大（> 0.3）时生成警告，提示 AI 分析质量不稳定

**示例代码**:
```python
def validate_confidence_thresholds(
    result: dict,
    stage: str,
    thresholds: dict[str, dict]
) -> tuple[bool, list[str], list[str]]:
    """
    验证置信度阈值

    Args:
        result: AI 分析结果
        stage: 分析阶段名称
        thresholds: 阶段置信度阈值配置

    Returns:
        (is_valid, errors, warnings): 验证结果、错误列表、警告列表
    """
    errors = []
    warnings = []

    stage_config = thresholds.get(stage, {})
    min_threshold = stage_config.get('min', 0.6)
    recommended_threshold = stage_config.get('recommended', 0.8)
    validation_level = stage_config.get('level', 'warning')

    # 整体置信度验证
    overall_confidence = result.get('confidence', 0.0)

    if overall_confidence < min_threshold:
        message = (
            f"Overall confidence {overall_confidence:.2f} is below minimum threshold "
            f"{min_threshold:.2f} for stage '{stage}'"
        )
        if validation_level == 'error':
            errors.append(message)
        else:
            warnings.append(message)
    elif overall_confidence < recommended_threshold:
        warnings.append(
            f"Overall confidence {overall_confidence:.2f} is below recommended threshold "
            f"{recommended_threshold:.2f} for stage '{stage}'"
        )

    # 节点级置信度验证
    nodes = result.get('data', {}).get('nodes', [])
    low_confidence_critical_nodes = [
        node for node in nodes
        if node.get('stereotype') in ['system', 'module']
        and node.get('metadata', {}).get('ai_confidence', 1.0) < 0.8
    ]

    if low_confidence_critical_nodes:
        warnings.append(
            f"{len(low_confidence_critical_nodes)} critical nodes have low confidence (<0.8): "
            f"{[node['id'] for node in low_confidence_critical_nodes[:5]]}..."
        )

    # 置信度分布检查
    confidences = [
        node.get('metadata', {}).get('ai_confidence', 1.0)
        for node in nodes
    ]
    if confidences:
        import statistics
        std_dev = statistics.stdev(confidences)
        if std_dev > 0.3:
            warnings.append(
                f"Confidence distribution has high standard deviation ({std_dev:.2f}), "
                "indicating unstable AI analysis quality"
            )

    return len(errors) == 0, errors, warnings
```

**失败处理**:
- 强制级别错误时返回 `AdapterValidationError`
- 警告级别错误不阻止使用
- 记录所有置信度验证结果到元数据

### 8.6 验证管道集成

**完整验证流程**:

```python
class AnalysisResultValidator:
    """AI 分析结果验证管道"""

    def __init__(self, schema_path: str, thresholds_config: dict):
        self.schema_path = schema_path
        self.thresholds_config = thresholds_config

    def validate(self, result: dict, stage: str) -> ValidationResult:
        """
        执行完整验证管道

        Args:
            result: AI 分析结果
            stage: 分析阶段名称

        Returns:
            ValidationResult: 包含 is_valid, errors, warnings
        """
        all_errors = []
        all_warnings = []

        # 1. JSON Schema 验证（强制）
        schema_valid, schema_error = validate_analysis_result(
            result, self.schema_path
        )
        if not schema_valid:
            all_errors.append(schema_error)
            return ValidationResult(
                is_valid=False,
                errors=all_errors,
                warnings=all_warnings
            )

        # 2. 引用完整性验证（强制）
        ref_valid, ref_errors = validate_references(result)
        all_errors.extend(ref_errors)

        # 3. 时间戳格式验证（强制）
        timestamp_valid, timestamp_errors = validate_all_timestamps(result)
        all_errors.extend(timestamp_errors)

        # 4. Execution Order 验证（强制）
        order_valid, order_errors, order_warnings = validate_execution_order(result)
        all_errors.extend(order_errors)
        all_warnings.extend(order_warnings)

        # 5. 递归调用栈验证（强制）
        recursive_valid, recursive_errors, recursive_warnings = validate_recursive_call_stack(
            result.get('data', {}).get('callStack', [])
        )
        all_errors.extend(recursive_errors)
        all_warnings.extend(recursive_warnings)

        # 6. 置信度阈值验证（阶段依赖）
        confidence_valid, confidence_errors, confidence_warnings = validate_confidence_thresholds(
            result, stage, self.thresholds_config
        )
        all_errors.extend(confidence_errors)
        all_warnings.extend(confidence_warnings)

        # 7. 业务逻辑验证（警告级别）
        business_warnings = validate_business_logic(result)
        all_warnings.extend(business_warnings)

        is_valid = len(all_errors) == 0

        return ValidationResult(
            is_valid=is_valid,
            errors=all_errors,
            warnings=all_warnings
        )
```

**使用示例**:

```python
# 在 AI 适配器层使用
validator = AnalysisResultValidator(
    schema_path="shared/schemas/analysis-schema-v1.0.0.json",
    thresholds_config={
        'project_understanding': {'min': 0.70, 'recommended': 0.85, 'level': 'error'},
        'structure_recognition': {'min': 0.80, 'recommended': 0.90, 'level': 'error'},
        'semantic_analysis': {'min': 0.70, 'recommended': 0.85, 'level': 'error'},
        'execution_inference': {'min': 0.60, 'recommended': 0.80, 'level': 'warning'},
        'concurrency_detection': {'min': 0.60, 'recommended': 0.80, 'level': 'warning'},
    }
)

# 验证 AI 返回结果
result = await ai_adapter.analyze(request)
validation_result = validator.validate(result, stage=request['stage'])

if not validation_result.is_valid:
    raise AdapterValidationError(
        f"AI analysis result validation failed: {validation_result.errors}"
    )

if validation_result.warnings:
    logger.warning(f"Validation warnings: {validation_result.warnings}")
```

---

**最后更新**: 2025-10-10 | **版本**: 1.1.0 | **状态**: Draft
