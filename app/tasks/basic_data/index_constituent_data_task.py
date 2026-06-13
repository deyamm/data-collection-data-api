import logging
import datetime
from typing import Any, cast

from app.core.registry import registry
from app.schemas.collection_task.task_template import ExecutionContext, OutputField, TaskRunRequest, TaskRunResult, TaskTemplateInfo
from app.tasks.pipeline import BaseCollectTask
from app.core.providers import ts_provider

from app.utils.datetime_utils import get_first_day_of_month, get_last_day_of_month

logger = logging.getLogger(__name__)

class IndexConstituentDataTask(BaseCollectTask):
    """
    采集指数成分股数据，包括指数代码、成分股代码、权重等信息，该接口只能返回MSCI、中证、上交所、深交所、中金、申万及其他指数的成分股，同花顺、东财等版块、概念等指数需要其他接口。
    """

    def __init__(self):
        
        super().__init__()
        
        self.task_code = 'index_constituent_data'

        self.ts = ts_provider


    async def collect(self, params: dict[str, Any], ctx: ExecutionContext) -> list[dict[str, Any]]:
        # 读取参数，包括指数代码、开始日期、结束日期等参数，其中index_code必填，start_date和end_date可选，默认值为当月第一天和当月最后一天
        index_code = params.get("index_code", None)
        if index_code == None:
            raise ValueError("index_code参数不能为空")
        start_date = params.get("start_date", get_first_day_of_month(datetime.date.today()))
        end_date = params.get("end_date", get_last_day_of_month(datetime.date.today()))
        
        # 返回指数代码、成分股代码、交易日期、权重
        index_constituent = await self.ts.index_weight(index_code=index_code, start_date=start_date, end_date=end_date)

        return cast(list[dict[str, Any]], index_constituent.rename(columns=str).to_dict("records"))


async def index_constituent_data_handler(request: TaskRunRequest) -> TaskRunResult:
    """采集任务的handler，负责调用task的execute方法并返回结果"""
    task = IndexConstituentDataTask()
    
    return await task.execute(request)


def register_index_constituent_data_task():
    """注册task和handler到registry中"""
    registry.register_handler('index_constituent_data_handler', index_constituent_data_handler)

    registry.register_task_template(
        TaskTemplateInfo(
            task_code='index_constituent_data',
            task_name='指数成分股数据采集',
            task_desc='采集特定指数的在某月的成分股信息，成分股为月度更新数据，包含指数代码、成分股代码、权重等信息',
            handler_name='index_constituent_data_handler',
            data_source='TUSHARE',
            asset_type='指数',
            biz_type='基本数据',
            params_schema=[
                OutputField(
                    field_code="index_code",
                    field_name="指数代码",
                    field_type="STRING",
                    required=True,
                    unique_key=True,
                    sort_no=1,
                    field_desc="指数代码，需要包括后缀，必填，来源于指数基本数据接口返回的index_code字段，如000300.SH、399001.SZ等"
                ),
                OutputField(
                    field_code="start_date",
                    field_name="开始日期",
                    field_type="DATE",
                    required=False,
                    unique_key=False,
                    sort_no=2,
                    field_desc="开始日期，一般为当月第一天，格式为YYYYMMDD，选填，默认为当月第一天"
                ),
                OutputField(
                    field_code="end_date",
                    field_name="结束日期",
                    field_type="DATE",
                    required=False,
                    unique_key=False,
                    sort_no=3,
                    field_desc="结束日期，一般为当月最后一天，格式为YYYYMMDD，选填，默认为当月最后一天"
                )
            ],
            output_fields = [
                OutputField(
                    field_code="index_code",
                    field_name="指数代码",
                    field_type="STRING",
                    required=True,
                    unique_key=False,
                    sort_no=1,
                    field_desc="指数代码全称，包含交易所后缀"
                ),
                OutputField(
                    field_code="constituent_code",
                    field_name="成分股代码",
                    field_type="STRING",
                    required=True,
                    unique_key=False,
                    sort_no=2,
                    field_desc="成分股代码全称，包含交易所后缀"
                ),
                OutputField(
                    field_code="trade_date",
                    field_name="交易日期",
                    field_type="DATE",
                    required=False,
                    unique_key=False,
                    sort_no=3,
                    field_desc="成分股对应的交易日期，格式为YYYYMMDD"
                ),
                OutputField(
                    field_code="weight",
                    field_name="权重",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=4,
                    field_desc="成分股的权重，单位为百分比，保留4位小数"
                )
            ]

                
        )
    )
