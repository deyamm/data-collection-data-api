
import logging
from typing import Any, cast

from app.core.registry import registry
from app.schemas.collection_task.task_template import ExecutionContext, OutputField, TaskRunRequest, TaskRunResult, TaskTemplateInfo
from app.tasks.pipeline import BaseCollectTask
from app.core.providers import ts_provider

logger = logging.getLogger(__name__)

class StockDailyPriceByCodeTask(BaseCollectTask):
    """
    根据传入的股票代码和开始日期、结束日期，采集指定股票指定时间范围的日线价格数据。
    """

    def __init__(self):
        
        super().__init__()
        
        self.task_code = 'stock_daily_price_by_code'

        self.ts = ts_provider


    async def collect(self, params: dict[str, Any], ctx: ExecutionContext) -> list[dict[str, Any]]:
        ts_code = params['ts_code']
        start_date = params['start_date']
        end_date = params['end_date']

        if not ts_code:
            raise ValueError("参数ts_code不能为空")

        all_stock_daily = await self.ts.stock_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        # 交易额单位为千元，转换为元
        all_stock_daily['turnover'] = all_stock_daily['turnover'] * 1000
        # 将交易量单位为手，转换为股
        all_stock_daily['volume'] = all_stock_daily['volume'] * 100
        return cast(list[dict[str, Any]], all_stock_daily.rename(columns=str).to_dict("records"))


async def stock_daily_price_by_code_handler(request: TaskRunRequest) -> TaskRunResult:
    """采集任务的handler，负责调用task的execute方法并返回结果"""
    task = StockDailyPriceByCodeTask()
    
    return await task.execute(request)


def register_stock_daily_price_by_code_task():
    """注册task和handler到registry中"""
    registry.register_handler('stock_daily_price_by_code_handler', stock_daily_price_by_code_handler)

    registry.register_task_template(
        TaskTemplateInfo(
            task_code='stock_daily_price_by_code',
            task_name='股票日线价格数据采集（按股票代码）',
            task_desc='根据指定股票代码和时间范围采集日线价格数据。',
            handler_name='stock_daily_price_by_code_handler',
            data_source='TUSHARE',
            asset_type='股票',
            biz_type='日线价格',
            params_schema=[
                OutputField(
                    field_code="ts_code",
                    field_name="股票代码",
                    field_type="STRING",
                    required=True,
                    field_desc="需要采集数据的股票代码，格式为xxxxxx.SZ或xxxxxx.SH，例如000001.SZ"
                ),
                OutputField(
                    field_code="start_date",
                    field_name="开始日期",
                    field_type="DATE",
                    required=False,
                    field_desc="采集数据的开始日期，格式为yyyymmdd，例如20240101；未设置时为单次最大可采集数量的开始日期（tushare中该接口最大单次采集数量为6000条）"
                ),
                OutputField(
                    field_code="end_date",
                    field_name="结束日期",
                    field_type="DATE",
                    required=False,
                    field_desc="采集数据的结束日期，格式为yyyymmdd，例如20240101；默认为当前日期"
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
