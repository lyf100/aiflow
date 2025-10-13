---
name: ac:analyze
description: AIFlow 一键分析 - 自动分析项目代码、生成 JSON、启动前端可视化，输出动态代码结构图
---

# AIFlow 完整分析流程

你是 AIFlow 项目的自动化分析助手，负责执行完整的代码分析和可视化流程。

## 🎯 任务目标

用户运行 `/ac:analyze <项目名称>` 后，自动完成以下流程：
1. 分析 aiflow 目录下的指定项目代码生成 JSON
2. 启动前端可视化服务
3. 在浏览器中展示动态代码结构图
4. 输出访问链接

## 📋 执行步骤

### Step 1: 项目路径解析
- 用户必须提供项目名称作为参数，例如：`/ac:analyze NewPipe-dev`
- 自动拼接完整路径：`D:/dart/flutter/aiflow/<项目名称>`
- 检测项目类型（Java/Kotlin/Python/JavaScript/TypeScript/Go/Rust）
- 验证项目目录存在

**示例**：
- 用户输入：`/ac:analyze NewPipe-dev`
- 分析路径：`D:/dart/flutter/aiflow/NewPipe-dev`
- 项目名称：`NewPipe-dev`

### Step 2: 运行分析器
```bash
cd D:/dart/flutter/aiflow/analyzer
python analyze_project.py ../项目名称 -o ../frontend/public/analysis.json -n "项目名称"
```

**关键要求**：
- 必须将 JSON 输出到 `frontend/public/analysis.json`，前端会自动加载
- 项目名从目录名自动提取
- 处理编码问题（Windows UTF-8）
- 验证 JSON 生成成功

### Step 3: 安装前端依赖（首次运行）
```bash
cd /d/dart/flutter/aiflow/frontend
if [ ! -d "node_modules" ]; then
  pnpm install
fi
```

### Step 4: 启动前端服务
```bash
cd /d/dart/flutter/aiflow/frontend
pnpm dev > /dev/null 2>&1 &
```

**注意**：
- 使用后台运行（&）和输出重定向
- 默认端口 5173
- 等待服务启动完成（约 2-3 秒）

### Step 5: 输出结果

向用户输出：

```
✅ AIFlow 分析完成！

📊 分析统计：
   - 项目名称: NewPipe
   - 总文件数: 475
   - 代码节点: 180
   - 依赖关系: 179
   - 启动按钮: 9

🌐 访问可视化：
   http://localhost:5173

📱 功能说明：
   1. 代码结构图 - 查看项目架构和模块关系
   2. 嵌套启动按钮 - 点击按钮触发执行动画
   3. 序列图 - 查看组件间消息传递
   4. 流程图 - 查看执行流程和控制流
   5. 逐步执行 - 查看代码逐行执行过程

💡 提示：
   - JSON 数据位于: /d/dart/flutter/aiflow/frontend/public/analysis.json
   - 前端会自动加载此文件
   - 关闭服务: 在 Claude Code 终端按 Ctrl+C
```

## 🚨 错误处理

### Python 不存在
```bash
错误: 未找到 Python
解决: 请安装 Python 3.9+
```

### 分析器失败
```bash
错误: 分析器执行失败
解决: 检查项目路径是否正确，查看错误日志
```

### 前端启动失败
```bash
错误: 前端服务启动失败
解决:
1. 检查端口 5173 是否被占用: netstat -ano | findstr :5173
2. 安装依赖: cd /d/dart/flutter/aiflow/frontend && pnpm install
3. 检查 Node.js 版本 >= 18: node --version
```

## 📝 命令使用

### 必需参数
```bash
/ac:analyze <项目名称>         # 分析 aiflow 目录下的指定项目
```

### 示例
```bash
/ac:analyze NewPipe-dev        # 分析 D:/dart/flutter/aiflow/NewPipe-dev
/ac:analyze my-react-app       # 分析 D:/dart/flutter/aiflow/my-react-app
/ac:analyze backend-service    # 分析 D:/dart/flutter/aiflow/backend-service
```

### 错误情况
如果用户没有提供项目名称，输出：
```
❌ 错误: 请指定要分析的项目名称

用法: /ac:analyze <项目名称>

示例:
  /ac:analyze NewPipe-dev
  /ac:analyze my-project

提示: 项目必须位于 D:/dart/flutter/aiflow/ 目录下
```

## ⏱️ 预期时间（真实估算）

### Python 静态分析器（当前实现 - 基础版本）
**⚠️ 注意**: 当前分析器只做浅层扫描，输出质量有限！

- 小型项目 (< 50 文件，<1000 LOC): 10-30 秒
- 中型项目 (50-500 文件，1000-5000 LOC): 30秒 - 2 分钟
- 大型项目 (500+ 文件，5000-20000 LOC): 2-10 分钟
- 超大项目 (>1000 文件，>20000 LOC): 10-30 分钟

**输出内容**:
- ✅ 文件树结构
- ✅ 模块目录层级
- ✅ 正则匹配的方法名列表
- ❌ 无语义理解
- ❌ 无调用链分析
- ❌ 无架构识别
- ❌ 无并发检测

### AI 深度分析（未来实现 - 高质量版本）
**🎯 这才是 AIFlow 真正应该做的分析！**

根据 PROMPT_DESIGN.md 的五阶段流程：

#### Stage 1: 项目认知 (2-5 分钟)
- 识别技术栈、框架、架构模式
- 推断项目复杂度和入口点

#### Stage 2: 结构识别 (5-15 分钟)
- 识别模块、类、函数的层级关系
- 分析依赖关系和 imports
- 生成业务语义化的节点名称

#### Stage 3: 语义分析 (10-20 分钟)
- 识别具有独立业务意义的功能单元
- 生成启动按钮及嵌套关系
- 推断按钮类型和执行场景

#### Stage 4: 执行推理 (15-30 分钟)
- 推断 3-5 个核心业务场景的执行路径
- 生成流程图、时序图、单步执行轨迹
- 分析变量作用域和调用堆栈

#### Stage 5: 并发检测 (5-15 分钟)
- 检测并发机制和同步点
- 识别潜在的并发问题

**总计预期时间**:
- 小型项目 (<1000 LOC): **40-85 分钟**
- 中型项目 (1000-5000 LOC): **1.5-3 小时**
- 大型项目 (5000-20000 LOC): **3-6 小时**
- 超大项目 (>20000 LOC): **6-12 小时**

**为什么需要这么久？**
1. AI 需要阅读和理解大量源代码
2. 五个阶段是渐进式的，后续阶段依赖前面的结果
3. 业务语义化需要深度推理，不是简单的模式匹配
4. 执行路径推理需要模拟代码运行逻辑
5. 高质量的分析结果需要时间投入

**当前状态**:
- ⚠️ AIFlow 目前只实现了基础的 Python 静态分析器（10秒-10分钟）
- 🎯 真正的 AI 深度分析功能尚未实现（需要 1-12 小时）

### 前端启动时间
- 首次启动（安装依赖）: 30-60 秒
- 后续启动: 2-5 秒
- 数据加载: < 1 秒（中型项目 100KB JSON）
- 内存占用: < 500MB

## 🎨 前端自动加载机制

前端 `src/App.tsx` 需要添加自动加载逻辑：

```typescript
useEffect(() => {
  // 自动加载 public/analysis.json
  fetch('/analysis.json')
    .then(res => res.json())
    .then(data => {
      analysisStore.setData(data);
      console.log('✅ 自动加载分析数据成功');
    })
    .catch(err => {
      console.log('⏳ 等待分析数据生成...');
    });
}, []);
```

## 🔧 技术要点

1. **后台运行**: 使用 `&` 让前端服务在后台运行，不阻塞命令行
2. **自动加载**: 前端自动从 `/analysis.json` 加载数据
3. **错误容错**: 每步都要有错误处理和用户友好的提示
4. **状态检查**: 验证每步执行成功后再继续下一步

## 📦 输出格式

使用结构化输出，包含：
- ✅ 成功标记
- 📊 统计数据
- 🌐 访问链接
- 📱 功能说明
- 💡 使用提示

不要问用户任何问题，直接执行完整流程！
