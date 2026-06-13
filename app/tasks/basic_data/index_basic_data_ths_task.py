
import logging
from typing import Any, cast

import pandas as pd

from app.core.registry import registry
from app.schemas.collection_task.task_template import ExecutionContext, OutputField, TaskRunRequest, TaskRunResult, TaskTemplateInfo
from app.tasks.pipeline import BaseCollectTask
from app.core.providers import ak_provider

logger = logging.getLogger(__name__)

class IndexBasicDataTHSTask(BaseCollectTask):
    """
    采集同花顺的行业和概念指数基本数据，只能采集名称、代码，当前还无法获取同花顺具体的成分股。
    """

    def __init__(self):
        
        super().__init__()
        
        self.task_code = 'index_basic_data_ths'

        self.ak = ak_provider


    async def collect(self, params: dict[str, Any], ctx: ExecutionContext) -> list[dict[str, Any]]:
        # 同花顺行业指数，包含name和code两列，code是指数代码
        industry_list_ths = self.ak.stock_board_industry_name_ths()
        # 添加category: 行业指数，market: THS，publisher: 同花顺
        industry_list_ths['category'] = '行业指数'
        industry_list_ths['market'] = 'THS'
        industry_list_ths['publisher'] = '同花顺'

        # 同花顺概念指数，包含name和code两列，code是指数代码
        concept_list_ths = self.ak.stock_board_concept_name_ths()
        # 添加category: 概念指数，market: THS，publisher: 同花顺
        concept_list_ths['category'] = '概念指数'
        concept_list_ths['market'] = 'THS'
        concept_list_ths['publisher'] = '同花顺'

        # 合并两个DataFrame，包含的列有name、code、category、market、publisher
        combined_list = pd.concat([industry_list_ths, concept_list_ths], ignore_index=True)

        return cast(list[dict[str, Any]], combined_list.rename(columns=str).to_dict("records"))


async def index_basic_data_ths_handler(request: TaskRunRequest) -> TaskRunResult:
    """采集任务的handler，负责调用task的execute方法并返回结果"""
    task = IndexBasicDataTHSTask()
    
    return await task.execute(request)


def register_index_basic_data_ths_task():
    """注册task和handler到registry中"""
    registry.register_handler('index_basic_data_ths_handler', index_basic_data_ths_handler)

    registry.register_task_template(
        TaskTemplateInfo(
            task_code='index_basic_data_ths',
            task_name='同花顺行业概念基本信息采集',
            task_desc='采集同花顺的行业和概念指数基本数据，只能采集名称、代码。当前还无法获取同花顺具体的成分股。暂时不用',
            handler_name='index_basic_data_ths_handler',
            data_source='AKSHARE',
            asset_type='指数',
            biz_type='基本数据',
            params_schema=[],
            output_fields = [
                OutputField(
                    field_code="name",
                    field_name="指数简称",
                    field_type="STRING",
                    required=False,
                    unique_key=False,
                    sort_no=2,
                    field_desc="同花顺行业和概念简称"
                ),
                OutputField(
                    field_code="code",
                    field_name="指数代码",
                    field_type="STRING",
                    required=True,
                    unique_key=True,
                    sort_no=1,
                    field_desc="同花顺行业和概念代码，纯6位数字"
                ),
                OutputField(
                    field_code="market",
                    field_name="市场",
                    field_type="STRING",
                    required=False,
                    unique_key=False,
                    sort_no=4,
                    field_desc="市场，同花顺行业和概念的市场固定为THS"
                ),
                OutputField(
                    field_code="publisher",
                    field_name="发布方",
                    field_type="STRING",
                    required=False,
                    unique_key=False,
                    sort_no=5,
                    field_desc="发布方，同花顺行业和概念的发布方固定为同花顺"
                ),
                OutputField(
                    field_code="category",
                    field_name="指数类别",
                    field_type="STRING",
                    required=False,
                    unique_key=False,
                    sort_no=7,
                    field_desc="同花顺的行业或概念"
                )
            ]   
        )
    )
