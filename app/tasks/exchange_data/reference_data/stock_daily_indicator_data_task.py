import logging
from typing import Any, cast

import numpy as np

from app.core.registry import registry
from app.schemas.collection_task.task_template import ExecutionContext, OutputField, TaskRunRequest, TaskRunResult, TaskTemplateInfo
from app.tasks.pipeline import BaseCollectTask
from app.core.providers import ts_provider

logger = logging.getLogger(__name__)

class StockDailyIndicatorDataTask(BaseCollectTask):
    """
    从tushare接口获取股票每日指标数据，包含股票代码、交易日期、收盘价、换手率、市盈率、市净率、总市值、流通市值等信息。
    该接口可以用于2种场景：
        1）定期（每日）采集指定交易日期所有股票的每日指标数据；
        2）一次性获取指定股票的历史每日指标数据。
    """

    def __init__(self):

        super().__init__()

        self.task_code = 'stock_daily_indicator_data'

        self.ts = ts_provider


    async def collect(self, params: dict[str, Any], ctx: ExecutionContext) -> list[dict[str, Any]]:
        '''
            采集股票每日指标，包含两种场景：
            1）传入交易日期，获取该交易日所有股票的每日指标数据，此时ts_code、start_date和end_date不需要传入；
            2）传入股票代码、开始日期和结束日期，获取指定股票在该日期范围内的每日指标数据，用于历史数据采集。如果没有传入开始和结束日期，则默认采集指定股票的所有历史每日指标数据（单次最多6000条）。
        '''

        trade_date = params.get("trade_date", None)
        if trade_date != None:
            stock_daily_indicator = await self.ts.stock_daily_indicator(trade_date=trade_date)
        else:
            ts_code = params.get("ts_code", None)
            if ts_code == None:
                raise ValueError("ts_code和trade_date参数不能同时为空")
            start_date = params.get("start_date", '')
            end_date = params.get("end_date", '')
            stock_daily_indicator = await self.ts.stock_daily_indicator(ts_code=ts_code, start_date=start_date, end_date=end_date)

        # 将股本单位由万股，转换为股
        for field in ['total_share', 'float_share', 'free_share']:
            stock_daily_indicator[field] = stock_daily_indicator[field] * 10000
        # 将市值单位由万元，转换为元
        for field in ['total_mv', 'circ_mv']:
            stock_daily_indicator[field] = stock_daily_indicator[field] * 10000
        
        stock_daily_indicator = stock_daily_indicator.replace([np.inf, -np.inf], np.nan)
        stock_daily_indicator = stock_daily_indicator.astype(object).where(stock_daily_indicator.notnull(), None)
        return cast(list[dict[str, Any]], stock_daily_indicator.rename(columns=str).to_dict("records"))


async def stock_daily_indicator_data_handler(request: TaskRunRequest) -> TaskRunResult:
    """采集任务的handler，负责调用task的execute方法并返回结果"""
    task = StockDailyIndicatorDataTask()

    return await task.execute(request)


def register_stock_daily_indicator_data_task():
    """注册task和handler到registry中"""
    registry.register_handler('stock_daily_indicator_data_handler', stock_daily_indicator_data_handler)

    registry.register_task_template(
        TaskTemplateInfo(
            task_code='stock_daily_indicator_data',
            task_name='股票每日指标数据采集',
            task_desc="""采集股票每日指标，包含两种场景：
            1）传入交易日期，获取该交易日所有股票的每日指标数据，此时ts_code、start_date和end_date不需要传入，如果传入了trade_date参数，ts_code、start_date和end_date将被忽略；
            2）传入股票代码、开始日期和结束日期，获取指定股票在该日期范围内的每日指标数据，用于历史数据采集。如果没有传入开始和结束日期，则默认采集指定股票的所有历史每日指标数据（单次最多6000条）""",
            handler_name='stock_daily_indicator_data_handler',
            data_source='TUSHARE',
            asset_type='股票',
            biz_type='每日指标',
            params_schema=[
                OutputField(
                    field_code="ts_code",
                    field_name="股票代码",
                    field_type="STRING",
                    required=False,
                    unique_key=False,
                    sort_no=1,
                    field_desc="股票代码，需要包括后缀，选填，如果没有传入trade_date参数，则该参数必填，来源于股票基本数据接口返回的ts_code字段，如000001.SZ、600000.SH等"
                ),
                OutputField(
                    field_code="trade_date",
                    field_name="交易日期",
                    field_type="DATE",
                    required=False,
                    unique_key=False,
                    sort_no=2,
                    field_desc="交易日期，格式为YYYYMMDD，选填，如果传入了trade_date参数，则ts_code、start_date和end_date不需要传入"
                ),
                OutputField(
                    field_code="start_date",
                    field_name="开始日期",
                    field_type="DATE",
                    required=False,
                    unique_key=False,
                    sort_no=3,
                    field_desc="开始日期，格式为YYYYMMDD，选填，如果没有传入start_date，则以end_date向前最多采集6000条数据"
                ),
                OutputField(
                    field_code="end_date",
                    field_name="结束日期",
                    field_type="DATE",
                    required=False,
                    unique_key=False,
                    sort_no=4,
                    field_desc="结束日期，格式为YYYYMMDD，选填，如果没有传入end_date，则以start_date向后最多采集6000条数据"
                )
            ],
            output_fields = [
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
                    field_desc="换手率（百分比）"
                ),
                OutputField(
                    field_code="turnover_rate_f",
                    field_name="换手率（自由流通股）",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=5,
                    field_desc="换手率（自由流通股，百分比）"
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
                    field_desc="市盈率（总市值/净利润，亏损的PE为空）"
                ),
                OutputField(
                    field_code="pe_ttm",
                    field_name="市盈率TTM",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=8,
                    field_desc="市盈率（TTM，亏损的PE为空）"
                ),
                OutputField(
                    field_code="pb",
                    field_name="市净率",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=9,
                    field_desc="市净率（总市值/净资产）"
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
                    field_desc="市销率（TTM）"
                ),
                OutputField(
                    field_code="dv_ratio",
                    field_name="股息率",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=12,
                    field_desc="股息率（百分比），除息日发生在去年期间的派现"
                ),
                OutputField(
                    field_code="dv_ttm",
                    field_name="股息率TTM",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=13,
                    field_desc="股息率（TTM，百分比），除息日在近12个月且分红报告期在12个月以内的派现"
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
                ),
            ]


        )
    )