
import logging
from typing import Any, cast

from app.core.registry import registry
from app.schemas.collection_task.task_template import ExecutionContext, OutputField, TaskRunRequest, TaskRunResult, TaskTemplateInfo
from app.tasks.pipeline import BaseCollectTask
from app.core.providers import ts_provider

logger = logging.getLogger(__name__)

class StockDailyPriceByDateTask(BaseCollectTask):
    """
    根据传入的日期，采集指定日期所有股票的日线价格数据。
    """

    def __init__(self):
        
        super().__init__()
        
        self.task_code = 'stock_daily_price_by_date'

        self.ts = ts_provider


    async def collect(self, params: dict[str, Any], ctx: ExecutionContext) -> list[dict[str, Any]]:
        trade_date = params['trade_date']
        if not trade_date:
            raise ValueError("参数trade_date不能为空，格式为yyyymmdd，例如20240101")

        all_stock_daily = await self.ts.daily(trade_date=trade_date)
        # 交易额单位为千元，转换为元
        all_stock_daily['amount'] = all_stock_daily['amount'] * 1000
        # 将交易量单位为手，转换为股
        all_stock_daily['vol'] = all_stock_daily['vol'] * 100
        return cast(list[dict[str, Any]], all_stock_daily.rename(columns=str).to_dict("records"))


async def stock_daily_price_by_date_handler(request: TaskRunRequest) -> TaskRunResult:
    """采集任务的handler，负责调用task的execute方法并返回结果"""
    task = StockDailyPriceByDateTask()
    
    return await task.execute(request)


def register_stock_daily_price_by_date_task():
    """注册task和handler到registry中"""
    registry.register_handler('stock_daily_price_by_date_handler', stock_daily_price_by_date_handler)

    registry.register_task_template(
        TaskTemplateInfo(
            task_code='stock_daily_price_by_date',
            task_name='股票日线价格数据采集（按日期）',
            task_desc='根据指定日期采集所有股票日线价格数据。',
            handler_name='stock_daily_price_by_date_handler',
            data_source='TUSHARE',
            asset_type='股票',
            biz_type='日线价格',
            params_schema=[
                OutputField(
                    field_code="trade_date",
                    field_name="交易日期",
                    field_type="DATE",
                    required=True,
                    field_desc="需要采集数据的交易日期，格式为yyyymmdd，例如20240101"
                )
            ],
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
                    field_code="open",
                    field_name="开盘价",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=3,
                    field_desc="开盘价"
                ),
                OutputField(
                    field_code="high",
                    field_name="最高价",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=4,
                    field_desc="最高价"
                ),
                OutputField(
                    field_code="low",
                    field_name="最低价",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=5,
                    field_desc="最低价"
                ),
                OutputField(
                    field_code="close",
                    field_name="收盘价",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=6,
                    field_desc="收盘价"
                ),
                OutputField(
                    field_code="pre_close",
                    field_name="昨收价",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=7,
                    field_desc="昨收价"
                ),
                OutputField(
                    field_code="change",
                    field_name="涨跌额",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=8,
                    field_desc="涨跌额"
                ),                
                OutputField(
                    field_code="pct_chg",
                    field_name="涨跌幅",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=9,
                    field_desc="涨跌幅（百分比）"
                ),
                OutputField(
                    field_code="vol",
                    field_name="成交量（股）",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=10,
                    field_desc="成交量，单位为股"
                ),
                OutputField(
                    field_code="amount",
                    field_name="成交金额（元）",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=11,
                    field_desc="成交金额，单位为元"
                )
            ]
        )
    )
    