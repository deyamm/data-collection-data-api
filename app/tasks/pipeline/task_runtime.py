from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from app.schemas.collection_task.task_template import ProblemRecord


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class TaskRuntime:
    """
    单次任务执行的运行态信息。

    注意：
    这里不保存 raw_rows、normalized_rows、valid_rows、physical_rows 等全量数据。
    Runtime 只保存统计信息、日志、问题样本和当前执行阶段。
    """

    run_id: str
    task_code: str

    current_stage: str = "CREATED"
    started_at: str = field(default_factory=utc_now_iso)
    finished_at: str | None = None

    collected_count: int = 0
    normalized_count: int = 0
    valid_count: int = 0
    mapped_count: int = 0
    write_count: int = 0

    success_count: int = 0
    problem_count: int = 0
    exception_count: int = 0

    problems: list[ProblemRecord] = field(default_factory=list)
    logs: list[dict[str, Any]] = field(default_factory=list)

    max_problem_samples: int = 100
    max_log_records: int = 500

    log_count: int = 0
    problem_samples_truncated: bool = False
    logs_truncated: bool = False

    def set_stage(self, stage: str) -> None:
        self.current_stage = stage

    def add_log(self, level: str, message: str) -> None:
        self.log_count += 1

        if len(self.logs) >= self.max_log_records:
            self.logs_truncated = True
            return

        self.logs.append(
            {
                "time": utc_now_iso(),
                "level": level,
                "stage": self.current_stage,
                "message": message,
            }
        )

    def add_problems(self, problems: list[ProblemRecord]) -> None:
        if not problems:
            return

        self.problem_count += len(problems)

        remain = self.max_problem_samples - len(self.problems)
        if remain <= 0:
            self.problem_samples_truncated = True
            return

        self.problems.extend(problems[:remain])

        if len(problems) > remain:
            self.problem_samples_truncated = True

    def finish(self) -> None:
        self.finished_at = utc_now_iso()

    def to_summary(self) -> dict[str, Any]:
        return {
            "processed_count": self.collected_count,
            "success_count": self.success_count,
            "problem_count": self.problem_count,
            "exception_count": self.exception_count,
            "write_count": self.write_count,
            "collected_count": self.collected_count,
            "normalized_count": self.normalized_count,
            "valid_count": self.valid_count,
            "mapped_count": self.mapped_count,
            "current_stage": self.current_stage,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "problem_samples_truncated": self.problem_samples_truncated,
            "logs_truncated": self.logs_truncated,
        }