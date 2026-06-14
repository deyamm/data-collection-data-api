
import asyncio
import logging
from typing import Any, cast

import numpy as np
import pandas as pd

from app.core.registry import registry
from app.schemas.collection_task.task_template import ExecutionContext, OutputField, TaskRunRequest, TaskRunResult, TaskTemplateInfo
from app.tasks.pipeline import BaseCollectTask
from app.core.providers import ts_provider

logger = logging.getLogger(__name__)

class IndexBasicDataTask(BaseCollectTask):
    """
    采集指数基本数据，包括指数代码、简称、全称、市场、发布方等信息，该接口只能返回MSCI、中证、上交所、深交所、中金、申万及其他指数，同花顺、东财等版块、概念等指数需要其他接口。
    由于接口一次最多返回8000条数据，因此需要按市场来分批采集，市场包括MSCI=MSCI指数，CSI=中证指数，SSE=上交所指数，SZSE=深交所指数，CICC=中金指数，SW=申万指数，OTH=其他指数。
    """

    def __init__(self):
        
        super().__init__()
        
        self.task_code = 'index_basic_data'

        self.ts = ts_provider


    async def collect(self, params: dict[str, Any], ctx: ExecutionContext) -> list[dict[str, Any]]:

        all_index_basic = []

        for market in ['MSCI', 'CSI', 'SSE', 'SZSE', 'CICC', 'SW', 'OTH']:
            logger.info(f"开始采集指数基本数据，市场={market}")
            index_basic = await self.ts.index_basic(market=market)
            all_index_basic.append(index_basic)
            await asyncio.sleep(10)  # 10S钟采集一次，避免接口限频
        
        all_index_basic = pd.concat(all_index_basic, ignore_index=True)
        all_index_basic = all_index_basic.replace([np.inf, -np.inf], np.nan)
        all_index_basic = all_index_basic.astype(object).where(all_index_basic.notnull(), None)

        return cast(list[dict[str, Any]], all_index_basic.rename(columns=str).to_dict("records"))


async def index_basic_data_handler(request: TaskRunRequest) -> TaskRunResult:
    """采集任务的handler，负责调用task的execute方法并返回结果"""
    task = IndexBasicDataTask()
    
    return await task.execute(request)


def register_index_basic_data_task():
    """注册task和handler到registry中"""
    registry.register_handler('index_basic_data_handler', index_basic_data_handler)

    registry.register_task_template(
        TaskTemplateInfo(
            task_code='index_basic_data',
            task_name='指数基本数据采集',
            task_desc='采集指数基本数据，包括指数代码、简称、全称、市场、发布方等信息，该接口只能返回MSCI、中证、上交所、深交所、中金、申万及其他指数，同花顺、东财等版块、概念等指数需要其他接口。由于接口一次最多返回8000条数据，因此需要按市场来分批采集，市场包括MSCI=MSCI指数，CSI=中证指数，SSE=上交所指数，SZSE=深交所指数，CICC=中金指数，SW=申万指数，OTH=其他指数',
            handler_name='index_basic_data_handler',
            data_source='TUSHARE',
            asset_type='指数',
            biz_type='基本数据',
            params_schema=[],
            output_fields = [
                OutputField(
                    field_code="ts_code",
                    field_name="代码全称",
                    field_type="STRING",
                    required=True,
                    unique_key=True,
                    sort_no=1,
                    field_desc="指数代码全称，包含交易所后缀"
                ),
                OutputField(
                    field_code="name",
                    field_name="简称",
                    field_type="STRING",
                    required=False,
                    unique_key=False,
                    sort_no=2,
                    field_desc="简称"
                ),
                OutputField(
                    field_code="fullname",
                    field_name="指数全称",
                    field_type="STRING",
                    required=False,
                    unique_key=False,
                    sort_no=3,
                    field_desc="指数全称"
                ),
                OutputField(
                    field_code="market",
                    field_name="市场",
                    field_type="STRING",
                    required=False,
                    unique_key=False,
                    sort_no=4,
                    field_desc="市场，MSCI=MSCI指数，CSI=中证指数，SSE=上交所指数，SZSE=深交所指数，CICC=中金指数，SW=申万指数，OTH=其他指数"
                ),
                OutputField(
                    field_code="publisher",
                    field_name="发布方",
                    field_type="STRING",
                    required=False,
                    unique_key=False,
                    sort_no=5,
                    field_desc="发布方"
                ),
                OutputField(
                    field_code="index_type",
                    field_name="指数风格",
                    field_type="STRING",
                    required=False,
                    unique_key=False,
                    sort_no=6,
                    field_desc="指数风格"
                ),
                OutputField(
                    field_code="category",
                    field_name="指数类别",
                    field_type="STRING",
                    required=False,
                    unique_key=False,
                    sort_no=7,
                    field_desc="指数类别，包含主题、指数、策略、风格、综合、成长、价值、有色、化工、能源、其他、外汇、基金、商品、债券等类别，其中行业指数又包括一级行业、二级行业、三级行业等类别"
                ),
                OutputField(
                    field_code="base_date",
                    field_name="基期",
                    field_type="DATE",
                    required=False,
                    unique_key=False,
                    sort_no=8,
                    field_desc="基期"
                ),
                OutputField(
                    field_code="base_point",
                    field_name="基点",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=9,
                    field_desc="基点"
                ),
                OutputField(
                    field_code="list_date",
                    field_name="发布日期",
                    field_type="DATE",
                    required=False,
                    unique_key=False,
                    sort_no=10,
                    field_desc="发布日期"
                ),
                OutputField(
                    field_code="weight_rule",
                    field_name="加权方式",
                    field_type="STRING",
                    required=False,
                    unique_key=False,
                    sort_no=11,
                    field_desc="加权方式"
                ),
                OutputField(
                    field_code="desc",
                    field_name="描述",
                    field_type="STRING",
                    required=False,
                    unique_key=False,
                    sort_no=12,
                    field_desc="描述"
                ),
                OutputField(
                    field_code="exp_date",
                    field_name="终止日期",
                    field_type="DATE",
                    required=False,
                    unique_key=False,
                    sort_no=13,
                    field_desc="终止日期"
                ),
            ]

                
        )
    )
