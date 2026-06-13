
import logging
from typing import Any, cast

import numpy as np

from app.core.registry import registry
from app.schemas.collection_task.task_template import ExecutionContext, OutputField, TaskRunRequest, TaskRunResult, TaskTemplateInfo
from app.tasks.pipeline import BaseCollectTask
from app.core.providers import ts_provider

logger = logging.getLogger(__name__)

class StockBasicDataTask(BaseCollectTask):
    """
    采集股票基本数据，包括股票代码、名称、上市日期、退市日期、所属行业等信息。每次采集获取所有股票的基本数据，通过full_symbol来更新。
    """

    def __init__(self):
        
        super().__init__()
        
        self.task_code = 'stock_basic_data'

        self.ts = ts_provider


    async def collect(self, params: dict[str, Any], ctx: ExecutionContext) -> list[dict[str, Any]]:

        stock_basic = await self.ts.stock_basic()

        stock_basic = stock_basic.replace([np.inf, -np.inf], np.nan)
        stock_basic = stock_basic.astype(object).where(stock_basic.notnull(), None)

        return cast(list[dict[str, Any]], stock_basic.rename(columns=str).to_dict("records"))


async def stock_basic_data_handler(request: TaskRunRequest) -> TaskRunResult:
    """采集任务的handler，负责调用task的execute方法并返回结果"""
    task = StockBasicDataTask()
    
    return await task.execute(request)


def register_stock_basic_data_task():
    """注册task和handler到registry中"""
    registry.register_handler('stock_basic_data_handler', stock_basic_data_handler)

    registry.register_task_template(
        TaskTemplateInfo(
            task_code='stock_basic_data',
            task_name='股票基本数据采集',
            task_desc='采集所有股票的基本信息。',
            handler_name='stock_basic_data_handler',
            data_source='TUSHARE',
            asset_type='股票',
            biz_type='基本数据',
            params_schema=[],
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
                    field_code="symbol",
                    field_name="股票代码",
                    field_type="STRING",
                    required=False,
                    unique_key=False,
                    sort_no=2,
                    field_desc="股票代码，不包含交易所后缀"
                ),
                OutputField(
                    field_code="name",
                    field_name="股票名称",
                    field_type="STRING",
                    required=False,
                    unique_key=False,
                    sort_no=3,
                    field_desc="股票名称"
                ),
                OutputField(
                    field_code="area",
                    field_name="地域",
                    field_type="STRING",
                    required=False,
                    unique_key=False,
                    sort_no=4,
                    field_desc="地域"
                ),
                OutputField(
                    field_code="industry",
                    field_name="所属行业",
                    field_type="STRING",
                    required=False,
                    unique_key=False,
                    sort_no=5,
                    field_desc="所属行业"
                ),
                OutputField(
                    field_code="fullname",
                    field_name="股票全称",
                    field_type="STRING",
                    required=False,
                    unique_key=False,
                    sort_no=6,
                    field_desc="股票全称"
                ),
                OutputField(
                    field_code="enname",
                    field_name="英文全称",
                    field_type="STRING",
                    required=False,
                    unique_key=False,
                    sort_no=7,
                    field_desc="英文全称"
                ),
                OutputField(
                    field_code="cnspell",
                    field_name="拼音缩写",
                    field_type="STRING",
                    required=False,
                    unique_key=False,
                    sort_no=8,
                    field_desc="拼音缩写"
                ),
                OutputField(
                    field_code="market",
                    field_name="市场类型",
                    field_type="STRING",
                    required=False,
                    unique_key=False,
                    sort_no=9,
                    field_desc="市场类型（主板/创业板/科创板/CDR）"
                ),
                OutputField(
                    field_code="exchange",
                    field_name="交易所代码",
                    field_type="STRING",
                    required=False,
                    unique_key=False,
                    sort_no=10,
                    field_desc="交易所代码"
                ),
                OutputField(
                    field_code="curr_type",
                    field_name="交易货币",
                    field_type="STRING",
                    required=False,
                    unique_key=False,
                    sort_no=11,
                    field_desc="交易货币"
                ),
                OutputField(
                    field_code="list_status",
                    field_name="上市状态",
                    field_type="STRING",
                    required=False,
                    unique_key=False,
                    sort_no=12,
                    field_desc="上市状态 L上市 D退市 G过会未交易 P暂停上市"
                ),
                OutputField(
                    field_code="list_date",
                    field_name="上市日期",
                    field_type="DATE",
                    required=False,
                    unique_key=False,
                    sort_no=13,
                    field_desc="上市日期"
                ),
                OutputField(
                    field_code="delist_date",
                    field_name="退市日期",
                    field_type="DATE",
                    required=False,
                    unique_key=False,
                    sort_no=14,
                    field_desc="退市日期"
                ),
                OutputField(
                    field_code="is_hs",
                    field_name="是否沪深港通标的",
                    field_type="STRING",
                    required=False,
                    unique_key=False,
                    sort_no=15,
                    field_desc="是否沪深港通标的，N否 H沪股通 S深股通"
                ),
                OutputField(
                    field_code="act_name",
                    field_name="实控人名称",
                    field_type="STRING",
                    required=False,
                    unique_key=False,
                    sort_no=16,
                    field_desc="实控人名称"
                ),
                OutputField(
                    field_code="act_ent_type",
                    field_name="实控人企业性质",
                    field_type="STRING",
                    required=False,
                    unique_key=False,
                    sort_no=17,
                    field_desc="实控人企业性质"
                ),
            ]
        )
    )
