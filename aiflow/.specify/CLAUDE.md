# Agent Context: 001-ai - AI分析指挥与可视化平台

**Last Updated**: 2025-10-09
**Feature Branch**: 001-ai
**Project Type**: Web Application (Frontend + Backend)

## Quick Reference

### Languages & Versions
- **Backend**: Python 3.11+
- **Frontend**: TypeScript 5.x
- **Target Platform**: Web (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)

### Primary Dependencies

**Backend**:
- FastAPI (Web framework)
- Poetry (Package management)
- Jinja2 (Template engine for Prompt Library)
- jsonschema (Data validation)
- aiohttp (Async HTTP client)
- Celery (Task queue, optional)
- pytest + pytest-asyncio + pytest-cov (Testing)

**Frontend**:
- React 18 (UI framework)
- Zustand (State management)
- Cytoscape.js (Main sandbox renderer - hierarchical code structure)
- D3.js (Detail analysis renderer - flowcharts, sequence diagrams)
- Monaco Editor (Step-by-step detail view)
- Vite (Build tool)
- Vitest (Unit testing)
- Playwright (E2E testing)

### Storage
- **Backend**: SQLite (cache) + File system (JSON analysis results + YAML prompt templates)
- **Frontend**: IndexedDB (analysis results) + LocalStorage (user preferences)

## Architecture Overview

### Core Components

**1. 核心指令集 (Prompt Library)**
- Technology: YAML + Jinja2 template engine
- Storage: Git LFS for version control
- Location: `backend/prompts/`
- Versioning: Semantic versioning (e.g., `python-structure-v1.1.0.yaml`)

**2. AI适配器层 (Adapter Layer)**
- Architecture: Plugin-based adapter system
- Interface: Python Protocol + TypedDict
- Supported AI Tools:
  - IDE integrated (VS Code Copilot, JetBrains AI)
  - CLI tools (Claude Code, Cursor, Aider)
  - Cloud API (OpenAI, Anthropic, Google Gemini)
  - Local models (Ollama, LM Studio)

**3. 可视化引擎 (Visualization Engine)**
- **Cytoscape.js**: Main behavioral sandbox (hierarchical code structure graph)
- **D3.js**: Detail analysis (flowcharts, sequence diagrams)
- **Monaco Editor**: Step-by-step detail view (code editor + debugger UI)
- **Animation**: Canvas + requestAnimationFrame

### Data Protocol

**Standard Format**: JSON Schema v1.0.0
- Schema file: `shared/schemas/analysis-schema-v1.0.0.json`
- Backward compatibility: ≥2 MAJOR versions
- Key sections:
  - `code_structure`: Nodes and edges for Cytoscape.js
  - `execution_trace`: Traceable units with multiple trace formats
  - `concurrency_info`: Concurrent flows and sync points
  - `behavior_metadata`: Launch buttons configuration
  - `prompt_templates`: Used prompt records

### AI Analysis Stages

5-stage sequential analysis with stage-level parallelization:

1. **Project Understanding** (30-60s): Project type, language, framework detection
2. **Structure Recognition** (1-30min): Module/class/function extraction
3. **Semantic Analysis** (1-40min): Business naming and functional descriptions
4. **Execution Inference** (1-50min): Execution traces (flowchart, sequence, step-by-step)
5. **Concurrency Detection** (0.5-20min): Concurrent patterns and sync points

## Project Structure

```
backend/
├── aiflow/
│   ├── adapters/          # AI Adapter Layer
│   ├── prompts/           # Prompt Library management
│   ├── analysis/          # AI Scheduling Engine
│   ├── protocol/          # Standardized Data Protocol
│   └── api/               # REST API & WebSocket
├── prompts/               # YAML prompt templates
└── tests/

frontend/
├── src/
│   ├── components/
│   │   ├── StructureGraph/      # Cytoscape.js
│   │   ├── DetailViews/         # D3.js
│   │   ├── StepDetailView/      # Monaco Editor
│   │   └── AnimationControl/
│   ├── services/          # API client, WebSocket, Animation
│   ├── stores/            # Zustand state management
│   └── types/             # TypeScript types
└── tests/

shared/
└── schemas/               # JSON Schema definitions
```

## Performance Targets

- **Small projects** (<500 nodes): First render <1s, level switch <150ms
- **Medium projects** (500-2000 nodes): First render <3s, level switch <300ms
- **Large projects** (2000-5000 nodes): First render <8s, level switch <500ms
- **AI analysis**: Small 2-5min, Medium 10-20min, Large 30-60min (with resume support)
- **Animation**: ≤5 concurrent flows ≥30 FPS

## Key Constraints

- Memory: Medium projects ≤500MB, Large projects ≤1GB
- API response: P95 <500ms
- WebSocket latency: <50ms
- Concurrency: ≥100 concurrent connections, ≥50 concurrent animation sessions

## Testing Requirements

- **Backend**: Unit test coverage ≥85%
- **Frontend**: Unit test coverage ≥80%
- **E2E**: All critical user flows covered
- **Performance**: Benchmark tests with standard test project set

## Documentation

- **Research**: `/specs/001-ai/research.md` - Technology decisions
- **Data Model**: `/specs/001-ai/data-model.md` - Entities and relationships
- **Contracts**: `/specs/001-ai/contracts/` - API contracts and JSON Schema
- **Quick Start**: `/specs/001-ai/quickstart.md` - Installation and usage guide
- **Plan**: `/specs/001-ai/plan.md` - Implementation plan and phases

## Constitution Compliance

All 6 core principles satisfied:
- ✅ I. AI Command-Driven Strategy (Prompt Library with 5-stage orchestration)
- ✅ II. Open Connectivity (Plugin-based adapters, 4 AI tool types)
- ✅ III. Intelligent Layering & Behavior-Driven Interaction (Cytoscape.js hierarchical)
- ✅ IV. Behavior Nesting (Nested launch buttons, macro/micro execution)
- ✅ V. Concurrency Visualization (Sequence diagrams, Fork/Join flowcharts)
- ✅ VI. User Complete Control (Animation control, step-by-step detail view)

## Current Phase

**Phase**: Planning Complete, Ready for Implementation
**Next Step**: Phase 2 - Foundation (AI Scheduling Layer)
**Start Date**: 2025-10-10 (estimated)

## Key Design Decisions

1. **Prompt Template Engine**: YAML + Jinja2 (human-readable, powerful templating)
2. **AI Scheduling**: 5-stage serial with stage-level parallelization
3. **Adapter Architecture**: Plugin-based with standardized Protocol interface
4. **Data Protocol**: JSON Schema v1.0.0 (strict validation, backward compatible)
5. **Main Sandbox**: Cytoscape.js (large graph performance, compound nodes)
6. **Detail Analysis**: D3.js (flexibility, custom animations)
7. **Step Detail**: Monaco Editor (VS Code kernel, professional experience)
8. **Animation**: Canvas + RAF (high performance, ≥30 FPS for 5 concurrent flows)
9. **Frontend Framework**: React 18 (concurrent mode for complex animations)
10. **Desktop App**: Tauri (priority, small footprint) or Electron (fallback)

## Common Commands

```bash
# Backend
cd backend
poetry install
poetry run uvicorn aiflow.main:app --reload

# Frontend
cd frontend
pnpm install
pnpm dev

# Testing
poetry run pytest  # Backend
pnpm test          # Frontend

# Analysis
aiflow analyze /path/to/project --adapter claude-code-adapter
aiflow visualize analysis-result.json
```

## Important Notes

- **AI Analysis Time**: Deep semantic analysis requires 2-60 minutes depending on project size
- **Cache Strategy**: 70%+ cache hit rate target through LRU eviction
- **Incremental Analysis**: Only re-analyze changed files and dependency chain
- **Offline Mode**: Support pre-generated analysis result files
- **Graceful Degradation**: 5-level degradation (full → partial → cache → static → offline)
- **Virtualization**: Auto-enable for >1000 nodes to maintain performance

## Risk Mitigations

- **AI Accuracy**: Confidence scoring + human feedback loop + multi-model comparison (optional)
- **Long Analysis**: Smart scope limiting + resume capability + background task queue
- **Performance**: Virtualization + LOD + Canvas layering + Web Workers
- **Connection Stability**: Multi-adapter support + 5-level degradation + cache
- **Learning Curve**: 15-minute onboarding + interactive tutorial + sample projects
