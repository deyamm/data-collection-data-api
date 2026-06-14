import asyncio
import logging
from typing import Any, AsyncIterator, cast

import numpy as np

from app.core.registry import registry
from app.schemas.collection_task.task_template import ExecutionContext, OutputField, TaskRunRequest, TaskRunResult, TaskTemplateInfo
from app.tasks.pipeline import BaseCollectTask
from app.core.providers import ts_provider

logger = logging.getLogger(__name__)

class StockDailyMoneyflowInitTask(BaseCollectTask):
    """
    初始化采集股票资金流向数据，先获取股票列表，再逐个股票采集全部历史资金流向数据。
    """

    def __init__(self):

        super().__init__()

        self.task_code = 'stock_daily_moneyflow_init'

        self.ts = ts_provider


    async def collect_batches(self, params: dict[str, Any], ctx: ExecutionContext) -> AsyncIterator[list[dict[str, Any]]]:
        """
            批量初始化采集股票资金流向数据：
            1）从股票基本数据接口读取股票列表；
            2）对每个股票代码ts_code，采集该股票全部历史资金流向数据；
            3）每只股票的数据作为一批yield出去，由基类自动完成后续标准化、清洗、字段映射和入库；
            4）相邻两次读取资金流向之间暂停5秒。
        """

        stock_basic = await self.ts.stock_basic()
        ts_codes = stock_basic["ts_code"].dropna().unique().tolist()

        for index, ts_code in enumerate(ts_codes):
            logger.info(f"开始采集股票{ts_code}的历史资金流向数据")
            moneyflow = await self.ts.daily_moneyflow(ts_code=str(ts_code))

            # 成交量单位为手，转换为股
            for column in [
                "buy_sm_vol",
                "sell_sm_vol",
                "buy_md_vol",
                "sell_md_vol",
                "buy_lg_vol",
                "sell_lg_vol",
                "buy_elg_vol",
                "sell_elg_vol",
                "net_mf_vol",
            ]:
                if column in moneyflow.columns:
                    moneyflow[column] = moneyflow[column] * 100

            # 成交金额单位为万元，转换为元
            for column in [
                "buy_sm_amount",
                "sell_sm_amount",
                "buy_md_amount",
                "sell_md_amount",
                "buy_lg_amount",
                "sell_lg_amount",
                "buy_elg_amount",
                "sell_elg_amount",
                "net_mf_amount",
            ]:
                if column in moneyflow.columns:
                    moneyflow[column] = moneyflow[column] * 10000

            moneyflow = moneyflow.replace([np.inf, -np.inf], np.nan)
            moneyflow = moneyflow.astype(object).where(moneyflow.notnull(), None)

            records = cast(list[dict[str, Any]], moneyflow.rename(columns=str).to_dict("records"))
            if len(records) > 0:
                yield records
            else:
                logger.info(f"股票{ts_code}没有获取到历史资金流向数据")

            if index < len(ts_codes) - 1:
                await asyncio.sleep(1)


async def stock_daily_moneyflow_init_handler(request: TaskRunRequest) -> TaskRunResult:
    """采集任务的handler，负责调用task的execute方法并返回结果"""
    task = StockDailyMoneyflowInitTask()

    return await task.execute(request)


def register_stock_daily_moneyflow_init_task():
    """注册task和handler到registry中"""
    registry.register_handler('stock_daily_moneyflow_init_handler', stock_daily_moneyflow_init_handler)

    registry.register_task_template(
        TaskTemplateInfo(
            task_code='stock_daily_moneyflow_init',
            task_name='股票资金流向初始化采集',
            task_desc='初始化采集所有股票的历史资金流向数据。任务先从股票基本数据接口获取股票列表，再逐个股票采集全部历史资金流向数据，每只股票的数据作为一批进行后续处理和入库，相邻两次接口调用之间暂停5秒。',
            handler_name='stock_daily_moneyflow_init_handler',
            data_source='TUSHARE',
            asset_type='股票',
            biz_type='资金流向',
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
                )
            ]
        )
    )