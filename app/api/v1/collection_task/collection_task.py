"""
采集任务处理路由
对应接口：
  GET  /api/v1/collection-task/task-templates/current  - 返回当前已注册的任务模板列表（供 Spring Boot 拉取）
  POST /api/v1/collection-task/task-runs/execute       - 接收 Spring Boot 下发的执行上下文并执行任务
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks

from app.schemas.collection_task.task_template import TaskRunRequest, TaskRunResult, TaskTemplateInfo
from app.core.registry import registry
from app.core.callback_client import _run_and_callback


logger  = logging.getLogger(__name__)
router  = APIRouter()


@router.get(
    "/task-templates/current",
    response_model=List[TaskTemplateInfo],
    summary="I-35 获取当前任务模板列表",
    description=(
        "返回任务处理层当前所有已注册的采集任务模板信息（含返回字段 JSON）。"
        "应用服务层在手动同步时调用此接口拉取全量或指定模板。"
    )
)
def get_current_templates(
    task_code: Optional[str] = Query(None, alias="taskCode", description="指定任务编码；为空时返回全量模板")
) -> List[TaskTemplateInfo]:
    """
    获取当前已注册的任务模板列表

    - 若指定 taskCode，则只返回该任务的模板信息；
    - 若不指定，返回全量已注册模板列表；
    - 模板信息中包含返回字段 JSON（outputFields），供 Spring Boot 解析并匹配数据类型版本。
    """
    logger.info("get_current_templates called, taskCode=%s", task_code)

    if task_code:
        template = registry.get_task_template(task_code)
        if template is None:
            raise HTTPException(status_code=404, detail=f"Task template not found: {task_code}")
        return [template]

    templates = registry.get_all_task_templates()
    logger.info("get_current_templates returning %d templates", len(templates))
    return templates


@router.post(
    "/task-runs/execute",
    response_model=TaskRunResult,
    summary="执行任务处理",
    description=(
        "接收应用服务层（Spring Boot）下发的执行上下文，并返回正在执行的状态，使用BackgroundTasks异步执行任务，包括根据 handlerName 找到对应处理函数、执行任务、返回结果。"
    )
)
async def execute_task_run(request: TaskRunRequest, background_tasks: BackgroundTasks) -> TaskRunResult:
    logger.info(
        "execute_task_run called, runId=%s, taskCode=%s, handler=%s",
        request.run_id, request.task_code, request.handler_name,
    )

    background_tasks.add_task(_run_and_callback, request)

    return TaskRunResult(
        run_id=request.run_id,
        status="RUNNING",
        total_count=0,
        success_count=0,
        failure_count=0,
        result_location=None,
        summary_content={"message": "Execution scheduled"},
        logs=[],
        problems=[],
        exceptions=None,
    )
