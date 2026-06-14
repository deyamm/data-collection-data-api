import asyncio
import logging
from typing import Any, AsyncIterator, cast

from app.core.registry import registry
from app.schemas.collection_task.task_template import ExecutionContext, OutputField, TaskRunRequest, TaskRunResult, TaskTemplateInfo
from app.tasks.pipeline import BaseCollectTask
from app.core.providers import ts_provider

logger = logging.getLogger(__name__)

class StockAdjustFactorInitTask(BaseCollectTask):
    """
    初始化采集所有股票历史复权因子数据，包括股票代码、交易日期、复权因子等信息。
    该接口可以用于初始化场景：
        1）先获取股票列表；
        2）再逐只股票获取其全部历史复权因子数据；
        3）每只股票的复权因子数据作为一个批次yield出去，由基类自动进行后续标准化、清洗、字段映射和入库。
    """

    def __init__(self):

        super().__init__()

        self.task_code = 'stock_adjust_factor_init'

        self.ts = ts_provider


    async def collect_batches(self, params: dict[str, Any], ctx: ExecutionContext) -> AsyncIterator[list[dict[str, Any]]]:
        """
            初始化采集所有股票历史复权因子数据：
            1）从股票基本数据接口获取股票列表；
            2）遍历每一个股票代码ts_code，按ts_code读取该股票全部历史复权因子数据；
            3）每只股票的复权因子records作为一个批次yield出去；
            4）相邻两次读取复权因子之间暂停5秒。
        """

        # 先读取股票列表
        stock_basic = await self.ts.stock_basic()

        if stock_basic is None or stock_basic.empty:
            logger.info("未获取到股票列表数据")
            return

        ts_codes = stock_basic["ts_code"].dropna().tolist()
        total_count = len(ts_codes)
        logger.info(f"共获取到{total_count}只股票，开始逐只采集历史复权因子数据")

        for index, ts_code in enumerate(ts_codes):
            if index < 3810:  # 从第693只股票开始采集，前692只股票的复权因子数据已采集完成
                continue
            logger.info(f"开始采集第 {index + 1}/{total_count} 只股票 {ts_code} 的历史复权因子数据")

            # 只传入ts_code参数，获取该股票全部历史复权因子数据
            adj_factor = await self.ts.adj_factor(ts_code=ts_code)
            records = cast(list[dict[str, Any]], adj_factor.rename(columns=str).to_dict("records"))

            if len(records) > 0:
                yield records
            else:
                logger.info(f"股票 {ts_code} 未获取到历史复权因子数据")

            # 相邻读取复权因子之间暂停1秒，最后一只股票采集完成后不再暂停
            if index < total_count - 1:
                await asyncio.sleep(1)


async def stock_adjust_factor_init_handler(request: TaskRunRequest) -> TaskRunResult:
    """采集任务的handler，负责调用task的execute方法并返回结果"""
    task = StockAdjustFactorInitTask()

    return await task.execute(request)


def register_stock_adjust_factor_init_task():
    """注册task和handler到registry中"""
    registry.register_handler('stock_adjust_factor_init_handler', stock_adjust_factor_init_handler)

    registry.register_task_template(
        TaskTemplateInfo(
            task_code='stock_adjust_factor_init',
            task_name='股票复权因子初始化数据采集',
            task_desc="""初始化采集所有股票历史复权因子数据：
            1）先从股票基本数据接口获取股票列表；
            2）再逐只股票获取其全部历史复权因子数据；
            3）每只股票的复权因子数据作为一个批次yield出去，由基类自动进行后续标准化、清洗、字段映射和入库；
            4）相邻两次读取复权因子之间暂停1秒。""",
            handler_name='stock_adjust_factor_init_handler',
            data_source='TUSHARE',
            asset_type='股票',
            biz_type='复权因子',
            params_schema=[],
            output_fields=[
                OutputField(
                    field_code="ts_code",
                    field_name="股票代码全称",
                    field_type="STRING",
                    required=True,
                    unique_key=True,
                    sort_no=1,
                    field_desc="股票代码全称"
                ),
                OutputField(
                    field_code="trade_date",
                    field_name="交易日期",
                    field_type="DATE",
                    required=True,
                    unique_key=False,
                    sort_no=2,
                    field_desc="交易日期"
                ),
                OutputField(
                    field_code="adj_factor",
                    field_name="复权因子",
                    field_type="DECIMAL",
                    required=True,
                    unique_key=True,
                    sort_no=3,
                    field_desc="复权因子"
                )
            ]
        )
    )