
import logging
from typing import Any, cast

import pandas as pd

from app.core.registry import registry
from app.schemas.collection_task.task_template import ExecutionContext, OutputField, TaskRunRequest, TaskRunResult, TaskTemplateInfo
from app.tasks.pipeline import BaseCollectTask
from app.core.providers import ak_provider

logger = logging.getLogger(__name__)

class IndexBasicDataEMTask(BaseCollectTask):
    """
    采集东方财富的行业和概念指数基本数据，只能采集名称、代码。
    当前接口超时，暂时不用
    """

    def __init__(self):
        
        super().__init__()
        
        self.task_code = 'index_basic_data_em'

        self.ak = ak_provider


    async def collect(self, params: dict[str, Any], ctx: ExecutionContext) -> list[dict[str, Any]]:
        # 东方财富行业指数，包含name和code两列，code是指数代码
        industry_list_em = self.ak.stock_board_industry_name_em()
        # 添加category: 行业指数，market: em，publisher: 东方财富
        industry_list_em['category'] = '行业指数'
        industry_list_em['market'] = 'EM'
        industry_list_em['publisher'] = '东方财富'

        # 东方财富概念指数，包含name和code两列，code是指数代码
        concept_list_em = self.ak.stock_board_concept_name_em()
        # 添加category: 概念指数，market: em，publisher: 东方财富
        concept_list_em['category'] = '概念指数'
        concept_list_em['market'] = 'EM'
        concept_list_em['publisher'] = '东方财富'

        # 合并两个DataFrame，包含的列有name、code、category、market、publisher
        combined_list = pd.concat([industry_list_em, concept_list_em], ignore_index=True)

        return cast(list[dict[str, Any]], combined_list.rename(columns=str).to_dict("records"))


async def index_basic_data_em_handler(request: TaskRunRequest) -> TaskRunResult:
    """采集任务的handler，负责调用task的execute方法并返回结果"""
    task = IndexBasicDataEMTask()
    
    return await task.execute(request)


def register_index_basic_data_em_task():
    """注册task和handler到registry中"""
    registry.register_handler('index_basic_data_em_handler', index_basic_data_em_handler)

    registry.register_task_template(
        TaskTemplateInfo(
            task_code='index_basic_data_em',
            task_name='东方财富行业概念基本信息采集',
            task_desc='采集东方财富的行业和概念指数基本数据，只能采集名称、代码。',
            handler_name='index_basic_data_em_handler',
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
                    field_desc="东方财富行业和概念简称"
                ),
                OutputField(
                    field_code="code",
                    field_name="指数代码",
                    field_type="STRING",
                    required=True,
                    unique_key=True,
                    sort_no=1,
                    field_desc="东方财富行业和概念代码，纯6位数字"
                ),
                OutputField(
                    field_code="market",
                    field_name="市场",
                    field_type="STRING",
                    required=False,
                    unique_key=False,
                    sort_no=4,
                    field_desc="市场，东方财富行业和概念的市场固定为EM"
                ),
                OutputField(
                    field_code="publisher",
                    field_name="发布方",
                    field_type="STRING",
                    required=False,
                    unique_key=False,
                    sort_no=5,
                    field_desc="发布方，东方财富行业和概念的发布方固定为东方财富"
                ),
                OutputField(
                    field_code="category",
                    field_name="指数类别",
                    field_type="STRING",
                    required=False,
                    unique_key=False,
                    sort_no=7,
                    field_desc="东方财富的行业或概念"
                )
            ]   
        )
    )
