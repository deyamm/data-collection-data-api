"""
Combined task template and handler registry.
"""

import hashlib
import json
import logging
from datetime import datetime
from typing import Callable, Dict, List, Optional, Awaitable

from app.schemas.collection_task.task_template import OutputField, TaskRunRequest, TaskRunResult, TaskTemplateInfo

logger = logging.getLogger(__name__)


HandleFuncType = Callable[[TaskRunRequest], Awaitable[TaskRunResult]]


class Registry:
    """
    In-memory registry for task templates and handlers.
    """

    def __init__(self) -> None:
        # key: taskCode, value: TaskTemplateInfo
        self._task_registry: Dict[str, TaskTemplateInfo] = {}
        # key: handlerName, value: callable
        self._handler_registry: Dict[str, HandleFuncType] = {}

    def register_task_template(self, template: TaskTemplateInfo) -> None:
        """Register or update task template info."""
        template.sync_time = template.sync_time or datetime.now()
        self._task_registry[template.task_code] = template
        logger.info("TaskRegistry: registered taskCode=%s", template.task_code)

    def register_handler(self, handler_name: str, handler_func: HandleFuncType) -> None:
        """Register a handler function."""
        self._handler_registry[handler_name] = handler_func
        logger.info("HandlerRegistry: registered handler=%s", handler_name)

    def get_all_task_templates(self) -> List[TaskTemplateInfo]:
        """Return all registered task templates."""
        return list(self._task_registry.values())

    def get_task_template(self, task_code: str) -> Optional[TaskTemplateInfo]:
        """Return a single template by task code."""
        return self._task_registry.get(task_code)

    def get_handler(self, handler_name: str) -> Optional[HandleFuncType]:
        """Return a handler by name."""
        return self._handler_registry.get(handler_name)

    async def execute(self, request: TaskRunRequest) -> TaskRunResult:
        """Execute a handler based on request.handlerName."""
        handler = self.get_handler(request.handler_name)
        if handler is None:
            logger.error("HandlerRegistry: handler not found, handlerName=%s", request.handler_name)
            return TaskRunResult(
                run_id=request.run_id,
                status="FAILED",
                total_count=0,
                success_count=0,
                failure_count=1,
                summary_content={"error": f"Handler not found: {request.handler_name}"},
            )

        try:
            logger.info("HandlerRegistry: executing runId=%s, handler=%s", request.run_id, request.handler_name)
            result = await handler(request)
            logger.info("HandlerRegistry: done runId=%s, total=%s, success=%s, failure=%s", request.run_id, result.total_count, result.success_count, result.failure_count)
            return result
        except Exception as exc:  # noqa: BLE001
            logger.exception("HandlerRegistry: handler raised exception, runId=%s", request.run_id)
            return TaskRunResult(
                run_id=request.run_id,
                status="FAILED",
                total_count=0,
                success_count=0,
                failure_count=1,
                summary_content={"error": str(exc)},
            )

    @staticmethod
    def compute_output_fields_hash(output_fields: List[OutputField]) -> str:
        """Compute MD5 hash of output fields JSON."""
        fields_json = json.dumps(
            [field.model_dump() for field in output_fields],
            ensure_ascii=False,
            sort_keys=True,
        )
        return hashlib.md5(fields_json.encode("utf-8")).hexdigest()


# Global singleton registry
registry = Registry()
