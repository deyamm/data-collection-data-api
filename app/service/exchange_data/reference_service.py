import pandas as pd
from app.utils.column_translation import translate_column_name
from app.core.providers import AkShareProvider, TuShareProvider

class ReferenceExchangeDataService:

    def __init__(self, ak_provider: AkShareProvider, ts_provider: TuShareProvider):
        self.ak = ak_provider
        self.ts = ts_provider

    def get_stock_valuation_ak(self, symbol: str) -> pd.DataFrame:
        """akshare的个股的每日估值指标接口.

        Note: 东方财富只能获取近7年数据

        接口：stock_value_em
        接口地址：https://akshare.akfamily.xyz/data/stock/stock.html#id284
        目标地址：https://data.eastmoney.com/gzfx/detail/300766.html

        Args:
            symbol(str): Stock code without market identifier, 6 digits.
        Returns:
            pd.DataFrame: 
        """
        valuation_df = self.ak.stock_value_em(symbol=symbol)
        valuation_df.columns = translate_column_name(valuation_df.columns.to_list())
        return valuation_df
    
    def get_stock_daily_indictor_ts(self, full_symbol: str = '', trade_date: str = '', start_date: str = '', end_date: str = '') -> pd.DataFrame:
        """tushare的个股的每日指标接口.

        Args:
            full_symbol(str): 股票代码，需要包含市场标识
            trade_date(str): 交易日期，与股票代码二选一，优先股票代码查询， 8位数字格式，如20240628
            start_date(str): 开始日期，8位数字格式，如20200101
            end_date(str): 结束日期，8位数字格式，如20240628
        Returns:
            pd.DataFrame: 接口内容参考https://tushare.pro/document/2?doc_id=32
        """
        valuation_df = self.ts.daily_basic(ts_code=full_symbol, trade_date=trade_date, start_date=start_date, end_date=end_date)
        valuation_df.columns = translate_column_name(valuation_df.columns.to_list(), api_source='ts')
        return valuation_df
    
    def get_stock_daily_moneyflow(self, full_symbol: str = '', trade_date: str = '', start_date: str = '', end_date: str = '') -> pd.DataFrame:
        """tushare个股的每日资金流向数据

        Args:
            full_symbol (str, optional): _description_. Defaults to ''.
            trade_date (str, optional): _description_. Defaults to ''.
            start_date (str, optional): _description_. Defaults to ''.
            end_date (str, optional): _description_. Defaults to ''.
        """
        moneyflow_df = self.ts.daily_moneyflow(ts_code=full_symbol, trade_date=trade_date, start_date=start_date, end_date=end_date)
        moneyflow_df.columns = translate_column_name(moneyflow_df.columns.to_list(), api_source='ts')
        return moneyflow_df