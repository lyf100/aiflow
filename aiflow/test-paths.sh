#!/bin/bash

echo "=== AIFlow 路径验证 ==="
echo ""

echo "1. 检查项目根目录:"
ls -d /d/dart/flutter/aiflow && echo "  ✅ aiflow 根目录存在" || echo "  ❌ 错误"

echo ""
echo "2. 检查分析器:"
ls /d/dart/flutter/aiflow/analyzer/analyze_project.py && echo "  ✅ 分析器存在" || echo "  ❌ 错误"

echo ""
echo "3. 检查前端目录:"
ls -d /d/dart/flutter/aiflow/frontend && echo "  ✅ frontend 目录存在" || echo "  ❌ 错误"

echo ""
echo "4. 检查前端文件:"
ls /d/dart/flutter/aiflow/frontend/index.html && echo "  ✅ index.html 存在" || echo "  ❌ 错误"
ls /d/dart/flutter/aiflow/frontend/package.json && echo "  ✅ package.json 存在" || echo "  ❌ 错误"
ls /d/dart/flutter/aiflow/frontend/src/App.tsx && echo "  ✅ App.tsx 存在" || echo "  ❌ 错误"

echo ""
echo "5. 检查测试项目:"
ls -d /d/dart/flutter/aiflow/NewPipe-dev && echo "  ✅ NewPipe-dev 存在" || echo "  ❌ 错误"

echo ""
echo "6. 检查命令文件:"
ls /d/dart/flutter/aiflow/.claude/commands/ac-analyze.md && echo "  ✅ /ac:analyze 命令存在" || echo "  ❌ 错误"

echo ""
echo "=== 路径验证完成 ==="
