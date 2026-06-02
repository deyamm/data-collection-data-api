import logging
from typing import Any
import httpx
from app.core.registry import registry
from app.core.config import settings
from app.schemas.collection_task.task_template import TaskRunRequest, TaskRunResult

logger = logging.getLogger(__name__)

async def post_callback(payload: dict[str, Any]) -> None:
    url = settings.SPRING_CALLBACK_BASE_URL.rstrip("/") + "/api/v1/task-runs/callback"
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, json=payload)
            logger.info("Posted callback to %s, status=%s", url, resp.status_code)
    except Exception as e:
        logger.exception("Failed to post callback to %s: %s", url, e)


async def _run_and_callback(req: TaskRunRequest) -> None:
    try:
        result = await registry.execute(req)
    except Exception as exc:
        logger.exception("Background execution failed for runId=%s", req.run_id)

        result = TaskRunResult(
            run_id=req.run_id,
            status="FAILED",
            total_count=0,
            success_count=0,
            failure_count=1,
            result_location=None,
            summary_content={"error": str(exc)},
            logs=[],
            problems=[],
            exceptions=[
                {
                    "message": str(exc),
                    "type": exc.__class__.__name__,
                }
            ],
        )

    await post_callback(result.model_dump(by_alias=True))
