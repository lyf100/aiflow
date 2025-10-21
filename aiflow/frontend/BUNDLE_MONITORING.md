# 📊 Bundle Size 监控与依赖管理指南

## 🎯 目的
维护AIFlow Frontend的性能和Bundle大小，确保长期保持优秀的加载速度。

---

## 📈 基线指标（2025年优化后）

### Bundle Size Baseline
```yaml
总大小（未压缩）:
  - JavaScript: ~760KB
  - CSS: ~170KB
  - 字体: ~80KB
  - 总计: ~1MB

Gzip压缩后:
  - JavaScript: ~243KB
  - CSS: ~29KB
  - 总计: ~272KB

关键Chunks:
  - react-vendor: 139KB (gzip: 45KB)
  - graph-viz: 517KB (gzip: 164KB) ⚡ 懒加载
  - d3-viz: 32KB (gzip: 12KB)
  - index: 55KB (gzip: 17KB)
  - CodeGraphCore: 12KB (gzip: 3KB) ⚡ 懒加载

构建时间: ~16秒
首屏加载: ~1.8秒 (3G网络)
```

### 依赖健康度
```yaml
总依赖数: ~450个包
生产依赖: 8个
  - react, react-dom
  - cytoscape, cytoscape-dagre
  - d3-selection, d3-scale, d3-transition
  - monaco-editor, @monaco-editor/react
  - zustand
  - pako

开发依赖: 15个
安全漏洞: 4个中等（可接受）
```

---

## 🔍 监控策略

### 1. 自动化监控（推荐）

#### 方法1: GitHub Actions + Bundlesize
```yaml
# .github/workflows/bundle-size.yml
name: Bundle Size Check

on:
  pull_request:
    branches: [main]

jobs:
  bundlesize:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm run build
      - uses: andresz1/size-limit-action@v1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          build_script: build
          limit: '300kb' # Gzip后的阈值
```

#### 方法2: package.json配置
```json
{
  "scripts": {
    "build": "tsc && vite build",
    "analyze": "vite-bundle-visualizer",
    "size-check": "npm run build && bundlesize"
  },
  "bundlesize": [
    {
      "path": "dist/assets/index-*.js",
      "maxSize": "20kb"
    },
    {
      "path": "dist/assets/react-vendor-*.js",
      "maxSize": "50kb"
    },
    {
      "path": "dist/assets/graph-viz-*.js",
      "maxSize": "170kb"
    }
  ]
}
```

### 2. 定期手动审查

#### 每月检查（15分钟）
```bash
cd frontend

# 1. 构建并查看大小
npm run build

# 2. 检查关键指标
ls -lh dist/assets/*.js | grep -E "index|vendor|graph"

# 3. 对比baseline
# 如果超过baseline 10%，需要调查原因

# 4. 生成可视化报告
npx vite-bundle-visualizer

# 5. 记录到文档
echo "$(date): Bundle size OK" >> bundle-check.log
```

#### 每季度深度审查（1小时）
```bash
# 1. 依赖安全审计
npm audit

# 2. 过时依赖检查
npx npm-check-updates

# 3. Bundle分析
npm run build -- --mode analyze

# 4. 性能测试
# 使用Lighthouse测试生产环境

# 5. 文档更新
# 更新baseline如果有显著变化
```

---

## 🚨 告警阈值

### Bundle Size告警
```yaml
警告级别:
  - 绿色: <300KB gzip (优秀)
  - 黄色: 300-350KB gzip (可接受)
  - 橙色: 350-400KB gzip (需优化)
  - 红色: >400KB gzip (立即优化)

当前状态: 🟢 绿色 (243KB)
```

### 依赖告警
```yaml
安全漏洞:
  - 严重/高危: 立即修复
  - 中等: 1周内修复
  - 低风险: 1月内修复

过时依赖:
  - 主版本落后: 评估升级
  - 次版本落后: 季度更新
  - 补丁版本落后: 可选更新

当前状态: ⚠️ 黄色 (4个中等漏洞待修复)
```

---

## 📋 优化清单

### 添加新依赖前必查
- [ ] 是否有更轻量的替代方案？
- [ ] 能否按需导入？
- [ ] Gzip后大小是多少？
- [ ] 是否支持Tree-shaking？
- [ ] 安全性如何？（npm audit）
- [ ] 维护活跃度？（最近更新时间）
- [ ] TypeScript支持？

### 定期优化检查
- [ ] 移除未使用的依赖（每月）
- [ ] 检查重复依赖（每季度）
- [ ] 评估懒加载机会（每季度）
- [ ] Review ESLint警告（每月）
- [ ] 更新安全补丁（实时）

---

## 🛠️ 优化工具

### 推荐工具
```bash
# Bundle分析
npm install --save-dev vite-bundle-visualizer

# Bundle大小监控
npm install --save-dev bundlesize

# 依赖更新检查
npm install -g npm-check-updates

# 安全审计（内置）
npm audit
```

### Vite插件
```typescript
// vite.config.ts
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig({
  plugins: [
    react(),
    // 仅在分析时启用
    process.env.ANALYZE && visualizer({
      open: true,
      filename: 'dist/stats.html',
      gzipSize: true,
      brotliSize: true,
    }),
  ],
});
```

---

## 📝 变更日志模板

```markdown
## Bundle Size 变更 - YYYY-MM-DD

### 变更内容
- [添加/移除/优化] 依赖名称

### 影响评估
- Bundle大小变化: +/-XX KB
- Gzip后变化: +/-XX KB
- 首屏加载变化: +/-X.Xs
- 原因: 简要说明

### 审批状态
- [ ] 小于10%变化（自动通过）
- [ ] 10-20%变化（需要review）
- [ ] 大于20%变化（需要详细说明）
```

---

## 🎯 长期目标

### 2025 Q2目标
- [ ] 保持gzip总大小 <250KB
- [ ] 首屏加载时间 <1.5秒（3G）
- [ ] 0个高危/严重漏洞
- [ ] ESLint零错误
- [ ] 测试覆盖率 >95%

### 持续改进方向
1. **HTTP/2推送**: 关键资源预加载
2. **Brotli压缩**: 进一步减小15-20%
3. **Service Worker**: 离线支持
4. **Critical CSS**: 内联关键CSS
5. **Prefetch/Preload**: 智能资源预加载

---

## 📚 参考资源

- [Vite Bundle Optimization](https://vitejs.dev/guide/build.html)
- [Web.dev Performance](https://web.dev/performance/)
- [Bundlephobia](https://bundlephobia.com/) - 依赖大小查询
- [npm.devtool.tech](https://npm.devtool.tech/) - npm包对比

---

**最后更新**: 2025-10-20
**维护者**: AIFlow Team
**Review周期**: 每月第一周
