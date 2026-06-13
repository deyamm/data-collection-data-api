import logging
from pathlib import Path
import re
from typing import Any, AsyncIterator, List, cast
import numpy as np
import pandas as pd

from app.schemas.collection_task.task_template import ExecutionContext, OutputField, TaskRunRequest, TaskRunResult, TaskTemplateInfo
from app.tasks.pipeline import BaseCollectTask
from app.core.registry import registry
from app.core.providers import ts_provider

logger = logging.getLogger(__name__)

class IndexDailyPriceTask(BaseCollectTask):
    """
    从tushare接口获取指定指数日线价格数据，包含指数代码、交易日期、开盘价、最高价、最低价、收盘价、成交量、成交金额等信息。
    该接口可以用于2种场景：
        1）定期（每日）采集指定指数的日线价格数据；
        2）一次性获取指定指数的历史日线价格数据。
    """

    def __init__(self):
        
        super().__init__()
        
        self.task_code = 'index_daily_price'

        self.ts = ts_provider

    async def collect(self, params: dict[str, Any], ctx: ExecutionContext) -> list[dict[str, Any]]:
        '''
            采集指定指数的日线价格，包含两种场景：
            1）传入交易日期，获取指定指数在该交易日的日线价格数据，此时start_date和end_date不需要传入；
            2）传入开始日期和结束日期，获取指定指数在该日期范围内的日线价格数据，用于历史数据采集。如果没有传入开始和结束日期，则默认采集指定指数的所有历史日线价格数据（最大8000条）。
        '''

        # 读取参数，指数代码必填
        index_code = params.get("index_code", None)
        if index_code == None:
            raise ValueError("index_code参数不能为空")
        
        trade_date = params.get("trade_date", None)
        if trade_date != None:
            index_daily = await self.ts.index_daily(ts_code=index_code, trade_date=trade_date)
        else:
            start_date = params.get("start_date", '')
            end_date = params.get("end_date", '')
            index_daily = await self.ts.index_daily(ts_code=index_code, start_date=start_date, end_date=end_date)
        
        # 交易额单位为千元，转换为元
        index_daily['amount'] = index_daily['amount'] * 1000
        # 将交易量单位为手，转换为股
        index_daily['vol'] = index_daily['vol'] * 100
        return cast(list[dict[str, Any]], index_daily.rename(columns=str).to_dict("records"))


async def index_daily_price_handler(request: TaskRunRequest) -> TaskRunResult:
    """采集任务的handler，负责调用task的execute方法并返回结果"""
    task = IndexDailyPriceTask()
    
    return await task.execute(request)


def register_index_daily_price_task():
    """注册task和handler到registry中"""
    registry.register_handler('index_daily_price_handler', index_daily_price_handler)

    registry.register_task_template(
        TaskTemplateInfo(
            task_code='index_daily_price',
            task_name='指数日线价格数据采集',
            task_desc="""采集指定指数的日线价格，包含两种场景：
            1）传入交易日期，获取指定指数在该交易日的日线价格数据，此时start_date和end_date不需要传入，如果传入了trade_date参数，start_date和end_date将被忽略；
            2）传入开始日期和结束日期，获取指定指数在该日期范围内的日线价格数据，用于历史数据采集。如果没有传入开始和结束日期，则默认采集指定指数的所有历史日线价格数据（最大8000条）""",
            handler_name='index_daily_price_handler',
            data_source='TUSHARE',
            asset_type='指数',
            biz_type='日线价格',
            params_schema=[
                OutputField(
                    field_code="ts_code",
                    field_name="指数代码",
                    field_type="STRING",
                    required=True,
                    unique_key=False,
                    sort_no=1,
                    field_desc="指数代码，需要包括后缀，必填，来源于指数基本数据接口返回的index_code字段，如000300.SH、399001.SZ等"
                ),
                OutputField(
                    field_code="trade_date",
                    field_name="交易日期",
                    field_type="DATE",
                    required=False,
                    unique_key=False,
                    sort_no=2,
                    field_desc="交易日期，格式为YYYYMMDD，选填，如果传入了trade_date参数，则start_date和end_date不需要传入"
                ),
                OutputField(
                    field_code="start_date",
                    field_name="开始日期",
                    field_type="DATE",
                    required=False,
                    unique_key=False,
                    sort_no=3,
                    field_desc="开始日期，一般为当月第一天，格式为YYYYMMDD，选填，如果没有传入start_date，则以end_date向前最多采集8000条数据"
                ),
                OutputField(
                    field_code="end_date",
                    field_name="结束日期",
                    field_type="DATE",
                    required=False,
                    unique_key=False,
                    sort_no=4,
                    field_desc="结束日期，一般为当月最后一天，格式为YYYYMMDD，选填，如果没有传入end_date，则以start_date向后最多采集8000条数据"
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
                    field_code="close",
                    field_name="收盘价",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=3,
                    field_desc="收盘价"
                ),
                OutputField(
                    field_code="open",
                    field_name="开盘价",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=4,
                    field_desc="开盘价"
                ),
                OutputField(
                    field_code="high",
                    field_name="最高价",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=5,
                    field_desc="最高价"
                ),
                OutputField(
                    field_code="low",
                    field_name="最低价",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=6,
                    field_desc="最低价"
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
