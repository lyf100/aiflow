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

---

**最后更新**: 2025-10-09 | **版本**: 1.0.0 | **状态**: Draft
