import asyncio
import logging
from typing import Any, AsyncIterator, cast

import numpy as np

from app.core.registry import registry
from app.schemas.collection_task.task_template import ExecutionContext, OutputField, TaskRunRequest, TaskRunResult, TaskTemplateInfo
from app.tasks.pipeline import BaseCollectTask
from app.core.providers import ts_provider

logger = logging.getLogger(__name__)

class IndexDailyIndicatorInitDataTask(BaseCollectTask):
    """
    初始化采集大盘指数每日指标数据，根据传入的指数代码列表，逐个指数采集全部历史每日指标数据。
    """

    def __init__(self):

        super().__init__()

        self.task_code = 'index_daily_indicator_init'

        self.ts = ts_provider


    def parse_index_codes(self, params: dict[str, Any]) -> list[str]:
        """从参数中读取指数代码列表，支持列表或半角逗号分隔字符串"""
        index_codes = params.get("index_codes", None)
        if index_codes == None:
            raise ValueError("index_codes参数不能为空")

        if isinstance(index_codes, str):
            parsed_index_codes = [item.strip() for item in index_codes.split(",") if item.strip()]
        elif isinstance(index_codes, list):
            parsed_index_codes = [str(item).strip() for item in index_codes if str(item).strip()]
        else:
            raise ValueError("index_codes参数必须为指数代码列表或半角逗号分隔字符串")

        if len(parsed_index_codes) == 0:
            raise ValueError("index_codes参数不能为空")

        return parsed_index_codes


    async def collect_batches(self, params: dict[str, Any], ctx: ExecutionContext) -> AsyncIterator[list[dict[str, Any]]]:
        """
            批量初始化采集大盘指数每日指标数据：
            1）从参数index_codes中读取需要初始化的指数代码列表；
            2）对每个指数代码，采集该指数全部历史每日指标数据；
            3）每个指数的数据作为一批yield出去，由基类自动完成后续标准化、清洗、字段映射和入库；
            4）相邻两次读取指数每日指标之间暂停5秒。
        """

        index_codes = self.parse_index_codes(params)

        for index, index_code in enumerate(index_codes):
            logger.info(f"开始采集指数{index_code}的历史每日指标数据")
            index_daily_basic = await self.ts.index_daily_indicator(ts_code=index_code)

            # 总股本、流通股本、自由流通股本单位为万股，转换为股
            for column in ["total_share", "float_share", "free_share"]:
                if column in index_daily_basic.columns:
                    index_daily_basic[column] = index_daily_basic[column] * 10000

            # 总市值、流通市值单位为万元，转换为元
            for column in ["total_mv", "float_mv"]:
                if column in index_daily_basic.columns:
                    index_daily_basic[column] = index_daily_basic[column] * 10000
            
            index_daily_basic = index_daily_basic.replace([np.inf, -np.inf], np.nan)
            index_daily_basic = index_daily_basic.astype(object).where(index_daily_basic.notnull(), None)

            records = cast(list[dict[str, Any]], index_daily_basic.rename(columns=str).to_dict("records"))
            if len(records) > 0:
                yield records
            else:
                logger.info(f"指数{index_code}没有获取到历史每日指标数据")

            if index < len(index_codes) - 1:
                await asyncio.sleep(1)


async def index_daily_indicator_init_handler(request: TaskRunRequest) -> TaskRunResult:
    """采集任务的handler，负责调用task的execute方法并返回结果"""
    task = IndexDailyIndicatorInitDataTask()

    return await task.execute(request)


def register_index_daily_indicator_init_task():
    """注册task和handler到registry中"""
    registry.register_handler('index_daily_indicator_init_handler', index_daily_indicator_init_handler)

    registry.register_task_template(
        TaskTemplateInfo(
            task_code='index_daily_indicator_init',
            task_name='大盘指数每日指标初始化采集',
            task_desc='初始化采集指定指数列表的历史每日指标数据。任务从参数index_codes读取指数代码列表，支持列表或逗号分隔字符串，再逐个指数采集全部历史每日指标数据，每个指数的数据作为一批进行后续处理和入库，相邻两次接口调用之间暂停5秒。',
            handler_name='index_daily_indicator_init_handler',
            data_source='TUSHARE',
            asset_type='指数',
            biz_type='每日指标',
            params_schema=[
                OutputField(
                    field_code="index_codes",
                    field_name="指数代码列表",
                    field_type="STRING",
                    required=True,
                    unique_key=False,
                    sort_no=1,
                    field_desc="需要初始化的指数代码列表，需要包括后缀，支持列表或半角逗号分隔字符串，如000001.SH,399001.SZ等"
                )
            ],
            output_fields=[
                OutputField(
                    field_code="ts_code",
                    field_name="指数代码全称",
                    field_type="STRING",
                    required=True,
                    unique_key=True,
                    sort_no=1,
                    field_desc="指数代码全称"
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
                    field_code="total_mv",
                    field_name="当日总市值（元）",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=3,
                    field_desc="当日总市值，单位为元"
                ),
                OutputField(
                    field_code="float_mv",
                    field_name="当日流通市值（元）",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=4,
                    field_desc="当日流通市值，单位为元"
                ),
                OutputField(
                    field_code="total_share",
                    field_name="当日总股本（股）",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=5,
                    field_desc="当日总股本，单位为股"
                ),
                OutputField(
                    field_code="float_share",
                    field_name="当日流通股本（股）",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=6,
                    field_desc="当日流通股本，单位为股"
                ),
                OutputField(
                    field_code="free_share",
                    field_name="当日自由流通股本（股）",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=7,
                    field_desc="当日自由流通股本，单位为股"
                ),
                OutputField(
                    field_code="turnover_rate",
                    field_name="换手率",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=8,
                    field_desc="换手率"
                ),
                OutputField(
                    field_code="turnover_rate_f",
                    field_name="换手率（自由流通股本）",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=9,
                    field_desc="换手率（基于自由流通股本）"
                ),
                OutputField(
                    field_code="pe",
                    field_name="市盈率",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=10,
                    field_desc="市盈率"
                ),
                OutputField(
                    field_code="pe_ttm",
                    field_name="市盈率TTM",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=11,
                    field_desc="市盈率TTM"
                ),
                OutputField(
                    field_code="pb",
                    field_name="市净率",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=12,
                    field_desc="市净率"
                )
            ]
        )
    )