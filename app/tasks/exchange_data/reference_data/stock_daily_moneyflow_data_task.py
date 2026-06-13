import logging
from typing import Any, cast

import numpy as np

from app.core.registry import registry
from app.schemas.collection_task.task_template import ExecutionContext, OutputField, TaskRunRequest, TaskRunResult, TaskTemplateInfo
from app.tasks.pipeline import BaseCollectTask
from app.core.providers import ts_provider

logger = logging.getLogger(__name__)

class StockDailyMoneyflowDataTask(BaseCollectTask):
    """
    从tushare接口获取个股资金流向数据，包含股票代码、交易日期、小单、中单、大单、特大单买卖量和买卖金额、净流入量、净流入金额等信息。
    该接口可以用于2种场景：
        1）定期（每日）采集指定交易日期所有股票的资金流向数据；
        2）一次性获取指定股票的历史资金流向数据。
    """

    def __init__(self):

        super().__init__()

        self.task_code = 'stock_daily_moneyflow_data'

        self.ts = ts_provider


    async def collect(self, params: dict[str, Any], ctx: ExecutionContext) -> list[dict[str, Any]]:
        '''
            采集个股资金流向，包含两种场景：
            1）传入交易日期，获取该交易日所有股票的资金流向数据，此时ts_code、start_date和end_date不需要传入；
            2）传入股票代码、开始日期和结束日期，获取指定股票在该日期范围内的资金流向数据，用于历史数据采集。如果没有传入开始和结束日期，则默认采集指定股票的所有历史资金流向数据（单次最多6000条）。
        '''

        trade_date = params.get("trade_date", None)
        if trade_date != None:
            stock_moneyflow = await self.ts.daily_moneyflow(trade_date=trade_date)
        else:
            ts_code = params.get("ts_code", None)
            if ts_code == None:
                raise ValueError("ts_code和trade_date参数不能同时为空")
            start_date = params.get("start_date", '')
            end_date = params.get("end_date", '')
            stock_moneyflow = await self.ts.daily_moneyflow(ts_code=ts_code, start_date=start_date, end_date=end_date)

        # 将成交量单位由手，转换为股
        for field in ['buy_sm_vol', 'sell_sm_vol', 'buy_md_vol', 'sell_md_vol', 'buy_lg_vol', 'sell_lg_vol', 'buy_elg_vol', 'sell_elg_vol', 'net_mf_vol']:
            stock_moneyflow[field] = stock_moneyflow[field] * 100
        # 将成交金额单位由万元，转换为元
        for field in ['buy_sm_amount', 'sell_sm_amount', 'buy_md_amount', 'sell_md_amount', 'buy_lg_amount', 'sell_lg_amount', 'buy_elg_amount', 'sell_elg_amount', 'net_mf_amount']:
            stock_moneyflow[field] = stock_moneyflow[field] * 10000
        
        stock_moneyflow = stock_moneyflow.replace([np.inf, -np.inf], np.nan)
        stock_moneyflow = stock_moneyflow.astype(object).where(stock_moneyflow.notnull(), None)

        return cast(list[dict[str, Any]], stock_moneyflow.rename(columns=str).to_dict("records"))


async def stock_daily_moneyflow_data_handler(request: TaskRunRequest) -> TaskRunResult:
    """采集任务的handler，负责调用task的execute方法并返回结果"""
    task = StockDailyMoneyflowDataTask()

    return await task.execute(request)


def register_stock_daily_moneyflow_data_task():
    """注册task和handler到registry中"""
    registry.register_handler('stock_daily_moneyflow_data_handler', stock_daily_moneyflow_data_handler)

    registry.register_task_template(
        TaskTemplateInfo(
            task_code='stock_daily_moneyflow_data',
            task_name='个股资金流向数据采集',
            task_desc="""采集个股资金流向，包含两种场景：
            1）传入交易日期，获取该交易日所有股票的资金流向数据，此时ts_code、start_date和end_date不需要传入，如果传入了trade_date参数，ts_code、start_date和end_date将被忽略；
            2）传入股票代码、开始日期和结束日期，获取指定股票在该日期范围内的资金流向数据，用于历史数据采集。如果没有传入开始和结束日期，则默认采集指定股票的所有历史资金流向数据（单次最多6000条）
            小单：5万以下 中单：5万～20万 大单：20万～100万 特大单：成交额>=100万 """,
            handler_name='stock_daily_moneyflow_data_handler',
            data_source='TUSHARE',
            asset_type='股票',
            biz_type='资金流向',
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
                    field_code="buy_sm_vol",
                    field_name="小单买入量（股）",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=3,
                    field_desc="小单买入量，单位为股"
                ),
                OutputField(
                    field_code="buy_sm_amount",
                    field_name="小单买入金额（元）",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=4,
                    field_desc="小单买入金额，单位为元"
                ),
                OutputField(
                    field_code="sell_sm_vol",
                    field_name="小单卖出量（股）",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=5,
                    field_desc="小单卖出量，单位为股"
                ),
                OutputField(
                    field_code="sell_sm_amount",
                    field_name="小单卖出金额（元）",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=6,
                    field_desc="小单卖出金额，单位为元"
                ),
                OutputField(
                    field_code="buy_md_vol",
                    field_name="中单买入量（股）",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=7,
                    field_desc="中单买入量，单位为股"
                ),
                OutputField(
                    field_code="buy_md_amount",
                    field_name="中单买入金额（元）",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=8,
                    field_desc="中单买入金额，单位为元"
                ),
                OutputField(
                    field_code="sell_md_vol",
                    field_name="中单卖出量（股）",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=9,
                    field_desc="中单卖出量，单位为股"
                ),
                OutputField(
                    field_code="sell_md_amount",
                    field_name="中单卖出金额（元）",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=10,
                    field_desc="中单卖出金额，单位为元"
                ),
                OutputField(
                    field_code="buy_lg_vol",
                    field_name="大单买入量（股）",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=11,
                    field_desc="大单买入量，单位为股"
                ),
                OutputField(
                    field_code="buy_lg_amount",
                    field_name="大单买入金额（元）",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=12,
                    field_desc="大单买入金额，单位为元"
                ),
                OutputField(
                    field_code="sell_lg_vol",
                    field_name="大单卖出量（股）",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=13,
                    field_desc="大单卖出量，单位为股"
                ),
                OutputField(
                    field_code="sell_lg_amount",
                    field_name="大单卖出金额（元）",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=14,
                    field_desc="大单卖出金额，单位为元"
                ),
                OutputField(
                    field_code="buy_elg_vol",
                    field_name="特大单买入量（股）",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=15,
                    field_desc="特大单买入量，单位为股"
                ),
                OutputField(
                    field_code="buy_elg_amount",
                    field_name="特大单买入金额（元）",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=16,
                    field_desc="特大单买入金额，单位为元"
                ),
                OutputField(
                    field_code="sell_elg_vol",
                    field_name="特大单卖出量（股）",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=17,
                    field_desc="特大单卖出量，单位为股"
                ),
                OutputField(
                    field_code="sell_elg_amount",
                    field_name="特大单卖出金额（元）",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=18,
                    field_desc="特大单卖出金额，单位为元"
                ),
                OutputField(
                    field_code="net_mf_vol",
                    field_name="净流入量（股）",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=19,
                    field_desc="净流入量，单位为股"
                ),
                OutputField(
                    field_code="net_mf_amount",
                    field_name="净流入额（元）",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=20,
                    field_desc="净流入额，单位为元"
                ),
            ]


        )
    )