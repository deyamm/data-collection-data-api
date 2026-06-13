from __future__ import annotations

from abc import ABC
from typing import Any, AsyncIterator, final
import logging

from app.schemas.collection_task.task_template import CleaningRule, ExecutionContext, TaskRunRequest, ResultLocation, ProblemRecord, TaskRunResult
from app.tasks.pipeline import normalize_rows, clean_rows, write_rows, TaskRuntime

logger = logging.getLogger(__name__)

class BaseCollectTask(ABC):
    """
    所有采集任务的基类。

    核心原则：
    1. execute() 封闭完整流程，子类不要重写，该方法实现两种采集方式：批量采集和单次采集。
    2. 子类实现 collect()或 collect_batches()，分别对应单次采集和批量采集。批量采集默认调用 collect()，特殊任务可重写 collect_batches() 实现分批处理。
     3. 处理流程包括：normalize -> clean -> map_fields -> write
    3. 特殊任务通过 hook 扩展。
    4. schema/table/field mapping 仍然来自后台执行快照。
    """

    task_code: str

    enable_normalize: bool = True
    enable_clean: bool = True
    enable_mapping: bool = True
    enable_write: bool = True

    @final
    async def execute(self, request: TaskRunRequest) -> TaskRunResult:
        runtime = TaskRuntime(run_id=request.run_id, task_code=request.task_code)
        ctx = request.execution_context

        try:
            runtime.set_stage("START")
            runtime.add_log("INFO", f"任务 {runtime.task_code} 开始执行，run_id={runtime.run_id}")
            logger.info(f"任务 {runtime.task_code} 开始执行，run_id={runtime.run_id}")   

            runtime.set_stage("VALIDATE_CONTEXT")
            await self.validate_context(ctx, runtime)

            runtime.set_stage("BEFORE_EXECUTE")
            await self.before_collect(ctx, runtime)

            # 批处理采集，默认一次批处理所有数据，特殊任务可重写 collect_batches 实现分批处理
            batch_no = 0
            total_rows = 0
            runtime.set_stage("COLLECT")
            async for raw_rows in self.collect_batches(ctx.params, ctx):
                batch_no += 1
                logger.info(f"处理第 {batch_no} 批数据，记录数: {len(raw_rows)}")

                raw_rows = await self.after_collect(ctx, raw_rows, runtime)

                runtime.collected_count += len(raw_rows)
                total_rows += len(raw_rows)
                logger.info(f"第 {batch_no} 批采集完成，原始记录数: {len(raw_rows)}")

                await self.process_batch(batch_no, raw_rows, ctx, runtime)
                del raw_rows  # 释放内存

            logger.info(f"所有批次采集完成，共{batch_no}批，累计原始记录数: {total_rows}")
            runtime.set_stage("AFTER_SUCCESS")
            await self.after_success(ctx, runtime)

            runtime.set_stage("SUCCESS")
            runtime.finish()

            return self.build_success_result(ctx, runtime)

        except Exception as exc:
            runtime.exception_count += 1
            runtime.add_log("ERROR", str(exc))
            logger.exception("执行失败")
            await self.after_failed(ctx, runtime, exc)

            runtime.set_stage("FAILED")
            runtime.finish()
            return self.build_failed_result(ctx, runtime, exc)

    async def validate_context(self, ctx: ExecutionContext, runtime: TaskRuntime) -> None:
        """
        验证后台传输的执行上下文的完整性和正确性。
        """
        if runtime.task_code != self.task_code:
            raise ValueError(f"任务编码不匹配: ctx.task_code={runtime.task_code}, task.task_code={self.task_code}")

        if not ctx.columns:
            raise ValueError("columns 不能为空")

        if self.enable_write:
            if not ctx.storage_mapping:
                raise ValueError("启用入库时 storage_mapping 不能为空")

            if not ctx.storage_mapping.physical_schema_name:
                raise ValueError("physical_schema_name 不能为空")

            if not ctx.storage_mapping.physical_table_name:
                raise ValueError("physical_table_name 不能为空")

            if not ctx.columns:
                raise ValueError("columns 不能为空")

    async def collect_batches(self, params: dict[str, Any], ctx: ExecutionContext) -> AsyncIterator[list[dict[str, Any]]]:
        """
        批量采集入口。

        默认行为：
        - 调用 collect()
        - 将原 collect() 的返回结果包装为单批

        大文件、大数据量任务可以重写本方法。
        """
        raw_rows = await self.collect(params, ctx)
        yield raw_rows

    async def process_batch(self, batch_no: int, raw_rows: list[dict[str, Any]], ctx: ExecutionContext, runtime: TaskRuntime) -> None:
        """
        单批次处理流程。

        每批独立执行：
        normalize -> clean -> map_fields -> write
        """
        runtime.set_stage("NORMALIZE")
        if self.enable_normalize:
            normalized_rows, problems = await self.normalize(ctx, raw_rows, runtime)
            runtime.problems.extend(problems)
        else:
            normalized_rows = raw_rows

        runtime.normalized_count += len(normalized_rows)
        runtime.add_log("INFO", f"第 {batch_no} 批标准化完成，记录数: {len(normalized_rows)}")
        logger.info(f"第 {batch_no} 批标准化完成，记录数: {len(normalized_rows)}")

        del raw_rows  # 释放内存

        runtime.set_stage("CLEAN")
        if self.enable_clean:
            valid_rows, problems = await self.clean(ctx, normalized_rows, runtime)
            runtime.problems.extend(problems)
        else:
            valid_rows = normalized_rows

        runtime.valid_count += len(valid_rows)
        runtime.add_log("INFO", f"第 {batch_no} 批清洗完成，有效记录数: {len(valid_rows)}，累计问题数: {len(runtime.problems)}")
        logger.info(f"第 {batch_no} 批清洗完成，有效记录数: {len(valid_rows)}，累计问题数: {len(runtime.problems)}")

        del normalized_rows  # 释放内存

        runtime.set_stage("MAP_FIELDS")
        if self.enable_mapping:
            physical_rows, problems = await self.map_fields(ctx, valid_rows, runtime)
            runtime.problems.extend(problems)
            if len(problems) > 0:
                logger.info(f"{problems[0]}")
        else:
            physical_rows, problems = valid_rows, []
            runtime.problems.extend(problems)

        runtime.mapped_count += len(physical_rows)
        runtime.add_log("INFO", f"第 {batch_no} 批字段映射完成，待入库记录数: {len(physical_rows)},累计问题数: {len(runtime.problems)}")
        logger.info(f"第 {batch_no} 批字段映射完成，待入库记录数: {len(physical_rows)}, 累计问题数: {len(runtime.problems)}")

        runtime.set_stage("WRITE")
        if self.enable_write:
            await self.before_write(ctx, runtime)
            write_count = await self.write(ctx, physical_rows, runtime)
            await self.after_write(ctx, runtime)
            
            runtime.write_count += write_count
            runtime.success_count += write_count
            runtime.add_log("INFO", f"第 {batch_no} 批入库完成，写入记录数: {write_count}")
            logger.info(f"第 {batch_no} 批入库完成，写入记录数: {write_count}")
        else:
            runtime.write_count = 0
            runtime.success_count += len(physical_rows)
            runtime.add_log("INFO", f"第 {batch_no} 批未启用入库，仅返回处理结果，记录数: {len(physical_rows)}")
            logger.info(f"第 {batch_no} 批未启用入库，仅返回处理结果，记录数: {len(physical_rows)}")
        
        del physical_rows  # 释放内存

    async def collect(self, params: dict[str, Any], ctx: ExecutionContext) -> list[dict[str, Any]]:
        """
        子类必须实现的采集逻辑。

        只负责从外部数据源采集数据。
        不负责清洗、字段映射、物理表选择、入库。
        """
        raise NotImplementedError

    async def before_collect(self, ctx: ExecutionContext, runtime: TaskRuntime) -> None:
        pass

    async def after_collect(self, ctx: ExecutionContext, raw_rows: list[dict[str, Any]], runtime: TaskRuntime) -> list[dict[str, Any]]:
        return raw_rows

    async def normalize(self, ctx: ExecutionContext, raw_rows: list[dict[str, Any]], runtime: TaskRuntime) -> tuple[list[dict[str, Any]], list[ProblemRecord]]:
        return normalize_rows(raw_rows, ctx.columns, target_layer="data_type")

    async def clean(self, ctx: ExecutionContext, rows: list[dict[str, Any]], runtime: TaskRuntime) -> tuple[list[dict[str, Any]], list[ProblemRecord]]:
        raw_rules = ctx.model_extra.get("cleaningRules", []) if ctx.model_extra else []
        rules = [CleaningRule.model_validate(rule) for rule in raw_rules] if raw_rules else []
        return clean_rows(rows, rules)

    async def map_fields(self, ctx: ExecutionContext, rows: list[dict[str, Any]], runtime: TaskRuntime) -> tuple[list[dict[str, Any]], list[ProblemRecord]]:
        return normalize_rows(rows, ctx.columns, target_layer="physical")

    async def before_write(self, ctx: ExecutionContext, runtime: TaskRuntime) -> None:
        pass

    async def write(self, ctx: ExecutionContext, rows: list[dict[str, Any]], runtime: TaskRuntime) -> int:
        return await write_rows(ctx.storage_mapping, ctx.columns, rows)

    async def after_write(self, ctx: ExecutionContext, runtime: TaskRuntime) -> None:
        pass

    async def after_success(self, ctx: ExecutionContext, runtime: TaskRuntime) -> None:
        pass

    async def after_failed(self, ctx: ExecutionContext, runtime: TaskRuntime, exc: Exception) -> None:
        pass

    def build_success_result(self, ctx: ExecutionContext, runtime: TaskRuntime) -> TaskRunResult:
        return TaskRunResult(
            run_id=runtime.run_id,
            status="SUCCESS",
            success_count=runtime.success_count,
            total_count=runtime.collected_count,
            failure_count=runtime.exception_count,
            result_location=ResultLocation(
                physical_schema_name=ctx.storage_mapping.physical_schema_name,
                physical_table_name=ctx.storage_mapping.physical_table_name,
                run_id=runtime.run_id,
            ) if self.enable_write else None,
            summary_content=runtime.to_summary(),
            logs=runtime.logs,
            problems=runtime.problems,
            exceptions=None,
        )

    def build_failed_result(self, ctx: ExecutionContext, runtime: TaskRuntime, exc: Exception) -> TaskRunResult:
        logger.info(runtime.logs)
        return TaskRunResult(
            run_id=runtime.run_id,
            status="FAILED",
            success_count=runtime.success_count,
            total_count=runtime.collected_count,
            failure_count=runtime.exception_count or 1,
            result_location=None,
            summary_content=runtime.to_summary(),
            logs=runtime.logs,
            problems=runtime.problems,
            exceptions=[{"message": str(exc), "type": exc.__class__.__name__}],
        )
