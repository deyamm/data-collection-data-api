import asyncio
import logging
from typing import Any, AsyncIterator, cast

from app.core.registry import registry
from app.schemas.collection_task.task_template import ExecutionContext, OutputField, TaskRunRequest, TaskRunResult, TaskTemplateInfo
from app.tasks.pipeline import BaseCollectTask
from app.core.providers import ts_provider

logger = logging.getLogger(__name__)

class IndexDailyPriceInitTask(BaseCollectTask):
    """
    批量初始化指数日线行情数据，包括指数代码、交易日期、开盘点位、最高点位、最低点位、收盘点位、成交量、成交金额等信息。
    该任务从传入参数中读取需要初始化的指数代码列表，然后逐个指数读取其历史日线行情数据。
    """

    def __init__(self):

        super().__init__()

        self.task_code = 'index_daily_price_init'

        self.ts = ts_provider


    async def collect_batches(self, params: dict[str, Any], ctx: ExecutionContext) -> AsyncIterator[list[dict[str, Any]]]:
        """
            批量初始化指数日线行情数据：
            1）从参数ts_codes读取需要初始化的指数代码列表，多个指数代码用英文逗号分隔；
            2）然后对每一个指数代码ts_code，读取该指数的历史日线行情数据；
            3）每个指数的日线行情数据作为一个批次yield出去，后续由基类自动执行标准化、清洗、字段映射和入库；
            4）相邻两次读取指数日线行情之间暂停5秒。
        """

        ts_codes = params.get("ts_codes", params.get("index_codes", None))
        if ts_codes == None or ts_codes == "":
            raise ValueError("ts_codes参数不能为空")

        if isinstance(ts_codes, str):
            ts_code_list = [item.strip() for item in ts_codes.split(",") if item.strip()]
        else:
            ts_code_list = list(ts_codes)

        if len(ts_code_list) == 0:
            raise ValueError("ts_codes参数不能为空")

        for index, ts_code in enumerate(ts_code_list):
            logger.info(f"开始采集指数日线行情初始化数据，ts_code={ts_code}")

            index_daily = await self.ts.index_daily(ts_code=ts_code)

            # 交易额单位为千元，转换为元
            if 'amount' in index_daily.columns:
                index_daily['amount'] = index_daily['amount'] * 1000

            # 交易量单位为手，转换为股
            if 'vol' in index_daily.columns:
                index_daily['vol'] = index_daily['vol'] * 100

            yield cast(list[dict[str, Any]], index_daily.rename(columns=str).to_dict("records"))

            if index < len(ts_code_list) - 1:
                await asyncio.sleep(5)


async def index_daily_price_init_handler(request: TaskRunRequest) -> TaskRunResult:
    """采集任务的handler，负责调用task的execute方法并返回结果"""
    task = IndexDailyPriceInitTask()

    return await task.execute(request)


def register_index_daily_price_init_task():
    """注册task和handler到registry中"""
    registry.register_handler('index_daily_price_init_handler', index_daily_price_init_handler)

    registry.register_task_template(
        TaskTemplateInfo(
            task_code='index_daily_price_init',
            task_name='指数日线行情初始化数据采集',
            task_desc='批量初始化采集指定指数列表的历史日线行情数据。从参数ts_codes读取需要初始化的指数代码列表，多个指数代码用英文逗号分隔，逐个指数代码读取历史日线行情数据，每个指数作为一个批次进入后续标准化、清洗、字段映射和入库流程，相邻两次接口调用之间暂停5秒。',
            handler_name='index_daily_price_init_handler',
            data_source='TUSHARE',
            asset_type='指数',
            biz_type='日线价格',
            params_schema=[
                OutputField(
                    field_code="ts_codes",
                    field_name="指数代码列表",
                    field_type="STRING",
                    required=True,
                    unique_key=False,
                    sort_no=1,
                    field_desc="需要初始化的指数代码列表，需要包括后缀，多个指数代码用英文逗号分隔，如000001.SH,399001.SZ等"
                )
            ],
            output_fields = [
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
                    field_name="收盘点位",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=3,
                    field_desc="收盘点位"
                ),
                OutputField(
                    field_code="open",
                    field_name="开盘点位",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=4,
                    field_desc="开盘点位"
                ),
                OutputField(
                    field_code="high",
                    field_name="最高点位",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=5,
                    field_desc="最高点位"
                ),
                OutputField(
                    field_code="low",
                    field_name="最低点位",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=6,
                    field_desc="最低点位"
                ),
                OutputField(
                    field_code="pre_close",
                    field_name="昨收点位",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=7,
                    field_desc="昨日收盘点位"
                ),
                OutputField(
                    field_code="change",
                    field_name="涨跌点",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=8,
                    field_desc="涨跌点"
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