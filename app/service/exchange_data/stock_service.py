import pandas as pd
import datetime
import logging
import numpy as np

from app.utils.column_translation import translate_column_name
from app.core.common.enum import PricePeriodType, PriceAdjustType
from app.core.providers import AkShareProvider, TuShareProvider
from app.core.config import settings

logger = logging.getLogger(__name__)

class StockExchangeDataService():

    def __init__(self, ak_provider: AkShareProvider, ts_provider: TuShareProvider):
        self.ak = ak_provider
        self.ts = ts_provider
    
    def init_daily_stock_price(self):
        """
        初始化股票的每日价格数据，价格均为除权数据
        数据来源为从国泰安下载的csv文件，文件命名格式为k-yyyymmdd-yyyymmdd，存放在static目录下
        """
        # 读取路径，static路径下的目录
        columns_name = ['full_symbol', 'trade_date', 'open', 'high', 'low', 'close',
                        'volume', 'turnover', 'pre_close', 'chg_pct']
        # db sessioin
        for child in settings.STATIC_DIR.iterdir():
            # k线数据的目录
            if child.is_dir() and child.name.startswith('k-'):
                # 指定目录时，只读取指定目录下的文件
                logger.info("date range: " + child.name + " start...")
                for file in child.iterdir():
                    if file.suffix == '.csv':
                        logger.info("file: " + file.name + " start...")
                        df = pd.read_csv(file, dtype={'Stkcd': str})
                        # 删去交易状态、市场类型、流通市值、总市值等字段
                        df.drop(columns=['Trdsta', 'Markettype', 'Dsmvosd', 'Dsmvtll'], inplace=True)
                        # 转换列名
                        df.columns = columns_name
                        # 在full_symbol列加上市场代码后缀，上海证券交易所6XXXXX为.SH，深圳证券交易所3XXXXX或0XXXXX为.SZ，北京证券交易所9XXXXX为.BJ
                        df['full_symbol'] = df['full_symbol'].apply(lambda x: x + '.SH' if x.startswith('6') else (x + '.SZ' if x.startswith('0') or x.startswith('3') else (x + '.BJ' if x.startswith('9') else x)))
                        # 计算涨跌额
                        df['chg_amt'] = df['close'] - df['pre_close']
                        # 添加k线周期标识，1:daily，2:weekly，3:monthly
                        df['period'] = 1
                        # 将nan值转换为None
                        df.replace(np.nan, None, inplace=True)
                        # 转化成ORM object list
                        obj_list = [StockKDataPO(**row) for row in df.to_dict(orient='records')] # type: ignore
                        # 批量新增
                        logger.info("file: " + file.name + " end...")

    def get_daily_stock_price(self, date : str) -> pd.DataFrame:
        # 验证日期格式
        datetime.datetime.strptime(date, "%Y%m%d")
        daily_price = self.ts.daily(trade_date=date)
        daily_price.columns = translate_column_name(daily_price.columns.to_list(), api_source='ts')
        # 
        daily_price['period'] = PricePeriodType.db_code(PricePeriodType.DAILY)
        # 交易额单位为千元，转换为元
        daily_price['turnover'] = daily_price['turnover'] * 1000
        # 将交易量单位为手，转换为股
        daily_price['volume'] = daily_price['volume'] * 100
        return daily_price
    

