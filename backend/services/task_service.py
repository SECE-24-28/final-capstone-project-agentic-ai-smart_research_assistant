"""
Task Service – In-memory task tracking for long-running agent operations.

Keeps a simple dict of task_id → TaskRecord so the frontend can poll
GET /agent/task/{task_id} for progress without requiring a DB write
on every update tick.

Results are optionally persisted to AgentTask in the DB when the
task completes, so the record survives server restarts.
"""
import uuid
import threading
from datetime import datetime
from typing import Optional, Dict, Any


class TaskRecord:
    def __init__(self, task_id: str, task_type: str):
        self.task_id = task_id
        self.task_type = task_type
        self.status = "pending"           # pending | running | done | failed
        self.progress = 0                 # 0-100
        self.current_step = "Initializing…"
        self.created_at = datetime.utcnow()
        self.completed_at: Optional[datetime] = None
        self.result: Optional[Any] = None
        self.error: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "status": self.status,
            "progress": self.progress,
            "current_step": self.current_step,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
        }


class TaskService:
    """Thread-safe in-memory task store."""

    def __init__(self):
        self._tasks: Dict[str, TaskRecord] = {}
        self._lock = threading.Lock()

    # ──────────────────────────────────────────────
    #  Public API
    # ──────────────────────────────────────────────

    def create(self, task_type: str) -> TaskRecord:
        task_id = str(uuid.uuid4())
        record = TaskRecord(task_id, task_type)
        with self._lock:
            self._tasks[task_id] = record
        return record

    def get(self, task_id: str) -> Optional[TaskRecord]:
        with self._lock:
            return self._tasks.get(task_id)

    def update(
        self,
        task_id: str,
        *,
        status: Optional[str] = None,
        progress: Optional[int] = None,
        current_step: Optional[str] = None,
        result: Optional[Any] = None,
        error: Optional[str] = None,
    ) -> None:
        with self._lock:
            record = self._tasks.get(task_id)
            if record is None:
                return
            if status is not None:
                record.status = status
            if progress is not None:
                record.progress = min(100, max(0, progress))
            if current_step is not None:
                record.current_step = current_step
            if result is not None:
                record.result = result
            if error is not None:
                record.error = error
            if status in ("done", "failed"):
                record.completed_at = datetime.utcnow()

    def mark_done(self, task_id: str, result: Any = None) -> None:
        self.update(task_id, status="done", progress=100,
                    current_step="Complete", result=result)

    def mark_failed(self, task_id: str, error: str) -> None:
        self.update(task_id, status="failed", error=error,
                    current_step="Failed")

    def cleanup_old(self, max_tasks: int = 200) -> None:
        """Evict the oldest tasks if the store grows too large."""
        with self._lock:
            if len(self._tasks) > max_tasks:
                oldest = sorted(self._tasks.values(),
                                key=lambda t: t.created_at)
                for task in oldest[: len(self._tasks) - max_tasks]:
                    del self._tasks[task.task_id]


# Singleton shared across the application
task_service = TaskService()
