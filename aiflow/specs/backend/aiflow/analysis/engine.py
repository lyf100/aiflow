"""
AIFlow Analysis Engine
AI 分析调度引擎 - 协调 5 阶段分析流程

核心功能:
1. 协调 5 阶段分析流程 (项目认知→结构识别→语义分析→执行推理→并发检测)
2. Prompt 模板加载和渲染
3. AI 模型调用
4. 结果验证和合并
5. 进度追踪和状态管理
"""

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from uuid import uuid4

from ..adapters.base import BaseAIAdapter, AIResponse
from ..prompts.manager import PromptTemplateManager
from ..prompts.renderer import PromptRenderer
from ..protocol.validator import ProtocolValidator, ValidationResult
from ..protocol.serializer import ProtocolSerializer


class AnalysisStage(Enum):
    """分析阶段枚举"""
    PROJECT_UNDERSTANDING = "project_understanding"
    STRUCTURE_RECOGNITION = "structure_recognition"
    SEMANTIC_ANALYSIS = "semantic_analysis"
    EXECUTION_INFERENCE = "execution_inference"
    CONCURRENCY_DETECTION = "concurrency_detection"


class AnalysisStatus(Enum):
    """分析状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class StageResult:
    """阶段分析结果"""
    stage: AnalysisStage
    status: AnalysisStatus
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    ai_response: Optional[AIResponse] = None
    validation_result: Optional[ValidationResult] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    @property
    def duration(self) -> Optional[float]:
        """计算执行时长（秒）"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


@dataclass
class AnalysisJob:
    """分析任务"""
    id: str
    language: str  # 编程语言
    project_path: Path
    project_name: str
    status: AnalysisStatus
    current_stage: Optional[AnalysisStage] = None
    stage_results: Dict[AnalysisStage, StageResult] = None
    final_result: Optional[Dict[str, Any]] = None
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        if self.stage_results is None:
            self.stage_results = {}
        if self.created_at is None:
            self.created_at = datetime.now()

    @property
    def duration(self) -> Optional[float]:
        """计算总执行时长（秒）"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


# 进度回调类型
ProgressCallback = Callable[[AnalysisJob, AnalysisStage, float], None]


class AnalysisEngine:
    """分析调度引擎"""

    # 5 阶段执行顺序
    STAGE_ORDER = [
        AnalysisStage.PROJECT_UNDERSTANDING,
        AnalysisStage.STRUCTURE_RECOGNITION,
        AnalysisStage.SEMANTIC_ANALYSIS,
        AnalysisStage.EXECUTION_INFERENCE,
        AnalysisStage.CONCURRENCY_DETECTION,
    ]

    def __init__(
        self,
        ai_adapter: BaseAIAdapter,
        prompts_dir: Optional[Path] = None,
        validate_results: bool = True
    ):
        """
        初始化分析引擎

        Args:
            ai_adapter: AI 适配器实例
            prompts_dir: Prompt 模板目录 (可选)
            validate_results: 是否验证结果 (默认 True)
        """
        self.ai_adapter = ai_adapter
        self.prompt_manager = PromptTemplateManager(prompts_dir)
        self.prompt_renderer = PromptRenderer(self.prompt_manager)
        self.validator = ProtocolValidator() if validate_results else None
        self.serializer = ProtocolSerializer(validate_on_serialize=validate_results)
        self.validate_results = validate_results

        # 任务存储
        self.jobs: Dict[str, AnalysisJob] = {}

    async def create_job(
        self,
        language: str,
        project_path: Path,
        project_name: Optional[str] = None
    ) -> AnalysisJob:
        """
        创建分析任务

        Args:
            language: 编程语言
            project_path: 项目路径
            project_name: 项目名称 (可选，默认使用目录名)

        Returns:
            AnalysisJob: 分析任务
        """
        if not project_path.exists():
            raise ValueError(f"Project path does not exist: {project_path}")

        if project_name is None:
            project_name = project_path.name

        job = AnalysisJob(
            id=str(uuid4()),
            language=language,
            project_path=project_path,
            project_name=project_name,
            status=AnalysisStatus.PENDING,
        )

        self.jobs[job.id] = job
        return job

    async def run_job(
        self,
        job_id: str,
        progress_callback: Optional[ProgressCallback] = None
    ) -> AnalysisJob:
        """
        执行分析任务

        Args:
            job_id: 任务 ID
            progress_callback: 进度回调函数 (可选)

        Returns:
            AnalysisJob: 完成的任务

        Raises:
            ValueError: 任务不存在
            RuntimeError: 任务已在运行或已完成
        """
        if job_id not in self.jobs:
            raise ValueError(f"Job not found: {job_id}")

        job = self.jobs[job_id]

        if job.status in [AnalysisStatus.RUNNING, AnalysisStatus.COMPLETED]:
            raise RuntimeError(f"Job already {job.status.value}: {job_id}")

        # 更新状态
        job.status = AnalysisStatus.RUNNING
        job.started_at = datetime.now()

        try:
            # 执行 5 阶段分析
            for idx, stage in enumerate(self.STAGE_ORDER):
                job.current_stage = stage

                # 进度回调
                if progress_callback:
                    progress = (idx / len(self.STAGE_ORDER)) * 100
                    progress_callback(job, stage, progress)

                # 执行阶段
                stage_result = await self._run_stage(job, stage)
                job.stage_results[stage] = stage_result

                # 检查是否失败
                if stage_result.status == AnalysisStatus.FAILED:
                    job.status = AnalysisStatus.FAILED
                    job.completed_at = datetime.now()
                    return job

            # 合并结果
            job.final_result = self._merge_results(job)

            # 完成
            job.status = AnalysisStatus.COMPLETED
            job.completed_at = datetime.now()

            # 最终进度回调
            if progress_callback:
                progress_callback(job, job.current_stage, 100.0)

        except Exception as e:
            job.status = AnalysisStatus.FAILED
            job.completed_at = datetime.now()
            raise RuntimeError(f"Job execution failed: {e}") from e

        return job

    async def _run_stage(
        self,
        job: AnalysisJob,
        stage: AnalysisStage
    ) -> StageResult:
        """
        执行单个分析阶段

        Args:
            job: 分析任务
            stage: 分析阶段

        Returns:
            StageResult: 阶段结果
        """
        result = StageResult(
            stage=stage,
            status=AnalysisStatus.RUNNING,
            started_at=datetime.now()
        )

        try:
            # 1. 准备输入数据
            input_data = self._prepare_stage_input(job, stage)

            # 2. 加载和渲染 Prompt
            rendered_prompt = self.prompt_renderer.render(
                language=job.language,
                stage=stage.value,
                input_data=input_data,
                validate_input=True
            )

            # 3. 调用 AI
            ai_response = await self.ai_adapter.generate_with_retry(
                prompt=rendered_prompt,
                system_prompt="You are an expert code analyzer. Respond with valid JSON only."
            )
            result.ai_response = ai_response

            # 4. 解析 JSON 响应
            try:
                stage_data = json.loads(ai_response.content)
            except json.JSONDecodeError as e:
                result.status = AnalysisStatus.FAILED
                result.error = f"Invalid JSON response: {e}"
                result.completed_at = datetime.now()
                return result

            # 5. 验证结果
            if self.validate_results:
                validation_result = self.validator.validate_complete(stage_data)
                result.validation_result = validation_result

                if not validation_result.is_valid:
                    result.status = AnalysisStatus.FAILED
                    result.error = f"Validation failed: {validation_result.errors}"
                    result.completed_at = datetime.now()
                    return result

            # 6. 保存结果
            result.data = stage_data
            result.status = AnalysisStatus.COMPLETED
            result.completed_at = datetime.now()

        except Exception as e:
            result.status = AnalysisStatus.FAILED
            result.error = str(e)
            result.completed_at = datetime.now()

        return result

    def _prepare_stage_input(
        self,
        job: AnalysisJob,
        stage: AnalysisStage
    ) -> Dict[str, Any]:
        """
        准备阶段输入数据

        Args:
            job: 分析任务
            stage: 分析阶段

        Returns:
            Dict[str, Any]: 输入数据
        """
        input_data = {
            "project_path": str(job.project_path),
            "project_name": job.project_name,
        }

        # 根据阶段添加前置结果
        if stage == AnalysisStage.PROJECT_UNDERSTANDING:
            # 第一阶段：需要文件树等基础信息
            input_data.update({
                "file_tree": self._get_file_tree(job.project_path),
                "current_timestamp_iso8601": datetime.now().isoformat() + "Z",
                "ai_model_name": self.ai_adapter.get_model_name(),
            })

        elif stage == AnalysisStage.STRUCTURE_RECOGNITION:
            # 第二阶段：需要第一阶段结果
            prev_result = job.stage_results.get(AnalysisStage.PROJECT_UNDERSTANDING)
            if prev_result and prev_result.data:
                input_data["project_metadata_json"] = json.dumps(
                    prev_result.data.get("project_metadata", {}),
                    ensure_ascii=False
                )

        elif stage == AnalysisStage.SEMANTIC_ANALYSIS:
            # 第三阶段：需要前两阶段结果
            prev_results = [
                job.stage_results.get(AnalysisStage.PROJECT_UNDERSTANDING),
                job.stage_results.get(AnalysisStage.STRUCTURE_RECOGNITION),
            ]
            for prev_result in prev_results:
                if prev_result and prev_result.data:
                    input_data["project_metadata_json"] = json.dumps(
                        prev_result.data.get("project_metadata", {}),
                        ensure_ascii=False
                    )
                    input_data["code_structure_json"] = json.dumps(
                        prev_result.data.get("code_structure", {}),
                        ensure_ascii=False
                    )

        # 其他阶段类似...

        return input_data

    def _get_file_tree(self, project_path: Path, max_depth: int = 3) -> str:
        """
        获取项目文件树

        Args:
            project_path: 项目路径
            max_depth: 最大深度

        Returns:
            str: 文件树文本表示
        """
        lines = []

        def walk(path: Path, prefix: str = "", depth: int = 0):
            if depth > max_depth:
                return

            entries = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
            for idx, entry in enumerate(entries):
                is_last = idx == len(entries) - 1
                connector = "└── " if is_last else "├── "
                lines.append(f"{prefix}{connector}{entry.name}")

                if entry.is_dir() and not entry.name.startswith("."):
                    extension = "    " if is_last else "│   "
                    walk(entry, prefix + extension, depth + 1)

        lines.append(project_path.name + "/")
        walk(project_path)
        return "\n".join(lines)

    def _merge_results(self, job: AnalysisJob) -> Dict[str, Any]:
        """
        合并所有阶段结果

        Args:
            job: 分析任务

        Returns:
            Dict[str, Any]: 完整的分析结果
        """
        merged = {
            "$schema": "https://aiflow.dev/schemas/analysis-v1.0.0.json",
            "version": "1.0.0",
            "project_metadata": {},
            "code_structure": {"nodes": [], "edges": []},
            "execution_trace": {"traceable_units": []},
        }

        for stage in self.STAGE_ORDER:
            stage_result = job.stage_results.get(stage)
            if stage_result and stage_result.data:
                merged.update(stage_result.data)

        return merged

    async def save_result(
        self,
        job_id: str,
        output_path: Path,
        compress: bool = False
    ) -> None:
        """
        保存分析结果到文件

        Args:
            job_id: 任务 ID
            output_path: 输出文件路径
            compress: 是否压缩 (默认 False)
        """
        if job_id not in self.jobs:
            raise ValueError(f"Job not found: {job_id}")

        job = self.jobs[job_id]

        if job.status != AnalysisStatus.COMPLETED:
            raise RuntimeError(f"Job not completed: {job.status.value}")

        if not job.final_result:
            raise RuntimeError("No result to save")

        self.serializer.serialize(
            job.final_result,
            output_path,
            compress=compress,
            validate=self.validate_results
        )

    def get_job(self, job_id: str) -> Optional[AnalysisJob]:
        """获取任务"""
        return self.jobs.get(job_id)

    def list_jobs(self) -> List[AnalysisJob]:
        """列出所有任务"""
        return list(self.jobs.values())
