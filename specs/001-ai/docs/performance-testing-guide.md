# Performance Testing Guide - AI分析指挥与可视化平台

**Version**: 1.0.0
**Last Updated**: 2025-10-10
**Target**: AIFlow Analysis & Visualization Platform

## Overview

This guide defines the performance measurement methodology, test environment specifications, and acceptance criteria for the AI Analysis & Visualization Platform (AIFlow). All performance targets are derived from `spec.md` requirements (FR-053 to FR-057).

## Performance Requirements Summary

### Rendering Performance (FR-053 to FR-056)

| Project Size | Node Count | First Render | Level Switch P95 | Level Switch P99 |
|--------------|------------|--------------|------------------|------------------|
| Small        | <500       | <1s          | <150ms           | <250ms           |
| Medium       | 500-2000   | <3s          | <300ms           | <500ms           |
| Large        | 2000-5000  | <8s          | <500ms           | <800ms           |
| Extra Large  | >5000      | <2s*         | N/A              | N/A              |

*Extra large projects use progressive loading - only initial viewport rendering is measured.

### AI Analysis Performance (FR-057)

| Project Size | LOC        | Analysis Time | Cache Hit Rate | Incremental Update |
|--------------|------------|---------------|----------------|---------------------|
| Small        | <1000      | 2-5 min       | ≥70%           | <30s                |
| Medium       | 1000-5000  | 10-20 min     | ≥70%           | 1-3 min             |
| Large        | 5000-20000 | 30-60 min     | ≥70%           | 5-10 min            |
| Extra Large  | >20000     | 1-3 hours     | ≥70%           | 10-30 min           |

### Animation Performance (FR-033, FR-041)

| Scenario                    | Target FPS | Success Rate |
|-----------------------------|------------|--------------|
| ≤5 concurrent flows         | ≥30 FPS    | ≥95%         |
| 6-10 concurrent flows       | ≥15 FPS    | ≥80%         |
| >10 concurrent flows        | Auto-degrade to simplified view | 100% |

### Memory & Resource Constraints

- **Medium projects**: ≤500MB memory usage
- **Large projects**: ≤1GB memory usage
- **API response time**: P95 <500ms, P99 <1s
- **WebSocket latency**: <50ms roundtrip
- **Concurrent connections**: ≥100 simultaneous users
- **Concurrent animations**: ≥50 simultaneous animation sessions

## Test Environment Specifications

### Hardware Requirements

#### Development Testing Environment
- **CPU**: Intel i5-10400 or AMD Ryzen 5 3600 (6 cores, 12 threads)
- **RAM**: 16GB DDR4-3200
- **Storage**: NVMe SSD (≥500 MB/s sequential read)
- **GPU**: Integrated graphics (Intel UHD 630 or equivalent)
- **Network**: Gigabit Ethernet or WiFi 5 (802.11ac)

#### Production Baseline Environment
- **CPU**: Intel i7-8700K or AMD Ryzen 7 3700X (8 cores, 16 threads)
- **RAM**: 32GB DDR4-3200
- **Storage**: NVMe SSD (≥1000 MB/s sequential read)
- **GPU**: Dedicated GPU with WebGL 2.0 support (GTX 1660 or equivalent)
- **Network**: Gigabit Ethernet

#### Mobile/Low-End Testing Environment
- **CPU**: Intel i3-8100 or AMD Ryzen 3 3200G (4 cores, 4 threads)
- **RAM**: 8GB DDR4-2666
- **Storage**: SATA SSD (≥300 MB/s sequential read)
- **GPU**: Integrated graphics
- **Network**: WiFi 5 (802.11ac)

### Software Requirements

#### Operating Systems
- **Windows**: Windows 10 21H2+ or Windows 11
- **macOS**: macOS 12 Monterey+
- **Linux**: Ubuntu 22.04 LTS or equivalent

#### Browser Versions (Must Test All)
- **Chrome**: 90+ (Primary target)
- **Firefox**: 88+ (Secondary target)
- **Safari**: 14+ (macOS only)
- **Edge**: 90+ (Chromium-based)

#### Backend Runtime
- **Python**: 3.11+
- **Node.js**: 18+ LTS (for frontend build)
- **Database**: SQLite 3.38+

## Performance Measurement Methodology

### 1. Rendering Performance Testing

#### Test Tool: Lighthouse + Custom Metrics

**Measurement Procedure**:

1. **First Render Time (FRT)**
   ```javascript
   // Frontend measurement code
   const startTime = performance.now();
   // Trigger Cytoscape.js rendering
   cy.mount(container);
   cy.layout({ name: 'cose' }).run();
   cy.on('layoutstop', () => {
     const endTime = performance.now();
     const frt = endTime - startTime;
     console.log(`First Render Time: ${frt}ms`);
   });
   ```

2. **Level Switch Time (LST)**
   ```javascript
   // Measure node expansion/collapse performance
   const startTime = performance.now();
   node.on('tap', () => {
     const expandStart = performance.now();
     // Expand node to show children
     expandNode(node);
     cy.layout({ name: 'cose' }).run();
     cy.on('layoutstop', () => {
       const expandEnd = performance.now();
       const lst = expandEnd - expandStart;
       console.log(`Level Switch Time: ${lst}ms`);
     });
   });
   ```

3. **Automated Testing with Playwright**
   ```typescript
   // E2E performance test
   test('rendering performance - medium project', async ({ page }) => {
     await page.goto('/analysis/medium-project');
     const frt = await page.evaluate(() => {
       return new Promise((resolve) => {
         const start = performance.now();
         window.addEventListener('aiflow:render:complete', () => {
           resolve(performance.now() - start);
         });
       });
     });
     expect(frt).toBeLessThan(3000); // 3s target for medium projects
   });
   ```

**Success Criteria**:
- P50 (median) must meet target -10%
- P95 must meet target exactly
- P99 must meet target +20%
- 95% of measurements within target range

#### Test Dataset Requirements

**Small Project Dataset** (<500 nodes):
- Example: Simple REST API (5-10 files, 500-1000 LOC)
- Structure: 3 modules, 20 classes, 100 functions
- Reference: `tests/fixtures/small-project/`

**Medium Project Dataset** (500-2000 nodes):
- Example: E-commerce backend (20-50 files, 3000-5000 LOC)
- Structure: 10 modules, 80 classes, 400 functions
- Reference: `tests/fixtures/medium-project/`

**Large Project Dataset** (2000-5000 nodes):
- Example: Microservices system (100+ files, 15000-20000 LOC)
- Structure: 30 modules, 300 classes, 1500 functions
- Reference: `tests/fixtures/large-project/`

### 2. Animation Performance Testing

#### Test Tool: Chrome DevTools Performance Profiler + Custom FPS Counter

**Measurement Procedure**:

1. **FPS Measurement**
   ```javascript
   // Custom FPS counter
   class FPSMonitor {
     constructor() {
       this.frames = [];
       this.lastTime = performance.now();
     }

     tick() {
       const now = performance.now();
       const delta = now - this.lastTime;
       this.frames.push(1000 / delta);
       this.lastTime = now;

       // Keep last 60 frames (1 second at 60fps)
       if (this.frames.length > 60) {
         this.frames.shift();
       }
     }

     getAverageFPS() {
       const sum = this.frames.reduce((a, b) => a + b, 0);
       return sum / this.frames.length;
     }

     getMinFPS() {
       return Math.min(...this.frames);
     }
   }

   // Usage in animation loop
   const fpsMonitor = new FPSMonitor();
   function animationLoop() {
     fpsMonitor.tick();
     // Animation logic here
     requestAnimationFrame(animationLoop);
   }
   ```

2. **Concurrent Flow Stress Test**
   ```typescript
   // E2E test with Playwright
   test('animation performance - 5 concurrent flows', async ({ page }) => {
     await page.goto('/analysis/concurrent-test');

     // Start FPS monitoring
     await page.evaluate(() => {
       window.fpsMonitor = new FPSMonitor();
       window.animationActive = true;
     });

     // Trigger 5 concurrent flow animations
     await page.click('[data-testid="launch-concurrent-5"]');

     // Monitor for 10 seconds
     await page.waitForTimeout(10000);

     const avgFPS = await page.evaluate(() => window.fpsMonitor.getAverageFPS());
     const minFPS = await page.evaluate(() => window.fpsMonitor.getMinFPS());

     expect(avgFPS).toBeGreaterThanOrEqual(30);
     expect(minFPS).toBeGreaterThanOrEqual(25); // Allow 5fps dip
   });
   ```

**Success Criteria**:
- Average FPS ≥ target FPS (30 for ≤5 flows)
- Minimum FPS ≥ target FPS - 5 (allow brief dips)
- 95% of frames within target FPS range
- No frame drops >100ms (jank detection)

### 3. AI Analysis Performance Testing

#### Test Tool: pytest + time profiling + cProfile

**Measurement Procedure**:

1. **End-to-End Analysis Time**
   ```python
   # Backend test
   import pytest
   import time
   from aiflow.analysis import AnalysisEngine

   @pytest.mark.slow
   def test_analysis_performance_small_project():
       start_time = time.time()

       engine = AnalysisEngine()
       result = engine.analyze_project(
           project_path="tests/fixtures/small-project",
           adapter="claude-code-adapter"
       )

       end_time = time.time()
       analysis_time = end_time - start_time

       assert result.status == "completed"
       assert analysis_time < 300  # 5 minutes = 300 seconds

       # Verify all 5 stages completed
       assert len(result.stages) == 5
       assert all(stage.status == "completed" for stage in result.stages)
   ```

2. **Stage-Level Profiling**
   ```python
   # Detailed stage timing
   def test_analysis_stage_timing():
       engine = AnalysisEngine()

       with engine.profile_stages() as profiler:
           result = engine.analyze_project(
               project_path="tests/fixtures/medium-project",
               adapter="claude-code-adapter"
           )

       stage_times = profiler.get_stage_times()

       # Verify stage time proportions
       assert stage_times['project_understanding'] < 60  # <1 min
       assert stage_times['structure_recognition'] < 1800  # <30 min
       assert stage_times['semantic_analysis'] < 2400  # <40 min
       assert stage_times['execution_inference'] < 3000  # <50 min
       assert stage_times['concurrency_detection'] < 1200  # <20 min
   ```

3. **Cache Hit Rate Measurement**
   ```python
   # Cache effectiveness test
   def test_cache_hit_rate():
       engine = AnalysisEngine()
       cache = engine.cache

       # Clear cache
       cache.clear()

       # First analysis (cold cache)
       engine.analyze_project("tests/fixtures/medium-project")

       # Analyze 10 times with minor modifications
       cache_stats = []
       for i in range(10):
           # Modify one file
           modify_random_file("tests/fixtures/medium-project")

           result = engine.analyze_project("tests/fixtures/medium-project")
           cache_stats.append(cache.get_hit_rate())

       avg_hit_rate = sum(cache_stats) / len(cache_stats)
       assert avg_hit_rate >= 0.70  # ≥70% cache hit rate
   ```

4. **Incremental Analysis Performance**
   ```python
   # Incremental update timing
   def test_incremental_analysis_performance():
       engine = AnalysisEngine()

       # Initial full analysis
       initial_result = engine.analyze_project("tests/fixtures/medium-project")

       # Modify 2 files
       modify_files(["src/auth.py", "src/user.py"])

       # Incremental analysis
       start_time = time.time()
       incremental_result = engine.analyze_project(
           "tests/fixtures/medium-project",
           mode="incremental"
       )
       incremental_time = time.time() - start_time

       # Should be much faster than full analysis
       assert incremental_time < 180  # <3 minutes for medium project
       assert incremental_result.updated_files == 2
       assert incremental_result.total_files == initial_result.total_files
   ```

**Success Criteria**:
- Full analysis time within target range (FR-057)
- Cache hit rate ≥70% after warmup
- Incremental analysis <20% of full analysis time
- All 5 stages must complete successfully
- Resume capability works after interruption

### 4. Memory Usage Testing

#### Test Tool: Chrome DevTools Memory Profiler + Python memory_profiler

**Frontend Memory Measurement**:
```javascript
// Frontend memory monitoring
class MemoryMonitor {
  async measure() {
    if (performance.memory) {
      return {
        usedJSHeapSize: performance.memory.usedJSHeapSize / 1048576, // MB
        totalJSHeapSize: performance.memory.totalJSHeapSize / 1048576,
        jsHeapSizeLimit: performance.memory.jsHeapSizeLimit / 1048576
      };
    }
    return null;
  }

  async startMonitoring(intervalMs = 1000) {
    this.measurements = [];
    this.interval = setInterval(async () => {
      const memory = await this.measure();
      if (memory) {
        this.measurements.push({
          timestamp: Date.now(),
          ...memory
        });
      }
    }, intervalMs);
  }

  stopMonitoring() {
    clearInterval(this.interval);
    return this.measurements;
  }

  getPeakMemory() {
    const peak = Math.max(...this.measurements.map(m => m.usedJSHeapSize));
    return peak;
  }
}
```

**Backend Memory Measurement**:
```python
# Backend memory profiling
from memory_profiler import profile

@profile
def test_analysis_memory_usage():
    engine = AnalysisEngine()
    result = engine.analyze_project("tests/fixtures/large-project")

    # Memory assertions handled by memory_profiler output
    # Manual verification against targets:
    # - Medium projects: ≤500MB
    # - Large projects: ≤1GB
```

**Success Criteria**:
- Peak memory usage within target limits
- No memory leaks (stable memory after GC)
- Memory growth rate <10% per hour during continuous operation

### 5. API & WebSocket Performance Testing

#### Test Tool: Apache Bench (ab) + WebSocket load testing tools

**REST API Load Test**:
```bash
# API endpoint performance test
ab -n 1000 -c 10 -T application/json \
   -p test-data.json \
   http://localhost:8000/api/analysis

# Expected results:
# - P95 latency <500ms
# - P99 latency <1000ms
# - 0% error rate
# - Throughput ≥100 req/s
```

**WebSocket Latency Test**:
```python
# WebSocket roundtrip latency test
import asyncio
import websockets
import time

async def measure_ws_latency():
    uri = "ws://localhost:8000/ws/animation/test-session"

    latencies = []
    async with websockets.connect(uri) as websocket:
        for i in range(100):
            start = time.time()

            # Send command
            await websocket.send('{"command": "ping"}')

            # Wait for response
            response = await websocket.recv()

            end = time.time()
            latency_ms = (end - start) * 1000
            latencies.append(latency_ms)

            await asyncio.sleep(0.1)

    avg_latency = sum(latencies) / len(latencies)
    p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]

    assert avg_latency < 30  # <30ms average
    assert p95_latency < 50  # <50ms P95
```

**Success Criteria**:
- API P95 response time <500ms
- WebSocket roundtrip latency <50ms P95
- Support ≥100 concurrent connections
- Support ≥50 concurrent animation sessions
- 0% connection drops under normal load

## Baseline Metrics & Acceptance Criteria

### Baseline Performance Targets

All measurements must be taken on the **Development Testing Environment** with the specified **Browser Versions**.

| Metric Category          | Metric                  | Target          | Must Pass | Nice to Have |
|--------------------------|-------------------------|-----------------|-----------|--------------|
| **Rendering**            | Small FRT               | <1s             | <1.2s     | <800ms       |
|                          | Medium FRT              | <3s             | <3.6s     | <2.5s        |
|                          | Large FRT               | <8s             | <9.6s     | <7s          |
|                          | Level Switch P95        | <300ms          | <360ms    | <250ms       |
| **Animation**            | ≤5 flows FPS            | ≥30 FPS         | ≥28 FPS   | ≥45 FPS      |
|                          | 6-10 flows FPS          | ≥15 FPS         | ≥13 FPS   | ≥20 FPS      |
| **AI Analysis**          | Small Project           | 2-5 min         | <6 min    | <3 min       |
|                          | Medium Project          | 10-20 min       | <24 min   | <15 min      |
|                          | Cache Hit Rate          | ≥70%            | ≥65%      | ≥80%         |
| **Memory**               | Medium Project          | ≤500MB          | ≤600MB    | ≤400MB       |
|                          | Large Project           | ≤1GB            | ≤1.2GB    | ≤800MB       |
| **API**                  | Response Time P95       | <500ms          | <600ms    | <400ms       |
| **WebSocket**            | Latency P95             | <50ms           | <60ms     | <40ms        |

### Regression Prevention

**Automated Performance Regression Tests**:
- Run on every commit to main branch
- Compare against baseline metrics from `tests/performance/baselines.json`
- Fail CI if any metric regresses by >10%
- Generate performance comparison report

```yaml
# Example CI configuration (.github/workflows/performance.yml)
name: Performance Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup environment
        run: ./scripts/setup-perf-env.sh
      - name: Run performance tests
        run: |
          pytest tests/performance/ --benchmark-json=output.json
      - name: Compare against baseline
        run: |
          python scripts/compare-perf.py output.json tests/performance/baselines.json
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: performance-results
          path: output.json
```

## Test Execution Schedule

### Development Phase Testing
- **Frequency**: On every significant change (feature completion, optimization)
- **Scope**: Quick smoke tests (small project only)
- **Duration**: <10 minutes
- **Automation**: Run automatically via pre-commit hooks

### Pre-Release Testing
- **Frequency**: Before each release candidate
- **Scope**: Full test suite (all project sizes, all browsers)
- **Duration**: 2-4 hours
- **Automation**: Run automatically via CI/CD pipeline

### Production Monitoring
- **Frequency**: Continuous (real user monitoring)
- **Scope**: Real-world usage metrics
- **Tools**: Application Performance Monitoring (APM) integration
- **Alerting**: Automatic alerts if metrics degrade >15%

## Performance Optimization Guidelines

### When Performance Degrades

**Investigation Process**:
1. **Identify Regression**: Which metric regressed? By how much?
2. **Isolate Cause**: Recent code changes, dependency updates, data changes?
3. **Profile**: Use browser DevTools or cProfile to find bottleneck
4. **Fix**: Apply targeted optimization
5. **Verify**: Re-run performance tests to confirm fix
6. **Document**: Add learnings to `docs/performance-learnings.md`

**Common Optimization Techniques**:
- **Rendering**: Virtualization (viewport culling), LOD (Level of Detail), lazy loading
- **Animation**: Canvas layering, Web Workers for computation, reduce repaints
- **AI Analysis**: Parallel stage execution, smarter caching, delta analysis
- **Memory**: Object pooling, weak references, manual GC triggering
- **Network**: Request batching, compression, HTTP/2 multiplexing

## Appendix: Test Data Generation

### Generating Synthetic Test Projects

```python
# Script: tests/fixtures/generate-test-project.py
from pathlib import Path
import random

def generate_test_project(size: str, output_path: Path):
    """
    Generate synthetic test project for performance testing.

    Args:
        size: 'small' | 'medium' | 'large'
        output_path: Output directory
    """
    configs = {
        'small': {'modules': 3, 'classes': 20, 'functions': 100, 'files': 10},
        'medium': {'modules': 10, 'classes': 80, 'functions': 400, 'files': 50},
        'large': {'modules': 30, 'classes': 300, 'functions': 1500, 'files': 150}
    }

    config = configs[size]

    # Generate project structure
    # ... (implementation details)

if __name__ == '__main__':
    generate_test_project('small', Path('tests/fixtures/small-project'))
    generate_test_project('medium', Path('tests/fixtures/medium-project'))
    generate_test_project('large', Path('tests/fixtures/large-project'))
```

## Appendix: Performance Test Checklist

- [ ] All test environments properly configured (dev, prod, mobile)
- [ ] All browser versions tested (Chrome, Firefox, Safari, Edge)
- [ ] Test datasets prepared (small, medium, large projects)
- [ ] Baseline metrics established and documented
- [ ] Automated performance tests integrated into CI/CD
- [ ] Performance regression detection enabled
- [ ] APM integration configured for production monitoring
- [ ] Performance optimization guidelines documented
- [ ] Team trained on performance testing methodology
- [ ] Performance test results reviewed and accepted by stakeholders

---

**References**:
- `specs/001-ai/spec.md` - FR-053 to FR-057 (Performance requirements)
- `specs/001-ai/plan.md` - Performance testing strategy (Section 6)
- Web Performance Working Group: https://www.w3.org/webperf/
- Chrome DevTools Performance: https://developer.chrome.com/docs/devtools/performance/
