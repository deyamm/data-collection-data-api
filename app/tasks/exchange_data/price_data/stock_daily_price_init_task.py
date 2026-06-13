import logging
from pathlib import Path
import re
from typing import Any, AsyncIterator, List
import numpy as np
import pandas as pd

from app.schemas.collection_task.task_template import ExecutionContext, OutputField, TaskRunRequest, TaskRunResult, TaskTemplateInfo
from app.tasks.pipeline import BaseCollectTask
from app.core.config import settings
from app.core.registry import registry

logger = logging.getLogger(__name__)

class StockDailyPriceInitTask(BaseCollectTask):
    """
    从下载的国泰安csv文件初始化股票日线价格数据，目录命名格式为k-yyyymmdd-yyyymmdd，存放在static目录下
    由于数据量较大，该任务通过批量采集的方式进行处理。
        源文件列名：
        Stkcd [证券代码]，添加市场代码后缀，上海证券交易所6XXXXX为.SH，深圳证券交易所3XXXXX或0XXXXX为.SZ，北京证券交易所9XXXXX为.BJ
        Trddt [交易日期]
        Opnprc [日开盘价]
        Hiprc [日最高价]
        Loprc [日最低价]
        Clsprc [日收盘价]
        Dnshrtrd [日个股交易股数]
        Dnvaltrd [日个股交易金额]
        Dsmvosd [日个股流通市值]
        Dsmvtll [日个股总市值]
        Markettype [市场类型] 
        Trdsta [交易状态]
        PreClosePrice [昨收盘(交易所)]
        ChangeRatio [涨跌幅]
        chg_amt [涨跌额] - 新加，等于日收盘价-昨收盘
    """

    def __init__(self):
        
        super().__init__()
        
        self.task_code = 'stock_daily_price_init'
        self.dir_name_re = re.compile(r"^k-(\d{8})-(\d{8})$")


    async def collect_batches(self, params: dict[str, Any], ctx: ExecutionContext) -> AsyncIterator[list[dict[str, Any]]]:
        """
        批量从csv文件中读取股票日线价格数据。
        一次性读取
        """
        batch_size = params.get('batch_size', settings.batch_size)
        csv_files = self._scan_csv_files()

        if not csv_files:
            raise FileNotFoundError("未找到符合条件的csv文件，请检查static目录下是否存在k-yyyymmdd-yyyymmdd格式的目录，并且目录下是否有csv文件。")
        
        for csv_file in csv_files:
            for chunk in pd.read_csv(csv_file, dtype={'Stkcd': str}, chunksize=batch_size):
                # 在Stkcd列加上市场代码后缀
                # 上海证券交易所6XXXXX为.SH，深圳证券交易所3XXXXX或0XXXXX为.SZ，北京证券交易所9XXXXX为.BJ
                chunk['Stkcd'] = chunk['Stkcd'].apply(
                    lambda x: x + '.SH' if x.startswith('6') else (x + '.SZ' if x.startswith('0') or x.startswith('3') else (x + '.BJ' if x.startswith('9') else x))
                )
                # 计算涨跌额                
                chunk['chg_amt'] = chunk['Clsprc'] - chunk['PreClosePrice']
                # 将nan值转换为None
                chunk.replace(np.nan, None, inplace=True)
                yield chunk.to_dict(orient='records')
        
    
    def _scan_csv_files(self) -> List[Path]:
        """
        扫描 static 下所有 k-yyyymmdd-yyyymmdd 目录中的 csv 文件，并返回文件路径列表。
        """
        static_dir = settings.STATIC_DIR

        if not static_dir.exists():
            raise FileNotFoundError(f"Static 目录不存在: {static_dir}")
        
        csv_files: List[Path] = []
        for child in static_dir.iterdir():
            # 只处理目录，且目录名符合 k-yyyymmdd-yyyymmdd 格式
            if not child.is_dir():
                continue
            if not self.dir_name_re.match(child.name):
                continue
            # 扫描目录下的 csv 文件
            for file in child.glob("*.csv"):
                csv_files.append(file.resolve())
        return csv_files


async def stock_daily_price_init_handler(request: TaskRunRequest) -> TaskRunResult:
    """采集任务的handler，负责调用task的execute方法并返回结果"""
    task = StockDailyPriceInitTask()
    
    return await task.execute(request)


def register_stock_daily_price_init_task():
    """注册task和handler到registry中"""
    registry.register_handler('stock_daily_price_init_handler', stock_daily_price_init_handler)

    registry.register_task_template(
        TaskTemplateInfo(
            task_code='stock_daily_price_init',
            task_name='股票日线价格数据初始化',
            task_desc='从下载的国泰安csv文件初始化股票日线价格数据，目录命名格式为k-yyyymmdd-yyyymmdd，存放在static目录下。由于数据量较大，该任务通过批量采集的方式进行处理。',
            handler_name='stock_daily_price_init_handler',
            data_source='CSMAR',
            asset_type='股票',
            biz_type='日线价格',
            params_schema=[
                OutputField(
                    field_code="batch_size",
                    field_name="批量大小",
                    field_type="INTEGER",
                    required=False,
                    field_desc="每次采集入库的批量大小，默认为5000"
                )
            ],
            output_fields=[
                OutputField(
                    field_code="Stkcd",
                    field_name="股票代码全称",
                    field_type="STRING",
                    required=True,
                    unique_key=True,
                    sort_no=1,
                    field_desc="股票代码全称"
                ),
                OutputField(
                    field_code="Trddt",
                    field_name="交易日期",
                    field_type="DATE",
                    required=True,
                    unique_key=True,
                    sort_no=2,
                    field_desc="交易日期，以YYYY-MM-DD表示"
                ),
                OutputField(
                    field_code="Opnprc",
                    field_name="开盘价",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=3,
                    field_desc="开盘价，A股以人民币元计，上海B以美元计，深圳B以港币计"
                ),
                OutputField(
                    field_code="Hiprc",
                    field_name="最高价",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=4,
                    field_desc="最高价，A股以人民币元计，上海B以美元计，深圳B以港币计"
                ),
                OutputField(
                    field_code="Loprc",
                    field_name="最低价",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=5,
                    field_desc="最低价，A股以人民币元计，上海B以美元计，深圳B以港币计"
                ),
                OutputField(
                    field_code="Clsprc",
                    field_name="收盘价",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=6,
                    field_desc="收盘价，A股以人民币元计，上海B以美元计，深圳B以港币计"
                ),
                OutputField(
                    field_code="Dnshrtrd",
                    field_name="交易股数",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=7,
                    field_desc="交易股数，单位为股，0=没有交易量"
                ),
                OutputField(
                    field_code="Dnvaltrd",
                    field_name="交易金额",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=8,
                    field_desc="交易金额，A股以人民币元计，上海B以美元计，深圳B以港币计，0=没有交易量"
                ),                
                OutputField(
                    field_code="Dsmvosd",
                    field_name="流通市值",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=9,
                    field_desc="流通市值，计算公式为：个股的流通股数与收盘价的乘积，A股以人民币元计，上海B股以美元计，深圳B股以港币计，注意单位是千。（注：ABH同股，只计算A股总市值）"
                ),
                OutputField(
                    field_code="Dsmvtll",
                    field_name="总市值",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=10,
                    field_desc="总市值，计算公式为：个股的总股数与收盘价的乘积，A股以人民币元计，上海B股以美元计，深圳B股以港币计，注意单位是千。（注：ABH同股，只计算A股总市值） A股：该字段计算用到的总股数计算公式为：个股的总股数= Nshrttl（总股数）-Nshrb (B股流通股数)-Nshrh(H股流通股数)-Nshroft(其它境外流通股)； B股：总股数Nshrttl=Nshrb B股流通股数；"
                ),
                OutputField(
                    field_code="Markettype",
                    field_name="市场类型",
                    field_type="INTEGER",
                    required=False,
                    unique_key=False,
                    sort_no=11,
                    field_desc="市场类型，1=上证A股市场 (不包含科创板），2=上证B股市场，4=深证A股市场（不包含创业板），8=深证B股市场，16=创业板， 32=科创板，64=北证A股市场。"
                ),
                OutputField(
                    field_code="Trdsta",
                    field_name="交易状态",
                    field_type="INTEGER",
                    required=False,
                    unique_key=False,
                    sort_no=12,
                    field_desc="交易状态，1=正常交易，2=ST，3＝*ST，4＝S（2006年10月9日及之后股改未完成），5＝SST，6＝S*ST，7=G（2006年10月9日之前已完成股改），8=GST，9=G*ST，10=U（2006年10月9日之前股改未完成），11=UST，12=U*ST，13=N，14=NST，15=N*ST，16=PT"
                ),
                OutputField(
                    field_code="PreClosePrice",
                    field_name="昨收价",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=13,
                    field_desc="昨收价，交易所接收的昨收盘价格，即经过除权的昨收价格"
                ),
                OutputField(
                    field_code="ChangeRatio",
                    field_name="涨跌幅",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=14,
                    field_desc="涨跌幅，基于昨收盘(交易所)计算的涨跌幅，计算公式为：日收盘价/昨收盘(交易所)-1"
                ),
                OutputField(
                    field_code="chg_amt",
                    field_name="涨跌额",
                    field_type="DECIMAL",
                    required=False,
                    unique_key=False,
                    sort_no=15,
                    field_desc="涨跌额，基于昨收盘(交易所)计算的涨跌额"
                ),
            ]
        )
    )
