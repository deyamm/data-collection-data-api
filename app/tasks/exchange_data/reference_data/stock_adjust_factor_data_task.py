import logging
from typing import Any, cast

from app.core.registry import registry
from app.schemas.collection_task.task_template import ExecutionContext, OutputField, TaskRunRequest, TaskRunResult, TaskTemplateInfo
from app.tasks.pipeline import BaseCollectTask
from app.core.providers import ts_provider

logger = logging.getLogger(__name__)

class StockAdjustFactorDataTask(BaseCollectTask):
    """
    从tushare接口获取股票复权因子数据，包含股票代码、交易日期、复权因子等信息。
    该接口可以用于2种场景：
        1）定期（每日）采集指定交易日期所有股票的复权因子数据；
        2）一次性获取指定股票的历史复权因子数据。
    """

    def __init__(self):

        super().__init__()

        self.task_code = 'stock_adjust_factor_data'

        self.ts = ts_provider


    async def collect(self, params: dict[str, Any], ctx: ExecutionContext) -> list[dict[str, Any]]:
        '''
            采集股票复权因子，包含两种场景：
            1）传入交易日期，获取该交易日所有股票的复权因子数据，此时ts_code、start_date和end_date不需要传入；
            2）传入股票代码、开始日期和结束日期，获取指定股票在该日期范围内的复权因子数据，用于历史数据采集。如果没有传入开始和结束日期，则默认采集指定股票的所有历史复权因子数据。
        '''

        trade_date = params.get("trade_date", None)
        if trade_date != None:
            stock_adj_factor = await self.ts.adj_factor(trade_date=trade_date)
        else:
            ts_code = params.get("ts_code", None)
            if ts_code == None:
                raise ValueError("ts_code和trade_date参数不能同时为空")
            start_date = params.get("start_date", '')
            end_date = params.get("end_date", '')
            stock_adj_factor = await self.ts.adj_factor(ts_code=ts_code, start_date=start_date, end_date=end_date)

        return cast(list[dict[str, Any]], stock_adj_factor.rename(columns=str).to_dict("records"))


async def stock_adjust_factor_data_handler(request: TaskRunRequest) -> TaskRunResult:
    """采集任务的handler，负责调用task的execute方法并返回结果"""
    task = StockAdjustFactorDataTask()

    return await task.execute(request)


def register_stock_adjust_factor_data_task():
    """注册task和handler到registry中"""
    registry.register_handler('stock_adjust_factor_data_handler', stock_adjust_factor_data_handler)

    registry.register_task_template(
        TaskTemplateInfo(
            task_code='stock_adjust_factor_data',
            task_name='股票复权因子数据采集',
            task_desc="""采集股票复权因子，包含两种场景：
            1）传入交易日期，获取该交易日所有股票的复权因子数据，此时ts_code、start_date和end_date不需要传入，如果传入了trade_date参数，ts_code、start_date和end_date将被忽略；
            2）传入股票代码、开始日期和结束日期，获取指定股票在该日期范围内的复权因子数据，用于历史数据采集。如果没有传入开始和结束日期，则默认采集指定股票的所有历史复权因子数据
            为了节省存储空间，将相同的复权因子合并，在后续的处理环节中再展开，合并规则如下：
            1）以stock_code和adj_factor作为唯一标识，对每天更新的交易日进行唯一键更新操作；
            2）这样，除权日复权因子发生变化，前一天的复权因子就为除权前的因子，除权日之后的复权因子则代表着最新的复权因子，这样在计算复权价格价格时，就可以根据交易日期和股票代码，找到对应的范围内的复权因子进行计算""",
            handler_name='stock_adjust_factor_data_handler',
            data_source='TUSHARE',
            asset_type='股票',
            biz_type='复权因子',
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
                    field_desc="开始日期，格式为YYYYMMDD，选填，如果没有传入start_date，则默认采集指定股票所有历史复权因子数据"
                ),
                OutputField(
                    field_code="end_date",
                    field_name="结束日期",
                    field_type="DATE",
                    required=False,
                    unique_key=False,
                    sort_no=4,
                    field_desc="结束日期，格式为YYYYMMDD，选填，如果没有传入end_date，则默认采集指定股票所有历史复权因子数据"
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
                    unique_key=False,
                    sort_no=2,
                    field_desc="交易日期"
                ),
                OutputField(
                    field_code="adj_factor",
                    field_name="复权因子",
                    field_type="DECIMAL",
                    required=True,
                    unique_key=True,
                    sort_no=3,
                    field_desc="复权因子"
                ),
            ]
        )
    )