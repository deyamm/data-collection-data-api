import asyncio
import logging
from typing import Any, AsyncIterator, cast

import numpy as np

from app.core.registry import registry
from app.schemas.collection_task.task_template import ExecutionContext, OutputField, TaskRunRequest, TaskRunResult, TaskTemplateInfo
from app.tasks.pipeline import BaseCollectTask
from app.core.providers import ts_provider

logger = logging.getLogger(__name__)

class StockDailyIndicatorInitTask(BaseCollectTask):
    """
    初始化采集股票每日指标数据，先获取股票列表，再逐个股票采集全部历史每日指标数据。
    """

    def __init__(self):

        super().__init__()

        self.task_code = 'stock_daily_indicator_init'

        self.ts = ts_provider


    async def collect_batches(self, params: dict[str, Any], ctx: ExecutionContext) -> AsyncIterator[list[dict[str, Any]]]:
        """
            批量初始化采集股票每日指标数据：
            1）从股票基本数据接口读取股票列表；
            2）对每个股票代码ts_code，采集该股票全部历史每日指标数据；
            3）每只股票的数据作为一批yield出去，由基类自动完成后续标准化、清洗、字段映射和入库；
            4）相邻两次读取每日指标之间暂停5秒。
        """

        stock_basic = await self.ts.stock_basic()
        ts_codes = stock_basic["ts_code"].dropna().unique().tolist()

        for index, ts_code in enumerate(ts_codes):
            logger.info(f"开始采集股票{ts_code}的历史每日指标数据")
            daily_indicator = await self.ts.stock_daily_indicator(ts_code=str(ts_code))

            # 总股本、流通股本、自由流通股本单位为万股，转换为股
            for column in ["total_share", "float_share", "free_share"]:
                if column in daily_indicator.columns:
                    daily_indicator[column] = daily_indicator[column] * 10000

            # 总市值、流通市值单位为万元，转换为元
            for column in ["total_mv", "circ_mv"]:
                if column in daily_indicator.columns:
                    daily_indicator[column] = daily_indicator[column] * 10000
            
            daily_indicator = daily_indicator.replace([np.inf, -np.inf], np.nan)
            daily_indicator = daily_indicator.astype(object).where(daily_indicator.notnull(), None)

            records = cast(list[dict[str, Any]], daily_indicator.rename(columns=str).to_dict("records"))
            if len(records) > 0:
                yield records
            else:
                logger.info(f"股票{ts_code}没有获取到历史每日指标数据")

            if index < len(ts_codes) - 1:
                await asyncio.sleep(1)


async def stock_daily_indicator_init_handler(request: TaskRunRequest) -> TaskRunResult:
    """采集任务的handler，负责调用task的execute方法并返回结果"""
    task = StockDailyIndicatorInitTask()

    return await task.execute(request)


def register_stock_daily_indicator_init_task():
    """注册task和handler到registry中"""
    registry.register_handler('stock_daily_indicator_init_handler', stock_daily_indicator_init_handler)

    registry.register_task_template(
        TaskTemplateInfo(
            task_code='stock_daily_indicator_init',
            task_name='股票每日指标初始化采集',
            task_desc='初始化采集所有股票的历史每日指标数据。任务先从股票基本数据接口获取股票列表，再逐个股票采集全部历史每日指标数据，每只股票的数据作为一批进行后续处理和入库，相邻两次接口调用之间暂停5秒。',
            handler_name='stock_daily_indicator_init_handler',
            data_source='TUSHARE',
            asset_type='股票',
            biz_type='每日指标',
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
                    unique_key=True,
                    sort_no=2,
                    field_desc="交易日期"
                ),
                OutputField(
                    field_code="close",
                    field_name="当日收盘价",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=3,
                    field_desc="当日收盘价"
                ),
                OutputField(
                    field_code="turnover_rate",
                    field_name="换手率",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=4,
                    field_desc="换手率"
                ),
                OutputField(
                    field_code="turnover_rate_f",
                    field_name="换手率（自由流通股本）",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=5,
                    field_desc="换手率（基于自由流通股本）"
                ),
                OutputField(
                    field_code="volume_ratio",
                    field_name="量比",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=6,
                    field_desc="量比"
                ),
                OutputField(
                    field_code="pe",
                    field_name="市盈率",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=7,
                    field_desc="市盈率"
                ),
                OutputField(
                    field_code="pe_ttm",
                    field_name="市盈率TTM",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=8,
                    field_desc="市盈率TTM"
                ),
                OutputField(
                    field_code="pb",
                    field_name="市净率",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=9,
                    field_desc="市净率"
                ),
                OutputField(
                    field_code="ps",
                    field_name="市销率",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=10,
                    field_desc="市销率"
                ),
                OutputField(
                    field_code="ps_ttm",
                    field_name="市销率TTM",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=11,
                    field_desc="市销率TTM"
                ),
                OutputField(
                    field_code="dv_ratio",
                    field_name="股息率",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=12,
                    field_desc="股息率"
                ),
                OutputField(
                    field_code="dv_ttm",
                    field_name="股息率TTM",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=13,
                    field_desc="股息率TTM"
                ),
                OutputField(
                    field_code="total_share",
                    field_name="总股本（股）",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=14,
                    field_desc="总股本，单位为股"
                ),
                OutputField(
                    field_code="float_share",
                    field_name="流通股本（股）",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=15,
                    field_desc="流通股本，单位为股"
                ),
                OutputField(
                    field_code="free_share",
                    field_name="自由流通股本（股）",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=16,
                    field_desc="自由流通股本，单位为股"
                ),
                OutputField(
                    field_code="total_mv",
                    field_name="总市值（元）",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=17,
                    field_desc="总市值，单位为元"
                ),
                OutputField(
                    field_code="circ_mv",
                    field_name="流通市值（元）",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=18,
                    field_desc="流通市值，单位为元"
                )
            ]
        )
    )