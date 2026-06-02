import pandas as pd

from app.core.common.enum import PricePeriodType, PriceAdjustType
from app.utils.column_translation import translate_column_name
from app.core.providers import AkShareProvider, TuShareProvider


class IndexExchangeDataService:

    def __init__(self, ak_provider: AkShareProvider, ts_provider: TuShareProvider):
        self.ak = ak_provider
        self.ts = ts_provider

    def get_industry_history_price_em(self, symbol: str, period: PricePeriodType, start_date: str, end_date: str, adjust: PriceAdjustType) -> pd.DataFrame:
        """获取东方财富行业的历史数据
        接口：stock_board_industry_hist_em
        目标地址：https://quote.eastmoney.com/bk/90.BK1027.html
        接口地址：https://akshare.akfamily.xyz/data/stock/stock.html#id361

        Args:
            symbol (str): 行业代码
            period (PricePeriodType): 频度，可以为daily、weekly、monthly，默认为daily
            start_date (str): 开始日期，YYYYMMMDD
            end_date (str): 结束日期，YYYYMMDD
            adjust (PriceAdjustType): 复权标识

        Returns:
            pd.DataFrame: _description_
        """
        info = self.ak.stock_board_industry_hist_em(symbol=symbol, period=PricePeriodType.em_period_chg(period), start_date=start_date, end_date=end_date, adjust=adjust.value).sort_values('日期')
        # 统一列名
        info.columns = translate_column_name(info.columns.to_list())
        # 代码
        info['index_code'] = symbol
        # 设置前收价，第一天的为当天开盘价
        info['pre_close'] = info['close'].shift()
        info.loc[0, 'pre_close'] = info.loc[0, 'optn']
        # k线周期
        info['period'] = PricePeriodType.db_code(period)
        return info

    def get_industry_history_price_ths(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """同花顺行业历史数据

        Args:
            symbol (str): _description_
            start_date (str): _description_
            end_date (str): _description_

        Returns:
            pd.DataFrame: _description_
        """
        info = (self.ak.stock_board_industry_index_ths(symbol=symbol, start_date=start_date, end_date=end_date)
                .sort_values("日期"))
        info.columns = translate_column_name(info.columns.to_list())
        info['index_code'] = symbol
        info['pre_close'] = info['close'].shift()
        info.loc[0, 'pre_close'] = info.loc[0, 'open']
        info['amplitude'] = round((info['high'] - info['low']) / info['pre_close'] * 100, 2)
        info['chg_amt'] = info['close'] - info['pre_close']
        info['chg_pct'] = round((info['chg_amt'] / info['pre_close'] * 100), 2)
        info['period'] = PricePeriodType.db_code(PricePeriodType.DAILY)
        return info

    def get_concept_history_price_em(self, symbol: str, period: PricePeriodType, start_date: str, end_date: str, adjust: PriceAdjustType) -> pd.DataFrame:
        """东方财富概念历史数据

        Args:
            symbol (str): _description_
            period (PricePeriodType): _description_
            start_date (str): _description_
            end_date (str): _description_
            adjust (PriceAdjustType): _description_

        Returns:
            pd.DataFrame: _description_
        """
        info = (self.ak.stock_board_concept_hist_em(symbol=symbol, period=period.value,
                                               start_date=start_date, end_date=end_date, adjust=adjust.value)
                .sort_values('日期'))
        
        info.columns = translate_column_name(info.columns.to_list())
        info['index_code'] = symbol
        info['pre_close'] = info['close'].shift()
        info.loc[0, 'pre_close'] = info.loc[0, 'optn']
        info['period'] = PricePeriodType.db_code(period)
        return info

    def get_concept_history_price_ths(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:

        info = (self.ak.stock_board_concept_index_ths(symbol=symbol, start_date=start_date, end_date=end_date)
                .sort_values("日期"))
        
        info.columns = translate_column_name(info.columns.to_list())
        info['index_code'] = symbol
        info['pre_close'] = info['close'].shift()
        info.loc[0, 'pre_close'] = info.loc[0, 'open']
        info['amplitude'] = round((info['high'] - info['low']) / info['pre_close'] * 100, 2)
        info['chg_amt'] = info['close'] - info['pre_close']
        info['chg_pct'] = round((info['chg_amt'] / info['pre_close'] * 100), 2)
        info['period'] = PricePeriodType.db_code(PricePeriodType.DAILY)
        return info

    def get_index_history_price_csi(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:

        info = (self.ak.stock_zh_index_hist_csindex(symbol=symbol, start_date=start_date, end_date=end_date)
                .sort_values('日期'))
        hist = info[['日期', '指数代码', '开盘', '最高', '最低', '收盘', '涨跌', '涨跌幅', '成交量', '成交金额']]

        hist.columns = translate_column_name(hist.columns.to_list())
        hist['index_code'] = symbol
        hist['pre_close'] = hist['close'].shift()
        hist.loc[0, 'pre_close'] = hist.loc[0, 'open']
        hist['amplitude'] = round((hist['high'] - hist['low']) / hist['pre_close'] * 100, 2)
        hist['period'] = PricePeriodType.db_code(PricePeriodType.DAILY)
        return hist

    def get_index_history_price_cni(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:

        info = self.ak.index_hist_cni(symbol=symbol, start_date=start_date, end_date=end_date)
        
        info.columns = translate_column_name(info.columns.to_list())
        info['index_code'] = symbol
        info['pre_close'] = info['close'].shift()
        info.loc[0, 'pre_close'] = info.loc[0, 'open']
        info['amplitude'] = round((info['high'] - info['low']) / info['pre_close'] * 100, 2)
        info['chg_amt'] = info['close'] - info['pre_close']
        info['period'] = PricePeriodType.db_code(PricePeriodType.DAILY)
        return info
    
    def get_index_daily_ts(self, full_symbol: str = '', trade_date: str = '', start_date: str = '', end_date: str = '') -> pd.DataFrame:
        """获取Tushare指数日线行情"""
        df = self.ts.index_daily(ts_code=full_symbol, trade_date=trade_date, start_date=start_date, end_date=end_date)
        # 转换列名，使用Tushare映射
        df.columns = translate_column_name(df.columns.to_list(), api_source='ts')
        return df
