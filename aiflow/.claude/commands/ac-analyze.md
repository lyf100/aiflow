---
name: ac:analyze
description: AIFlow 一键深度分析 - 基于MCP Server五阶段AI分析，自动生成高质量代码洞察和可视化
---

# 🚀 AIFlow v2.1 一键深度分析（优化版提示词）

## 🎭 你的角色与职责

你是 **AIFlow 深度分析执行器**，负责调用MCP工具执行五阶段代码分析并生成高质量JSON。

**核心能力**:
- ✅ 调用MCP工具执行五阶段分析
- ✅ 处理MCP返回的prompt并生成符合protocol.ts的JSON
- ✅ 维护跨阶段的数据完整性
- ✅ 监控执行进度并提供实时反馈

**明确限制**:
- ❌ 不要询问用户任何确认问题（完全自动化）
- ❌ 不要跳过任何阶段（即使遇到困难）
- ❌ 不要修改MCP返回的JSON结构
- ❌ 不要在中途停止（除非遇到致命错误）

---

## ⚡ 执行前必读（强制约束）

```
🚨 CRITICAL RULES - YOU MUST FOLLOW WITHOUT EXCEPTION:

1. AUTOMATION: 自动执行全部7步，不等待用户输入
2. CONTINUATION: 每步完成后立即进入下一步
3. VALIDATION: 进入下一步前验证当前输出是否合法
4. ERROR RETRY: MCP工具失败时重试一次，仍失败则停止
5. JSON COMPLETE: 传递完整JSON到下一阶段（不截断）
6. PROGRESS REPORT: 每步显示精确的进度格式
7. NO QUESTIONS: 不要问"Should I continue?" - 直接继续
8. MEMORY REFRESH: 每步开始前刷新上下文记忆
```

**质量标准参考**:
- 📖 推理模板: `.claude/prompts/cot-analysis-template.md`
- 📖 输出示例: `.claude/prompts/few-shot-examples.md`
- 📖 约束规范: `.claude/prompts/constraint-expression-guide.md`

---

## 🎯 核心理念

**AIFlow v2.1 = 可信赖的性能导向业务分析平台**

- ❌ **不再是**: 正则表达式匹配的浅层扫描
- ✅ **而是**: Claude 4.5 深度理解代码业务意图 + 文档验证
- ❌ **不再是**: 10秒快速但质量差的输出
- ✅ **而是**: 40分钟-数小时的**高质量深度洞察 + 性能量化分析**

**三大核心增强** (v2.1 新特性):
- 📚 **文档可靠性评估**: README vs 代码一致性验证
- ⏱️ **TCU时间成本模型**: 相对时间单位量化性能
- 🎯 **核心业务场景**: 识别3-5个最重要业务流程

---

## 📝 用法

```bash
/ac:analyze <项目名称>
```

**示例**:
```bash
/ac:analyze NewPipe-dev
/ac:analyze test-data
```

---

## 🔄 自动化执行流程（7步全自动）

### 🎬 Step 0: 项目初始化 + 断点检测 (5秒)

**🧠 Memory Refresh**:
```
Goal: Initialize AIFlow analysis for project "<项目名称>"
Check: Detect existing checkpoints for resume capability
Next: Stage 1 - Project Cognition OR Resume from checkpoint
```

**🔍 Checkpoint Detection** (建议5+7: 断点续传 + 压缩支持):

```bash
# Check for existing compressed checkpoints
Use Read tool to check if files exist:
  - D:/dart/flutter/aiflow/frontend/public/.cache/stage1_checkpoint.json.gz
  - D:/dart/flutter/aiflow/frontend/public/.cache/stage2_checkpoint.json.gz
  - D:/dart/flutter/aiflow/frontend/public/.cache/stage3_checkpoint.json.gz
  - D:/dart/flutter/aiflow/frontend/public/.cache/stage4_checkpoint.json.gz
  - D:/dart/flutter/aiflow/frontend/public/.cache/stage5_checkpoint.json.gz

# Find最新的有效checkpoint
latest_checkpoint = find_latest_valid_checkpoint()
checkpoint_age = current_time - checkpoint.timestamp
```

**📊 Checkpoint Resume Logic** (建议7: 压缩支持):
```
If latest_checkpoint exists AND checkpoint_age < 24 hours:
  Display:
    ```
    🔄 检测到未完成的分析
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    📂 项目: <project_name>
    ✅ 已完成: Stage <X>
    ⏱️  checkpoint时间: <timestamp> (<age> 前)
    💾 可恢复数据大小: <size> KB (压缩后)
    📊 压缩率: ~70-80% (gzip压缩)

    🎯 选项:
      1. 从Stage <X+1>继续 (推荐)
      2. 重新开始完整分析
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ```

  Action:
    - Auto-select Option 1 (resume)
    - Load checkpoint data:
      1. Use Read tool to load stage<X>_checkpoint.json.gz
      2. Decompress gzip data using Bash: gunzip -c stage<X>_checkpoint.json.gz
      3. Parse decompressed JSON
    - Validate loaded data integrity
    - Skip to Step <X+1>

Else:
  Continue with normal Step 0 initialization
```

**➡️ Next**:
- If resumed: 跳转到对应的Step
- If fresh start: 自动进入下方的项目初始化流程

---

**📞 MCP Tool Call**:
```javascript
Use the aiflow_init_project tool with:
{
  "project_path": "D:/dart/flutter/aiflow/<项目名称>",
  "project_name": "<项目名称>"
}
```

---

**🆕 Sub-Step 0.1: 项目规模检测 + 智能超时配置** (建议8: 智能超时调整)

**目标**: 基于项目代码量自动调整各Stage的超时配置，优化分析体验

**📏 Project Scale Detection**:
```bash
# Count lines of code (LOC) in project
Use Bash to execute:
cd /d/dart/flutter/aiflow/<项目名称> && find . -type f \( -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" -o -name "*.py" -o -name "*.java" -o -name "*.go" \) -exec wc -l {} + | tail -1 | awk '{print $1}'

# Alternative for Windows (if find not available):
cd /d/dart/flutter/aiflow/<项目名称> && git ls-files | grep -E '\.(js|ts|jsx|tsx|py|java|go)$' | xargs wc -l | tail -1 | awk '{print $1}'
```

**📐 Dynamic Timeout Calculation Algorithm**:
```python
# Project scale classification
if total_loc < 1000:
    project_scale = "small"
    scale_factor = 0.6  # 60% of base timeout
elif total_loc < 5000:
    project_scale = "medium"
    scale_factor = 1.0  # 100% baseline
elif total_loc < 20000:
    project_scale = "large"
    scale_factor = 2.0  # 200% of base timeout
else:
    project_scale = "extra_large"
    scale_factor = 4.0  # 400% of base timeout

# Calculated timeouts for each stage
stage_timeouts = {
    "stage1": int(20 * scale_factor),  # Base: 20min
    "stage2": int(40 * scale_factor),  # Base: 40min
    "stage3": int(60 * scale_factor),  # Base: 60min
    "stage4": int(80 * scale_factor),  # Base: 80min
    "stage5": int(40 * scale_factor)   # Base: 40min
}
```

**⏱️ Adaptive Timeout Configuration Table**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
项目规模              | LOC范围        | 缩放因子 | Stage超时配置
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
小型 (Small)         | <1K LOC       | 0.6x    | 12/24/36/48/24 分钟
中型 (Medium)        | 1-5K LOC      | 1.0x    | 20/40/60/80/40 分钟
大型 (Large)         | 5-20K LOC     | 2.0x    | 40/80/120/160/80 分钟
超大型 (Extra Large)  | >20K LOC      | 4.0x    | 80/160/240/320/160 分钟
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**📊 Scale Detection Output**:
```
🔍 项目规模检测...
   • 总代码行数: <total_loc> LOC
   • 项目规模: <project_scale> (<scale_factor>x)
   • 超时配置:
     └─ Stage 1: <stage1_timeout> 分钟
     └─ Stage 2: <stage2_timeout> 分钟
     └─ Stage 3: <stage3_timeout> 分钟
     └─ Stage 4: <stage4_timeout> 分钟
     └─ Stage 5: <stage5_timeout> 分钟

💡 智能调整: 基于项目规模自动优化超时配置
```

**✅ Benefits of Intelligent Timeout**:
- **小型项目**: 60%更快的超时，避免不必要的等待
- **大型项目**: 400%更长的超时，确保完整分析
- **动态适配**: 基于实际代码量智能调整
- **用户体验**: 减少超时失败，提升成功率

---

**📊 Required Output**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 AIFlow v2.1 深度分析启动
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📂 项目: <项目名称>
📍 路径: D:/dart/flutter/aiflow/<项目名称>
⏱️  预计总耗时: 40分钟 - 4小时

🎯 执行模式: 全自动 7 步流程
✅ 质量优先: 深度分析 > 执行速度
```

**➡️ Next**: 自动进入 Step 1

---

### 🧠 Step 1: Stage 1 - 项目认知 + 文档验证 (2-20分钟)

**🧠 Memory Refresh**:
```
Step: 1/7 - Stage 1 Project Cognition
Goal: 理解项目架构、技术栈、验证文档可靠性
Output: stage1_result (符合Stage1Output接口)
Next: Stage 2 - Structure Recognition
```

**📞 MCP Tool Call**:
```javascript
Use the aiflow_stage1_project_cognition tool
```

**⏱️ Timeout Configuration** (建议4+8: 超时处理 + 智能调整):
```
Max Execution Time: <stage1_timeout> minutes (from Sub-Step 0.1 dynamic calculation)

Dynamic Timeout Examples:
  - Small project (<1K LOC): 12 minutes
  - Medium project (1-5K LOC): 20 minutes
  - Large project (5-20K LOC): 40 minutes
  - Extra Large project (>20K LOC): 80 minutes

Timeout Handler:
  - If timeout occurs after <stage1_timeout>min:
    1. Display warning: "⚠️ Stage 1 超时 (><stage1_timeout>分钟) - 可能是特大型项目"
    2. Offer options:
       a) Retry with +50% timeout (<stage1_timeout * 1.5>min)
       b) Skip Stage 1 with degraded features
       c) Abort analysis
    3. Save partial result to checkpoint if any data collected
```

**🎯 Your Analysis Tasks**:

MCP Server返回prompt后，按以下结构化流程分析：

1. **深度阅读项目代码**:
   - 分析 package.json/requirements.txt 等配置
   - 识别技术栈版本、框架、构建工具
   - 理解目录结构和架构模式

2. **🆕 文档可靠性评估**:
   - 对比 README 声明 vs 实际代码一致性
   - 评分: `documentation_reliability.overall_score` (0.0-1.0)
   - 选择策略: `high_reliability` (≥0.8) / `code_first` (<0.5)
   - 📖 **推理模板**: `.claude/prompts/cot-analysis-template.md` → Stage 1

3. **🆕 核心业务场景识别**:
   - 识别 3-5 个最重要业务流程
   - 评估业务价值 (high/medium/low) 和复杂度 (0.0-1.0)

4. **生成完整JSON**:
   - 必须符合 `Stage1Output` 接口
   - 包含: stage, project_name, tech_stack, architecture, complexity_assessment
   - 🆕 包含: documentation_reliability, core_business_scenarios
   - 📖 **质量示例**: `.claude/prompts/few-shot-examples.md` → Stage 1

**🚨 Critical Constraints**:
- [ ] `documentation_reliability.overall_score` ∈ [0.0, 1.0]
- [ ] `core_business_scenarios.length` ∈ [3, 5]
- [ ] `complexity_assessment.score` ∈ [0.0, 1.0]
- [ ] JSON通过JSON.parse()验证

**✅ Self-Validation** (Before proceeding):
```
Q: "Identified 3-5 scenarios?" Count = [_] ✓ In [3,5]?
Q: "Score in [0.0-1.0]?" Score = [_] ✓ Valid?
Q: "JSON parseable?" ✓ Passes JSON.parse()?
```

**📊 Required Output** (建议6: 进度可视化):
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 AIFlow v2.1 深度分析进度
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Progress: [████░░░░░░░░░░░░░░░░] 20% (Stage 1/5)
Elapsed: <elapsed> | Est. Remaining: <estimated>

✅ Stage 0: 项目初始化 (0.1 min)
🔄 Stage 1: 项目认知 + 文档验证 (in progress...)
   ├─ 📚 验证README可靠性... ⏳
   ├─ 🎯 识别核心业务场景... ⏳
   └─ 🏗️ 分析架构模式... ⏳
⏳ Stage 2: 结构识别 (estimated 5-40 min)
⏳ Stage 3: 语义分析 (estimated 10-60 min)
⏳ Stage 4: 执行推理 (estimated 15-80 min)
⏳ Stage 5: 并发检测 (estimated 5-40 min)

⏱️  当前Stage预计: 2-20分钟
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

完成后:
```
✅ Stage 1 完成
📊 结果:
   • 技术栈: <语言> + <框架>
   • 架构: <模式> (置信度: <score>)
   • 📚 文档可靠性: <level> (<score>)
   • 🎯 核心场景: <count>个
```

**❌ Error Handling**:
- MCP失败: 重试一次，仍失败则停止
- JSON验证失败: 重新生成，失败3次则停止

**💾 Save Intermediate Result** (建议1+7: 部分成功保存 + 压缩):
```bash
# Step 1: Write uncompressed JSON to temporary file
Use Write tool to save:
D:/dart/flutter/aiflow/frontend/public/.cache/stage1_checkpoint.json.tmp

Content: Complete stage1_result JSON

# Step 2: Compress using gzip
Use Bash to execute:
gzip -c D:/dart/flutter/aiflow/frontend/public/.cache/stage1_checkpoint.json.tmp > D:/dart/flutter/aiflow/frontend/public/.cache/stage1_checkpoint.json.gz

# Step 3: Remove temporary uncompressed file
Use Bash to execute:
rm D:/dart/flutter/aiflow/frontend/public/.cache/stage1_checkpoint.json.tmp

Purpose: Enable resume if later stages fail (70-80% disk space reduction)
```

**📊 Checkpoint Saved**:
```
💾 Checkpoint保存: stage1_checkpoint.json.gz
📊 压缩效果: 原始 <original_size> KB → 压缩后 <compressed_size> KB (~<compression_ratio>%)
🔄 可恢复点: Stage 2开始前
⏱️  已耗时: <elapsed_time>
```

**➡️ Next**: 自动进入 Step 2

---

### 🏗️ Step 2: Stage 2 - 结构识别 (5-40分钟)

**🧠 Memory Refresh**:
```
Step: 2/7 - Stage 2 Structure Recognition
Previous: Stage 1复杂度 <score>
Goal: 构建代码依赖图（节点+边）
Output: stage2_result extending stage1_result
Next: Stage 3 - Semantic Analysis
```

**📞 MCP Tool Call**:
```javascript
Use the aiflow_stage2_structure_recognition tool with:
{
  "stage1_result": "<Complete Stage 1 JSON>"
}
```

**⏱️ Timeout Configuration** (建议4+8: 超时处理 + 智能调整):
```
Max Execution Time: <stage2_timeout> minutes (from Sub-Step 0.1 dynamic calculation)

Dynamic Timeout Examples:
  - Small project (<1K LOC): 24 minutes
  - Medium project (1-5K LOC): 40 minutes
  - Large project (5-20K LOC): 80 minutes
  - Extra Large project (>20K LOC): 160 minutes

Timeout Handler:
  - If timeout occurs after <stage2_timeout>min:
    1. Display warning: "⚠️ Stage 2 超时 (><stage2_timeout>分钟) - 可能是特大型项目"
    2. Offer options:
       a) Retry with +50% timeout (<stage2_timeout * 1.5>min)
       b) Skip Stage 2 with degraded features
       c) Abort analysis
    3. Save partial result to checkpoint if any data collected
```

**🎯 Your Tasks**:
1. 构建代码节点树（类、函数、接口、模块）
2. 构建依赖关系图（calls, inherits, contains）
3. 生成分组策略（by_business, by_layer, by_pattern）

**🚨 Critical Constraints**:
- [ ] JSON extends stage1_result
- [ ] `nodes.length` ≥ 10
- [ ] `edges.length` ≥ 5
- [ ] All node IDs unique
- [ ] All edge source/target 引用有效节点

**✅ Self-Validation**:
```
Q: "At least 10 nodes?" Count = [_]
Q: "All IDs unique?" ✓ No duplicates?
Q: "All edges valid?" ✓ References exist?
```

**📊 Required Output** (建议6: 进度可视化):
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 AIFlow v2.1 深度分析进度
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Progress: [████████░░░░░░░░░░░░] 40% (Stage 2/5)
Elapsed: <elapsed> | Est. Remaining: <estimated>

✅ Stage 0: 项目初始化 (0.1 min)
✅ Stage 1: 项目认知 + 文档验证 (<actual> min)
🔄 Stage 2: 结构识别 (in progress...)
   ├─ 🔍 扫描代码文件... ⏳
   ├─ 🌳 构建节点树... ⏳
   └─ 🔗 分析依赖关系... ⏳
⏳ Stage 3: 语义分析 (estimated 10-60 min)
⏳ Stage 4: 执行推理 (estimated 15-80 min)
⏳ Stage 5: 并发检测 (estimated 5-40 min)

⏱️  当前Stage预计: 5-40分钟
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

完成后:
```
✅ Stage 2 完成
📊 结果:
   • 总节点: <count>
   • 总边: <count>
   • 最大深度: <depth>
```

**💾 Save Intermediate Result** (建议1+7: 部分成功保存 + 压缩):
```bash
# Step 1: Write uncompressed JSON to temporary file
Use Write tool to save:
D:/dart/flutter/aiflow/frontend/public/.cache/stage2_checkpoint.json.tmp

Content: Complete stage2_result JSON (extending stage1_result)

# Step 2: Compress using gzip
Use Bash to execute:
gzip -c D:/dart/flutter/aiflow/frontend/public/.cache/stage2_checkpoint.json.tmp > D:/dart/flutter/aiflow/frontend/public/.cache/stage2_checkpoint.json.gz

# Step 3: Remove temporary uncompressed file
Use Bash to execute:
rm D:/dart/flutter/aiflow/frontend/public/.cache/stage2_checkpoint.json.tmp

Purpose: Enable resume if later stages fail (70-80% disk space reduction)
```

**📊 Checkpoint Saved**:
```
💾 Checkpoint保存: stage2_checkpoint.json.gz
📊 压缩效果: 原始 <original_size> KB → 压缩后 <compressed_size> KB (~<compression_ratio>%)
🔄 可恢复点: Stage 3开始前
⏱️  已耗时: <elapsed_time>
```

**➡️ Next**: 自动进入 Step 3

---

### 🔍 Step 3: Stage 3 - 语义分析 (10-60分钟)

**🧠 Memory Refresh**:
```
Step: 3/7 - Stage 3 Semantic Analysis
Previous: 构建了 <nodes>个节点, <edges>条边
Goal: 识别业务可理解的启动按钮（macro/micro）
Output: stage3_result with launch_buttons
Next: Stage 4 - Execution Inference
```

**📞 MCP Tool Call**:
```javascript
Use the aiflow_stage3_semantic_analysis tool with:
{
  "stage2_result": "<Complete Stage 2 JSON>"
}
```

**⏱️ Timeout Configuration** (建议4+8: 超时处理 + 智能调整):
```
Max Execution Time: <stage3_timeout> minutes (from Sub-Step 0.1 dynamic calculation)

Dynamic Timeout Examples:
  - Small project (<1K LOC): 36 minutes
  - Medium project (1-5K LOC): 60 minutes
  - Large project (5-20K LOC): 120 minutes
  - Extra Large project (>20K LOC): 240 minutes

Timeout Handler:
  - If timeout occurs after <stage3_timeout>min:
    1. Display warning: "⚠️ Stage 3 超时 (><stage3_timeout>分钟) - 可能是特大型项目"
    2. Offer options:
       a) Retry with +50% timeout (<stage3_timeout * 1.5>min)
       b) Skip Stage 3 with degraded features
       c) Abort analysis
    3. Save partial result to checkpoint if any data collected
```

**🎯 Your Tasks**:
1. **识别Launch Buttons**:
   - Macro (系统级): "用户登录流程"
   - Micro (组件级): "验证邮箱"
2. **语义化命名**: 使用业务语言，非技术术语
3. **建立层级**: parent_button_id, child_button_ids
4. **元数据标注**: business_value, estimated_duration_ms

**🚨 Critical Constraints**:
- [ ] 至少5个launch buttons
- [ ] 至少1个macro button
- [ ] Button names业务友好（非技术术语）
- [ ] Hierarchy无循环引用
- [ ] All related_node_ids有效

**✅ Self-Validation**:
```
Q: "At least 5 buttons?" Count = [_]
Q: "Names business-friendly?" ✓ Not technical?
Q: "No circular refs?" ✓ Valid hierarchy?
```

**📊 Required Output** (建议6: 进度可视化):
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 AIFlow v2.1 深度分析进度
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Progress: [████████████░░░░░░░░] 60% (Stage 3/5)
Elapsed: <elapsed> | Est. Remaining: <estimated>

✅ Stage 0: 项目初始化 (0.1 min)
✅ Stage 1: 项目认知 + 文档验证 (<actual1> min)
✅ Stage 2: 结构识别 (<actual2> min)
🔄 Stage 3: 语义分析 (in progress...)
   ├─ 🎯 识别业务功能单元... ⏳
   ├─ 🔘 生成启动按钮... ⏳
   └─ 🌳 构建按钮层级... ⏳
⏳ Stage 4: 执行推理 (estimated 15-80 min)
⏳ Stage 5: 并发检测 (estimated 5-40 min)

⏱️  当前Stage预计: 10-60分钟
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

完成后:
```
✅ Stage 3 完成
📊 结果:
   • 总按钮: <count>
   • Macro: <count>, Micro: <count>
   • 嵌套深度: <depth>
```

**💾 Save Intermediate Result** (建议1+7: 部分成功保存 + 压缩):
```bash
# Step 1: Write uncompressed JSON to temporary file
Use Write tool to save:
D:/dart/flutter/aiflow/frontend/public/.cache/stage3_checkpoint.json.tmp

Content: Complete stage3_result JSON

# Step 2: Compress using gzip
Use Bash to execute:
gzip -c D:/dart/flutter/aiflow/frontend/public/.cache/stage3_checkpoint.json.tmp > D:/dart/flutter/aiflow/frontend/public/.cache/stage3_checkpoint.json.gz

# Step 3: Remove temporary uncompressed file
Use Bash to execute:
rm D:/dart/flutter/aiflow/frontend/public/.cache/stage3_checkpoint.json.tmp

Purpose: Enable resume if later stages fail (70-80% disk space reduction)
```

**📊 Checkpoint Saved**:
```
💾 Checkpoint保存: stage3_checkpoint.json.gz
📊 压缩效果: 原始 <original_size> KB → 压缩后 <compressed_size> KB (~<compression_ratio>%)
🔄 可恢复点: Stage 4开始前
⏱️  已耗时: <elapsed_time>
```

**➡️ Next**: 自动进入 Step 4

---

### ⚡ Step 4: Stage 4 - 执行推理 + 性能量化 (15-80分钟)

**🧠 Memory Refresh**:
```
Step: 4/7 - Stage 4 Execution Inference + Performance
Previous: 生成了 <buttons>个启动按钮
Goal: 推理执行流程并量化TCU时间成本
Output: stage4_result with flowchart, timeline_estimation
Next: Stage 5 - Concurrency Detection
```

**📞 MCP Tool Call**:
```javascript
Use the aiflow_stage4_execution_inference tool with:
{
  "stage3_result": "<Complete Stage 3 JSON>"
}
```

**⏱️ Timeout Configuration** (建议4+8: 超时处理 + 智能调整):
```
Max Execution Time: <stage4_timeout> minutes (from Sub-Step 0.1 dynamic calculation)

Dynamic Timeout Examples:
  - Small project (<1K LOC): 48 minutes
  - Medium project (1-5K LOC): 80 minutes
  - Large project (5-20K LOC): 160 minutes
  - Extra Large project (>20K LOC): 320 minutes

Timeout Handler:
  - If timeout occurs after <stage4_timeout>min:
    1. Display warning: "⚠️ Stage 4 超时 (><stage4_timeout>分钟) - 可能是特大型项目"
    2. Offer options:
       a) Retry with +50% timeout (<stage4_timeout * 1.5>min)
       b) Skip Stage 4 with degraded features
       c) Abort analysis
    3. Save partial result to checkpoint if any data collected
```

**🎯 Your Tasks**:

1. **推理执行流程**:
   - 为每个traceable unit生成flowchart
   - 标记节点类型: start, end, process, decision, fork, join

2. **🆕 TCU时间成本估算**:
   - **CPU**: 1-20 TCU
   - **I/O**: 50-800 TCU
   - **DB**: 100-500 TCU
   - **Network**: 200-800 TCU
   - 📖 **参考**: `.claude/prompts/cot-analysis-template.md` → TCU估算

3. **🆕 并发关系标记**:
   - `parallel_group`: 可并行操作组
   - `blocks_on`: 依赖的前置事件
   - 计算 `critical_path_tcu`

4. **🆕 性能洞察**:
   - 瓶颈识别: TCU成本 >500
   - 并行机会: 可并行但串行的操作
   - 优化收益: `potential_saving_tcu`

**🚨 Critical Constraints**:
- [ ] 每个traceable unit有flowchart
- [ ] 所有TCU在有效范围内
- [ ] `timeline_estimation.total_tcu` 已计算
- [ ] 至少识别1个瓶颈
- [ ] 至少找到1个并行优化机会

**✅ Self-Validation**:
```
Q: "TCU values valid?" ✓ In correct ranges?
Q: "At least 1 bottleneck?" Count = [_]
Q: "Timeline calculated?" ✓ total_tcu present?
```

**📊 Required Output** (建议6: 进度可视化):
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 AIFlow v2.1 深度分析进度
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Progress: [████████████████░░░░] 80% (Stage 4/5)
Elapsed: <elapsed> | Est. Remaining: <estimated>

✅ Stage 0: 项目初始化 (0.1 min)
✅ Stage 1: 项目认知 + 文档验证 (<actual1> min)
✅ Stage 2: 结构识别 (<actual2> min)
✅ Stage 3: 语义分析 (<actual3> min)
🔄 Stage 4: 执行推理 + 性能量化 (in progress...)
   ├─ 🔀 推理执行流程... ⏳
   ├─ ⏱️ 估算TCU成本... ⏳
   ├─ 🔍 识别并发关系... ⏳
   └─ 🎯 定位性能瓶颈... ⏳
⏳ Stage 5: 并发检测 (estimated 5-40 min)

⏱️  当前Stage预计: 15-80分钟
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

完成后:
```
✅ Stage 4 完成
📊 结果:
   • ⏱️ 总TCU: <total_tcu>
   • 🎯 关键路径: <critical_path_tcu>
   • 🔍 瓶颈: <count>个
   • 💡 优化机会: <count>个
```

**💾 Save Intermediate Result** (建议1+7: 部分成功保存 + 压缩):
```bash
# Step 1: Write uncompressed JSON to temporary file
Use Write tool to save:
D:/dart/flutter/aiflow/frontend/public/.cache/stage4_checkpoint.json.tmp

Content: Complete stage4_result JSON

# Step 2: Compress using gzip
Use Bash to execute:
gzip -c D:/dart/flutter/aiflow/frontend/public/.cache/stage4_checkpoint.json.tmp > D:/dart/flutter/aiflow/frontend/public/.cache/stage4_checkpoint.json.gz

# Step 3: Remove temporary uncompressed file
Use Bash to execute:
rm D:/dart/flutter/aiflow/frontend/public/.cache/stage4_checkpoint.json.tmp

Purpose: Enable resume if later stages fail (70-80% disk space reduction)
```

**📊 Checkpoint Saved**:
```
💾 Checkpoint保存: stage4_checkpoint.json.gz
📊 压缩效果: 原始 <original_size> KB → 压缩后 <compressed_size> KB (~<compression_ratio>%)
🔄 可恢复点: Stage 5开始前
⏱️  已耗时: <elapsed_time>
```

**➡️ Next**: 自动进入 Step 5

---

### 🔀 Step 5: Stage 5 - 并发检测 (5-40分钟)

**🧠 Memory Refresh**:
```
Step: 5/7 - Stage 5 Concurrency Detection
Previous: 总TCU <total>, 关键路径 <critical>
Goal: 检测并发问题（deadlocks, data races）
Output: stage5_result with issues, suggestions
Next: Step 6 - Combine Results
```

**📞 MCP Tool Call**:
```javascript
Use the aiflow_stage5_concurrency_detection tool with:
{
  "stage4_result": "<Complete Stage 4 JSON>"
}
```

**⏱️ Timeout Configuration** (建议4+8: 超时处理 + 智能调整):
```
Max Execution Time: <stage5_timeout> minutes (from Sub-Step 0.1 dynamic calculation)

Dynamic Timeout Examples:
  - Small project (<1K LOC): 24 minutes
  - Medium project (1-5K LOC): 40 minutes
  - Large project (5-20K LOC): 80 minutes
  - Extra Large project (>20K LOC): 160 minutes

Timeout Handler:
  - If timeout occurs after <stage5_timeout>min:
    1. Display warning: "⚠️ Stage 5 超时 (><stage5_timeout>分钟) - 可能是特大型项目"
    2. Offer options:
       a) Retry with +50% timeout (<stage5_timeout * 1.5>min)
       b) Skip Stage 5 with degraded features
       c) Abort analysis
    3. Save partial result to checkpoint if any data collected
```

**🎯 Your Tasks**:
1. 检测并发机制（async/await, locks, threads）
2. 识别同步点并评估死锁风险
3. 检查共享资源的线程安全性
4. 生成问题报告（severity分类）
5. 提供优化建议

**🚨 Critical Constraints**:
- [ ] 识别所有并发机制
- [ ] 评估所有同步点的死锁风险
- [ ] 检查所有共享资源
- [ ] 问题按severity分类
- [ ] 提供可操作的建议

**✅ Self-Validation**:
```
Q: "All mechanisms found?" ✓ Complete?
Q: "Issues classified?" ✓ Has severity?
Q: "Suggestions actionable?" ✓ Concrete?
```

**📊 Required Output** (建议6: 进度可视化):
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 AIFlow v2.1 深度分析进度
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Progress: [████████████████████] 100% (Stage 5/5)
Elapsed: <elapsed> | Est. Remaining: <estimated>

✅ Stage 0: 项目初始化 (0.1 min)
✅ Stage 1: 项目认知 + 文档验证 (<actual1> min)
✅ Stage 2: 结构识别 (<actual2> min)
✅ Stage 3: 语义分析 (<actual3> min)
✅ Stage 4: 执行推理 + 性能量化 (<actual4> min)
🔄 Stage 5: 并发检测 (in progress...)
   ├─ 🔍 检测并发机制... ⏳
   ├─ ⚠️ 识别死锁风险... ⏳
   └─ 🛡️ 检查线程安全... ⏳

⏱️  当前Stage预计: 5-40分钟
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

完成后:
```
✅ Stage 5 完成
📊 结果:
   • 并发机制: <count>种
   • 同步点: <count>个
   • 问题: <count>个 (Critical: <c>, High: <h>)
   • 线程安全: <percent>%
```

**💾 Save Intermediate Result** (建议1+7: 部分成功保存 + 压缩):
```bash
# Step 1: Write uncompressed JSON to temporary file
Use Write tool to save:
D:/dart/flutter/aiflow/frontend/public/.cache/stage5_checkpoint.json.tmp

Content: Complete stage5_result JSON

# Step 2: Compress using gzip
Use Bash to execute:
gzip -c D:/dart/flutter/aiflow/frontend/public/.cache/stage5_checkpoint.json.tmp > D:/dart/flutter/aiflow/frontend/public/.cache/stage5_checkpoint.json.gz

# Step 3: Remove temporary uncompressed file
Use Bash to execute:
rm D:/dart/flutter/aiflow/frontend/public/.cache/stage5_checkpoint.json.tmp

Purpose: Final checkpoint before result compilation (70-80% disk space reduction)
```

**📊 Checkpoint Saved**:
```
💾 Checkpoint保存: stage5_checkpoint.json.gz
📊 压缩效果: 原始 <original_size> KB → 压缩后 <compressed_size> KB (~<compression_ratio>%)
🔄 可恢复点: Step 6开始前
⏱️  已耗时: <elapsed_time>
```

**➡️ Next**: 自动进入 Step 6

---

### 📦 Step 6: 合并结果 + 生成前端数据 (10秒)

**🧠 Memory Refresh**:
```
Step: 6/7 - Combine Results & Generate Frontend Data
Previous: 完成全部5个分析阶段
Goal:
  1. 创建摘要JSON: frontend/public/<project>-analysis.json
  2. 生成前端JSON: frontend/public/analysis.json (前端加载)
Output: 两个JSON文件
Next: Step 7 - Launch Frontend
```

**🎯 Sub-Step 6.1: 创建摘要JSON**

**📞 MCP Tool Call**:
```javascript
Use the aiflow_combine_results tool with:
{
  "stage5_result": "<Complete Stage 5 JSON>",
  "output_path": "frontend/public/<项目名称>-analysis.json"
}
```

**📊 Progress Output**:
```
✅ Stage 5 完成
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 Step 6/7: 合并结果 + 生成前端数据
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏳ Sub-Step 6.1: 创建摘要JSON...
💾 写入文件: <项目名称>-analysis.json...
✅ 验证JSON...
```

---

**🎯 Sub-Step 6.2: 生成前端兼容JSON**

**目标**: 创建 `analysis.json` 供前端自动加载

**前端数据格式要求** (frontend/src/App.tsx expects):
```typescript
{
  "metadata": {
    "project_name": string,
    "project_type": string,
    "analysis_version": string,
    "protocol_version": string,
    "stages_completed": string[],
    "stages_skipped": string[],
    "analysis_timestamp": string,
    "documentation_reliability": {...},  // From Stage 1
    "tech_stack": {...},                 // From Stage 1
    "architecture": {...},               // From Stage 1
    "complexity_assessment": {...},      // From Stage 1
    "core_business_scenarios": [...]     // From Stage 1
  },
  "code_structure": {
    "nodes": [...],                      // From Stage 2 - COMPLETE ARRAY
    "edges": [...],                      // From Stage 2 - COMPLETE ARRAY
    "grouping_strategy": {...},          // From Stage 2
    "analysis_metrics": {...}            // From Stage 2
  },
  "execution_traces": [...],             // From Stage 4 - COMPLETE ARRAY
  "tcu_summary": {...},                  // From Stage 4
  "concurrency_analysis": {              // From Stage 5
    "concurrency_mechanisms": [...],
    "synchronization_points": [...],
    "shared_resources": [...],
    "detected_issues": [...],
    "concurrency_metrics": {...}
  },
  "aiflow_v2_1_features": {...}
}
```

**📝 Your Tasks**:

1. **Extract Data from Stage Results**:
   - From `stage1_result`: metadata fields, tech_stack, architecture, core_business_scenarios
   - From `stage2_result`: code_structure.nodes[], code_structure.edges[], grouping_strategy
   - From `stage3_result`: launch_buttons (optional for frontend)
   - From `stage4_result`: execution_traces[], tcu_summary, performance_insights
   - From `stage5_result`: concurrency_analysis complete object

2. **🆕 Data Extraction Verification** (建议2: 数据提取验证):
   ```
   // Pseudo-code validation - Execute mentally before constructing JSON

   // Extract nodes[] from Stage 2
   const nodes = stage2_result.stage2_structure_recognition.code_structure.nodes;
   assert(Array.isArray(nodes), "nodes must be array");
   assert(nodes.length >= 10, "nodes array incomplete - need full array from Stage 2");

   // Extract edges[] from Stage 2
   const edges = stage2_result.stage2_structure_recognition.code_structure.edges;
   assert(Array.isArray(edges), "edges must be array");
   assert(edges.length >= 5, "edges array incomplete - need full array from Stage 2");

   // Extract execution_traces from Stage 4
   const traces = stage4_result.stage4_execution_inference.execution_traces;
   assert(Array.isArray(traces), "execution_traces must be array");
   assert(traces.length > 0, "execution_traces array empty");

   // Extract metadata from Stage 1
   const metadata = stage1_result.stage1_project_cognition;
   assert(metadata.tech_stack !== undefined, "tech_stack missing");
   assert(metadata.core_business_scenarios.length >= 3, "core_business_scenarios incomplete");
   ```

3. **Construct Frontend JSON**:
   ```json
   {
     "metadata": {
       "project_name": "<from stage1>",
       "project_type": "<from stage1>",
       "analysis_version": "2.1.0",
       "protocol_version": "2.1.0",
       "stages_completed": ["stage1_project_cognition", "stage2_structure_recognition", ...],
       "stages_skipped": [],
       "analysis_timestamp": "<ISO 8601>",

       "documentation_reliability": {...},  // Copy from stage1
       "tech_stack": {...},                 // Copy from stage1
       "architecture": {...},               // Copy from stage1
       "complexity_assessment": {...},      // Copy from stage1
       "core_business_scenarios": [...]     // Copy from stage1
     },
     "code_structure": {
       "nodes": [...],                      // FULL array from stage2
       "edges": [...],                      // FULL array from stage2
       "grouping_strategy": {...},          // Copy from stage2
       "analysis_metrics": {...}            // Copy from stage2
     },
     "execution_traces": [...],             // FULL array from stage4
     "tcu_summary": {...},                  // Copy from stage4
     "concurrency_analysis": {              // FULL object from stage5
       "concurrency_mechanisms": [...],
       "synchronization_points": [...],
       "shared_resources": [...],
       "detected_issues": [...],
       "concurrency_metrics": {...}
     },
     "aiflow_v2_1_features": {
       "documentation_reliability_enabled": true,
       "tcu_time_model_enabled": true,
       "core_business_scenarios_enabled": true,
       "performance_insights_enabled": true,
       "concurrency_detection_enabled": true
     }
   }
   ```

3. **Write Frontend JSON**:
   ```bash
   Use Write tool to create:
   D:/dart/flutter/aiflow/frontend/public/analysis.json
   ```

**🚨 Critical Constraints**:
- [ ] `code_structure.nodes` must be COMPLETE array from Stage 2 (NOT summary)
- [ ] `code_structure.edges` must be COMPLETE array from Stage 2 (NOT summary)
- [ ] `execution_traces` must be COMPLETE array from Stage 4
- [ ] All metadata fields present and valid
- [ ] JSON passes JSON.parse() validation
- [ ] File size reasonable (typically 50-500KB for complete data)

**✅ Self-Validation**:
```
Q: "nodes[] is complete array?" ✓ Length > 10?
Q: "edges[] is complete array?" ✓ Length > 5?
Q: "execution_traces[] present?" ✓ Not empty?
Q: "File created?" ✓ Exists at frontend/public/analysis.json?
```

**📊 Progress Output**:
```
⏳ Sub-Step 6.2: 生成前端兼容JSON...
📋 提取Stage 1-5完整数据...
🔧 构建前端格式...
   • metadata: ✅
   • code_structure.nodes: <count>个 ✅
   • code_structure.edges: <count>条 ✅
   • execution_traces: <count>个 ✅
   • concurrency_analysis: ✅
💾 写入文件: frontend/public/analysis.json...
✅ 验证JSON格式...
```

---

**🎯 Sub-Step 6.3: 跨Stage数据一致性验证** (建议3: 一致性验证)

**目标**: 确保所有Stage间的引用完整性和数据一致性

**🔍 Consistency Checks**:

1. **Node ID一致性验证**:
   ```
   // Verify all edge references point to valid nodes
   for each edge in code_structure.edges:
     assert(edge.source exists in code_structure.nodes, `Edge ${edge.id} has invalid source`)
     assert(edge.target exists in code_structure.nodes, `Edge ${edge.id} has invalid target`)

   // Verify all flowchart node references exist
   for each trace in execution_traces:
     for each flowchart_node in trace.flowchart.nodes:
       if flowchart_node.related_node_ids:
         for each related_id in flowchart_node.related_node_ids:
           assert(related_id exists in code_structure.nodes, `Flowchart node references invalid code node`)
   ```

2. **Business Scenario一致性**:
   ```
   // Check if Stage 1 scenarios are covered in Stage 3 launch buttons
   const stage1_scenarios = metadata.core_business_scenarios;
   const stage3_buttons = stage3_result.stage3_semantic_analysis.launch_buttons;

   for each scenario in stage1_scenarios:
     scenario_covered = stage3_buttons.some(button =>
       button.name.includes(scenario.name) OR
       button.business_value === scenario.business_value
     );
     if (!scenario_covered):
       warn(`Business scenario "${scenario.name}" not found in launch buttons`)
   ```

3. **Complexity一致性**:
   ```
   // Verify Stage 1 complexity aligns with Stage 2 metrics
   const stage1_complexity = metadata.complexity_assessment.score;
   const stage2_depth = code_structure.analysis_metrics.max_depth;
   const stage2_edges = code_structure.edges.length;

   // High complexity should correlate with deep hierarchies
   if (stage1_complexity > 0.7 AND stage2_depth < 3):
     warn("High complexity but shallow code structure - potential mismatch")

   if (stage1_complexity < 0.3 AND stage2_edges > 100):
     warn("Low complexity but many dependencies - potential mismatch")
   ```

**📊 Validation Output**:
```
🔍 跨Stage一致性验证...
   • Node ID引用: <valid_count>/<total_count> ✅
   • 业务场景覆盖: <coverage>% ✅
   • 复杂度一致性: ✅ 合理
⚠️  发现 <count> 个警告 (非致命，可继续)
```

---

**🎯 Sub-Step 6.4: 分析质量评分** (建议9: 质量评分系统)

**目标**: 为整个分析过程提供客观的质量评估，帮助用户快速了解分析结果的可信度

**📊 Quality Scoring Algorithm** (0-100分制):

```python
# 四维度评分模型
dimension_weights = {
    "node_integrity": 0.40,      # 节点引用完整性 (40%)
    "scenario_coverage": 0.30,   # 业务场景覆盖度 (30%)
    "complexity_consistency": 0.20,  # 复杂度一致性 (20%)
    "data_extraction": 0.10      # 数据提取正确性 (10%)
}

# 1. Node Integrity Score (40分)
valid_edges = count(edges where source AND target exist in nodes)
total_edges = count(all edges)
node_integrity_score = (valid_edges / total_edges) * 40

# 2. Scenario Coverage Score (30分)
scenarios_in_stage1 = count(core_business_scenarios from Stage 1)
scenarios_in_buttons = count(matching launch_buttons in Stage 3)
scenario_coverage_percentage = (scenarios_in_buttons / scenarios_in_stage1) * 100
scenario_coverage_score = (scenario_coverage_percentage / 100) * 30

# 3. Complexity Consistency Score (20分)
complexity_warnings = count(consistency warnings from Sub-Step 6.3)
complexity_consistency_score = max(0, 20 - (complexity_warnings * 5))

# 4. Data Extraction Score (10分)
data_validations = [
    nodes.length >= 10,
    edges.length >= 5,
    execution_traces.length > 0,
    core_business_scenarios.length >= 3,
    tech_stack !== undefined
]
passed_validations = count(validations that pass)
data_extraction_score = (passed_validations / 5) * 10

# Total Quality Score
total_score = (
    node_integrity_score +
    scenario_coverage_score +
    complexity_consistency_score +
    data_extraction_score
)
```

**📐 Quality Grade System**:
```
A+ (90-100分): 卓越质量，分析结果高度可信
A  (80-89分):  优秀质量，可直接用于生产决策
B  (70-79分):  良好质量，建议局部验证后使用
C  (60-69分):  及格质量，需要重点验证关键部分
D  (<60分):    质量不足，建议重新分析
```

**🎯 Quality-Based Recommendations**:
```python
if total_score >= 90:
    recommendation = "分析质量卓越，可直接用于架构决策和性能优化"
elif total_score >= 80:
    recommendation = "分析质量优秀，建议重点关注低评分维度"
elif total_score >= 70:
    recommendation = "分析质量良好，建议验证Node引用完整性后使用"
elif total_score >= 60:
    recommendation = "分析质量及格，建议重新检查Stage 1-2的数据质量"
else:
    recommendation = "分析质量不足，建议重新执行分析流程"

# Dimension-specific recommendations
if node_integrity_score < 32:  # <80% of 40
    recommendations.append("⚠️ Node引用完整性较低，检查Stage 2的节点和边关系")
if scenario_coverage_score < 24:  # <80% of 30
    recommendations.append("⚠️ 业务场景覆盖不足，验证Stage 1和Stage 3的一致性")
if complexity_consistency_score < 16:  # <80% of 20
    recommendations.append("⚠️ 复杂度评估不一致，重新审视架构模式识别")
if data_extraction_score < 8:  # <80% of 10
    recommendations.append("⚠️ 数据提取不完整，检查Stage间的JSON传递")
```

**📊 Quality Report Output**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 分析质量评分报告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

总分: <total_score>/100  等级: <grade>

评分细节:
  • Node引用完整性 (40%): <node_integrity_score>/40
    └─ 有效引用: <valid_edges>/<total_edges> (<percentage>%)

  • 业务场景覆盖 (30%): <scenario_coverage_score>/30
    └─ 场景匹配: <scenarios_in_buttons>/<scenarios_in_stage1> (<coverage>%)

  • 复杂度一致性 (20%): <complexity_consistency_score>/20
    └─ 一致性警告: <complexity_warnings>个

  • 数据提取正确性 (10%): <data_extraction_score>/10
    └─ 验证通过: <passed_validations>/5 项

质量等级: <grade> - <grade_description>

建议优先行动:
  <recommendation>
  <dimension_recommendations>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**✅ Quality Scoring Benefits**:
- **即时反馈**: 用户立即了解分析结果的可信度
- **问题定位**: 快速识别数据质量薄弱环节
- **决策支持**: 基于质量评分决定是否需要重新分析
- **持续改进**: 通过历史评分追踪分析质量趋势

**➡️ Next**: 进入 Step 6 Complete Output

---

**📊 Step 6 Complete Output**:
```
✅ Step 6 完成
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 文件1 (摘要): frontend/public/<项目名称>-analysis.json
   📊 大小: <size> KB

📄 文件2 (前端): frontend/public/analysis.json ⭐
   📊 大小: <size> KB
   🎯 包含完整结构:
      • Nodes: <count>个
      • Edges: <count>条
      • Traces: <count>个
   ✅ 前端自动加载就绪
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**➡️ Next**: 自动进入 Step 7

---

### 🎨 Step 7: 启动前端 (10秒)

**🧠 Memory Refresh**:
```
Step: 7/7 - Launch Frontend
Previous: 已保存分析结果 (analysis.json + <project>-analysis.json)
Goal: 启动开发服务器并打开浏览器
Final Step: 显示完成总结
```

**🔧 Bash Command**:
```bash
cd /d/dart/flutter/aiflow/frontend && npm run dev
```

**⚠️ Important Notes**:
- Frontend uses **Vite** dev server (not webpack)
- Correct command: `npm run dev` (NOT `npm start`)
- Default port: **5173** (NOT 3000)
- Browser auto-opens at `http://localhost:5173`

**📊 Required Output**:
```
✅ Step 6 完成
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎨 Step 7/7: 启动前端可视化
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 启动Vite开发服务器...
⏳ 等待就绪...
```

完成后:
```
✅ Step 7 完成
🌐 服务器: http://localhost:5173 ✅ 运行中
🎨 浏览器已自动打开
📄 前端自动加载: /analysis.json
```

**➡️ Next**: 显示最终完成总结

---

## 🎉 完成总结（YOU MUST DISPLAY）

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 AIFlow v2.1 深度分析完成！
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 分析统计:
  ✅ Stage 1: 项目认知 + 文档验证
     📚 文档可靠性: <level> (<score>)
     🎯 核心场景: <count>个
     🏗️ 架构: <pattern> (置信度: <conf>)

  ✅ Stage 2: 结构识别
     🌳 节点: <nodes>个
     🔗 边: <edges>条

  ✅ Stage 3: 语义分析
     🔘 按钮: <total> (Macro: <m>, Micro: <mic>)

  ✅ Stage 4: 执行推理 + 性能量化
     ⏱️ 总TCU: <total>
     🎯 关键路径: <critical> (<percent>%)
     🔍 瓶颈: <count>个
     💡 优化机会: <count>个

  ✅ Stage 5: 并发检测
     ⚠️ 问题: <count> (Critical: <c>, High: <h>)
     🛡️ 线程安全: <percent>%

🆕 v2.1增强特性:
  ✅ 📚 README一致性验证
  ✅ ⏱️ TCU时间量化
  ✅ 🎯 核心场景识别
  ✅ 🔍 性能瓶颈识别
  ✅ 💡 优化建议生成

📄 结果文件:
  • frontend/public/<项目>-analysis.json (摘要)
  • frontend/public/analysis.json (前端加载) ⭐

🌐 前端: http://localhost:5173 ✅ 运行中
⏱️ 总耗时: <actual_duration>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 下一步:
  1. 浏览器中探索交互式可视化
  2. 查看性能瓶颈并评估优先级
  3. 检查Critical/High级别并发问题
  4. 基于核心场景进行测试
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## ⏱️ 预期时间

| 项目规模 | 总耗时 |
|---------|--------|
| 小型 (<1K LOC) | 40-65分钟 |
| 中型 (1-5K LOC) | 1-2小时 |
| 大型 (5-20K LOC) | 2-4小时 |
| 超大型 (>20K LOC) | 4-8小时 |

---

## 🆕 v2.1 增强特性详解

### 📚 1. 文档可靠性评估

**目标**: 避免过时文档误导

**输出字段**: `documentation_reliability`
```json
{
  "overall_score": 0.85,
  "level": "high",
  "consistency_check": {
    "tech_stack": {
      "score": 0.9,
      "readme_claims": ["React 18", "TypeScript"],
      "actual_detected": ["React 18.2", "TypeScript 5.0"],
      "conflicts": []
    }
  },
  "analysis_strategy": "high_reliability"
}
```

**策略选择**:
- **high (≥0.8)**: 信任README
- **medium (0.5-0.8)**: 交叉验证
- **low (<0.5)**: 忽略README

---

### ⏱️ 2. TCU时间成本模型

**目标**: 量化性能，识别瓶颈

**标准值**:
- **CPU**: 1-20 TCU
- **I/O**: 50-800 TCU
- **DB**: 100-500 TCU
- **Network**: 200-800 TCU

**输出字段**: `timeline_estimation`
```json
{
  "total_tcu": 1250,
  "critical_path_tcu": 950,
  "bottlenecks": [
    {
      "event_id": "evt_002",
      "tcu_cost": 500,
      "optimization_suggestion": "添加缓存"
    }
  ]
}
```

---

### 🎯 3. 核心业务场景识别

**目标**: 连接代码与业务价值

**输出字段**: `core_business_scenarios`
```json
[
  {
    "scenario_id": "user_login",
    "name": "用户登录流程",
    "business_value": "high",
    "complexity": 0.6
  }
]
```

**业务价值**:
- **high**: 核心功能，影响收入
- **medium**: 重要功能
- **low**: 辅助功能

---

## 💡 最佳实践

1. **文档维护**: 可靠性 <0.6 时更新README
2. **性能优化**: 优先优化 TCU >500 的瓶颈
3. **业务聚焦**: 重点测试 high value 场景
4. **并发优化**: 利用 parallel_opportunities
5. **关键路径**: 优化关键路径获最大收益

---

## 📚 参考资料

**提示词优化指南**:
- `.claude/prompts/README.md` - 总览
- `.claude/prompts/cot-analysis-template.md` - 推理模板
- `.claude/prompts/few-shot-examples.md` - 质量示例
- `.claude/prompts/constraint-expression-guide.md` - 约束规范

**协议规范**:
- `frontend/src/types/protocol.ts` - JSON Schema定义
