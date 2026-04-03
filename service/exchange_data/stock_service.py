import akshare as ak
import pandas as pd
import datetime

from utils.column_translation import translate_column_name
from core.enum_params import PricePeriodType, PriceAdjustType
from core.providers import AkShareProvider, TuShareProvider


class StockExchangeDataService():

    def __init__(self, ak_provider: AkShareProvider, ts_provider: TuShareProvider):
        self.ak = ak_provider
        self.ts = ts_provider

    def get_current_snapshot(self) -> pd.DataFrame:
        snap_df = self.ak.current_snap_shot_df().drop(columns="序号")
        # 将原来的中文列名转换为英文列名
        snap_df.columns = translate_column_name(snap_df.columns.to_list())
        return snap_df

    def get_stock_history_price(self, symbol: str, period: PricePeriodType, start_date: str, end_date: str, adjust: PriceAdjustType) -> pd.DataFrame:
        history_df = self.ak.get_stock_history_price(symbol=symbol, period=period.value,
                                    start_date=start_date, end_date=end_date, adjust=adjust.value)
        # 转换列名
        history_df.columns = translate_column_name(history_df.columns.to_list())
        # k线周期
        history_df['period'] = PricePeriodType.db_code(period)
        return history_df
    
    def get_daily_stock_price(self, date : str) -> pd.DataFrame:
        # 验证日期格式
        datetime.datetime.strptime(date, "%Y%m%d")
        daily_price = self.ts.daily(trade_date=date)
        daily_price.columns = translate_column_name(daily_price.columns.to_list(), api_source='ts')
        # 
        daily_price['period'] = PricePeriodType.db_code(PricePeriodType.DAILY)
        # 将ts_code中的交易所标识去掉，保留6位数字的股票代码
        # 交易额单位为千元，转换为元
        daily_price['turnover'] = daily_price['turnover'] * 1000
        # 将交易量单位为手，转换为股
        daily_price['volume'] = daily_price['volume'] * 100
        return daily_price
    

