"""
AIFlow Analysis Task Queue
分析任务队列 - 异步任务管理和并发控制

核心功能:
1. 异步任务队列
2. 并发控制 (最大并发任务数)
3. 优先级队列
4. 任务取消和超时
5. 任务状态追踪
"""

import asyncio
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Deque, Dict, Optional, Set
from uuid import uuid4


class TaskPriority(Enum):
    """任务优先级"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3


class TaskState(Enum):
    """任务状态"""
    PENDING = "pending"  # 等待执行
    RUNNING = "running"  # 正在执行
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败
    CANCELLED = "cancelled"  # 已取消
    TIMEOUT = "timeout"  # 超时


@dataclass
class QueueTask:
    """队列任务"""
    id: str
    name: str
    func: Callable
    args: tuple
    kwargs: dict
    priority: TaskPriority
    state: TaskState
    result: Optional[Any] = None
    error: Optional[Exception] = None
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    timeout: Optional[float] = None  # 超时时间(秒)

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    @property
    def duration(self) -> Optional[float]:
        """计算执行时长（秒）"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def waiting_time(self) -> Optional[float]:
        """计算等待时长（秒）"""
        if self.started_at:
            return (self.started_at - self.created_at).total_seconds()
        return (datetime.now() - self.created_at).total_seconds()


class TaskQueue:
    """分析任务队列"""

    def __init__(
        self,
        max_concurrent: int = 5,
        max_queue_size: int = 1000
    ):
        """
        初始化任务队列

        Args:
            max_concurrent: 最大并发任务数 (默认 5)
            max_queue_size: 最大队列大小 (默认 1000)
        """
        self.max_concurrent = max_concurrent
        self.max_queue_size = max_queue_size

        # 任务存储
        self.tasks: Dict[str, QueueTask] = {}

        # 优先级队列 (使用 deque 实现)
        self.queues: Dict[TaskPriority, Deque[str]] = {
            priority: deque() for priority in TaskPriority
        }

        # 正在运行的任务
        self.running_tasks: Set[str] = set()

        # 事件循环
        self._worker_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()

    async def start(self) -> None:
        """启动队列处理器"""
        if self._worker_task is not None:
            raise RuntimeError("Queue already started")

        self._shutdown_event.clear()
        self._worker_task = asyncio.create_task(self._worker())

    async def stop(self, timeout: Optional[float] = 10.0) -> None:
        """
        停止队列处理器

        Args:
            timeout: 等待超时时间(秒)，None 表示无限等待
        """
        if self._worker_task is None:
            return

        # 设置关闭事件
        self._shutdown_event.set()

        # 等待 worker 完成
        try:
            if timeout is not None:
                await asyncio.wait_for(self._worker_task, timeout=timeout)
            else:
                await self._worker_task
        except asyncio.TimeoutError:
            # 强制取消
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass

        self._worker_task = None

    async def submit(
        self,
        func: Callable,
        *args: Any,
        name: Optional[str] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        timeout: Optional[float] = None,
        **kwargs: Any
    ) -> str:
        """
        提交任务到队列

        Args:
            func: 异步函数
            *args: 函数参数
            name: 任务名称 (可选)
            priority: 任务优先级 (默认 NORMAL)
            timeout: 超时时间(秒) (可选)
            **kwargs: 函数关键字参数

        Returns:
            str: 任务 ID

        Raises:
            RuntimeError: 队列已满
        """
        # 检查队列大小
        total_queued = sum(len(q) for q in self.queues.values())
        if total_queued >= self.max_queue_size:
            raise RuntimeError(f"Queue is full (max: {self.max_queue_size})")

        # 创建任务
        task_id = str(uuid4())
        task = QueueTask(
            id=task_id,
            name=name or f"Task-{task_id[:8]}",
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            state=TaskState.PENDING,
            timeout=timeout,
        )

        # 保存任务
        self.tasks[task_id] = task

        # 加入对应优先级队列
        self.queues[priority].append(task_id)

        return task_id

    async def cancel(self, task_id: str) -> bool:
        """
        取消任务

        Args:
            task_id: 任务 ID

        Returns:
            bool: 是否成功取消
        """
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]

        # 只能取消 PENDING 或 RUNNING 的任务
        if task.state not in [TaskState.PENDING, TaskState.RUNNING]:
            return False

        if task.state == TaskState.PENDING:
            # 从队列中移除
            try:
                self.queues[task.priority].remove(task_id)
            except ValueError:
                pass

        task.state = TaskState.CANCELLED
        task.completed_at = datetime.now()

        return True

    def get_task(self, task_id: str) -> Optional[QueueTask]:
        """获取任务"""
        return self.tasks.get(task_id)

    async def wait_for_task(
        self,
        task_id: str,
        timeout: Optional[float] = None
    ) -> QueueTask:
        """
        等待任务完成

        Args:
            task_id: 任务 ID
            timeout: 超时时间(秒)

        Returns:
            QueueTask: 完成的任务

        Raises:
            ValueError: 任务不存在
            asyncio.TimeoutError: 等待超时
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task not found: {task_id}")

        task = self.tasks[task_id]
        start_time = asyncio.get_event_loop().time()

        # 轮询任务状态
        while task.state in [TaskState.PENDING, TaskState.RUNNING]:
            if timeout is not None:
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed >= timeout:
                    raise asyncio.TimeoutError(
                        f"Waiting for task {task_id} timed out"
                    )

            await asyncio.sleep(0.1)

        return task

    def get_stats(self) -> Dict[str, Any]:
        """获取队列统计信息"""
        stats = {
            "total_tasks": len(self.tasks),
            "running": len(self.running_tasks),
            "pending": sum(len(q) for q in self.queues.values()),
            "completed": sum(1 for t in self.tasks.values() if t.state == TaskState.COMPLETED),
            "failed": sum(1 for t in self.tasks.values() if t.state == TaskState.FAILED),
            "cancelled": sum(1 for t in self.tasks.values() if t.state == TaskState.CANCELLED),
            "timeout": sum(1 for t in self.tasks.values() if t.state == TaskState.TIMEOUT),
            "max_concurrent": self.max_concurrent,
            "queue_by_priority": {
                priority.name: len(queue)
                for priority, queue in self.queues.items()
            },
        }

        # 计算平均等待时间和执行时间
        completed_tasks = [t for t in self.tasks.values() if t.state == TaskState.COMPLETED]
        if completed_tasks:
            stats["avg_waiting_time"] = sum(t.waiting_time or 0 for t in completed_tasks) / len(completed_tasks)
            stats["avg_duration"] = sum(t.duration or 0 for t in completed_tasks) / len(completed_tasks)

        return stats

    async def _worker(self) -> None:
        """任务处理器 (内部使用)"""
        while not self._shutdown_event.is_set():
            # 检查是否可以启动新任务
            if len(self.running_tasks) >= self.max_concurrent:
                await asyncio.sleep(0.1)
                continue

            # 获取下一个任务 (按优先级)
            task_id = self._get_next_task()
            if task_id is None:
                await asyncio.sleep(0.1)
                continue

            # 启动任务
            asyncio.create_task(self._run_task(task_id))

    def _get_next_task(self) -> Optional[str]:
        """获取下一个待执行任务 (按优先级)"""
        # 按优先级从高到低遍历
        for priority in sorted(TaskPriority, key=lambda p: p.value, reverse=True):
            queue = self.queues[priority]
            if queue:
                return queue.popleft()
        return None

    async def _run_task(self, task_id: str) -> None:
        """执行任务 (内部使用)"""
        task = self.tasks[task_id]

        # 标记为运行中
        task.state = TaskState.RUNNING
        task.started_at = datetime.now()
        self.running_tasks.add(task_id)

        try:
            # 执行任务 (带超时)
            if task.timeout:
                task.result = await asyncio.wait_for(
                    task.func(*task.args, **task.kwargs),
                    timeout=task.timeout
                )
            else:
                task.result = await task.func(*task.args, **task.kwargs)

            task.state = TaskState.COMPLETED

        except asyncio.TimeoutError:
            task.state = TaskState.TIMEOUT
            task.error = TimeoutError(f"Task timeout after {task.timeout}s")

        except asyncio.CancelledError:
            task.state = TaskState.CANCELLED

        except Exception as e:
            task.state = TaskState.FAILED
            task.error = e

        finally:
            task.completed_at = datetime.now()
            self.running_tasks.discard(task_id)


# 全局队列实例 (可选)
_global_queue: Optional[TaskQueue] = None


def get_global_queue(
    max_concurrent: int = 5,
    max_queue_size: int = 1000
) -> TaskQueue:
    """
    获取全局任务队列实例

    Args:
        max_concurrent: 最大并发任务数
        max_queue_size: 最大队列大小

    Returns:
        TaskQueue: 全局队列实例
    """
    global _global_queue
    if _global_queue is None:
        _global_queue = TaskQueue(max_concurrent, max_queue_size)
    return _global_queue


# CLI 测试入口
if __name__ == "__main__":
    import sys

    async def example_task(name: str, duration: float) -> str:
        """示例任务"""
        print(f"Task {name} started")
        await asyncio.sleep(duration)
        print(f"Task {name} completed")
        return f"Result from {name}"

    async def main():
        # 创建队列
        queue = TaskQueue(max_concurrent=3)
        await queue.start()

        # 提交任务
        task_ids = []
        for i in range(10):
            priority = TaskPriority.HIGH if i < 3 else TaskPriority.NORMAL
            task_id = await queue.submit(
                example_task,
                f"Task-{i}",
                duration=1.0,
                priority=priority
            )
            task_ids.append(task_id)
            print(f"Submitted {task_id[:8]} with priority {priority.name}")

        # 等待所有任务完成
        for task_id in task_ids:
            task = await queue.wait_for_task(task_id)
            print(f"Task {task_id[:8]}: {task.state.value}, result={task.result}")

        # 打印统计
        print("\nQueue statistics:")
        stats = queue.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")

        # 停止队列
        await queue.stop()

    asyncio.run(main())
