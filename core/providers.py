import akshare as ak
import pandas as pd
from core.config import settings

from core.enum_params import PricePeriodType, PriceAdjustType


class AkShareProvider:

    # ------------------------------exchange_data/stock_data---------------------------------
    def current_snap_shot_df(self) -> pd.DataFrame:
        """东方财富网当前沪深京A股上市公司的实时行情
        ** 接口可用性较差，容易被东财禁用 **
        
        分类：exchange_data/stock_data
        
        接口：stock_zh_a_spot_em
        地址：https://akshare.akfamily.xyz/data/stock/stock.html#id11
        目标地址：https://quote.eastmoney.com/center/gridlist.html#hs_a_board

        Returns:
            pd.DataFrame: _description_
        """
        return ak.stock_zh_a_spot_em()

    def get_stock_history_price(self, symbol: str, period: str, start_date: str, end_date: str, adjust: str) -> pd.DataFrame:
        """获取指定股票的历史行情数据

        分类：exchange_data/stock_data

        接口：stock_zh_a_hist
        地址：https://akshare.akfamily.xyz/data/stock/stock.html#id22
        目标地址：https://quote.eastmoney.com/concept/sh603777.html?from=classic(示例)

        Args:
            symbol (str): _description_
            period (str): _description_
            start_date (str): _description_
            end_date (str): _description_
            adjust (str): _description_

        Returns:
            pd.DataFrame: _description_
        """
        return ak.stock_zh_a_hist(
            symbol=symbol,
            period=period,
            start_date=start_date,
            end_date=end_date,
            adjust=adjust,
        )
    
    # ------------------------------basic_info/market_basic_info---------------------------------
    def stock_board_industry_name_em(self) -> pd.DataFrame:
        return ak.stock_board_industry_name_em()
    
    def stock_board_industry_cons_em(self, symbol: str) -> pd.DataFrame:
        return ak.stock_board_industry_cons_em(symbol=symbol)
    
    def stock_board_industry_name_ths(self) -> pd.DataFrame:
        return ak.stock_board_industry_name_ths()
    
    def stock_board_industry_summary_ths(self) -> pd.DataFrame:
        return ak.stock_board_industry_summary_ths()
    
    def stock_board_concept_name_em(self) -> pd.DataFrame:
        return ak.stock_board_concept_name_em()
    
    def stock_board_concept_cons_em(self, symbol: str) -> pd.DataFrame:
        return ak.stock_board_concept_cons_em(symbol=symbol)
    
    def stock_board_concept_name_ths(self) -> pd.DataFrame:
        return ak.stock_board_concept_name_ths()
    
    def index_stock_cons_csindex(self, symbol: str):
        return ak.index_stock_cons_csindex(symbol=symbol)
    
    def index_all_cni(self):
        return ak.index_all_cni()
    
    def index_csindex_all(self):
        return ak.index_csindex_all()
    
    def index_detail_cni(self, symbol: str):
        return ak.index_detail_cni(symbol=symbol)
    
    def index_stock_info(self):
        return ak.index_stock_info()
    
    def stock_info_sh_name_code(self, symbol: str):
        return ak.stock_info_sh_name_code(symbol=symbol)
    
    def stock_info_sz_name_code(self, symbol: str):
        return ak.stock_info_sz_name_code(symbol=symbol)
    
    def stock_info_bj_name_code(self):
        return ak.stock_info_bj_name_code()
    
    # ------------------------------exchange_data/index_data---------------------------------
    def stock_board_industry_hist_em(self, symbol: str, period: str, start_date: str, end_date: str, adjust: str) -> pd.DataFrame:
        return ak.stock_board_industry_hist_em(symbol=symbol, period=period, start_date=start_date, end_date=end_date, adjust=adjust)
    
    def stock_board_industry_index_ths(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        return ak.stock_board_industry_index_ths(symbol=symbol, start_date=start_date, end_date=end_date)

    def stock_board_concept_hist_em(self, symbol: str, period: str, start_date: str, end_date: str, adjust: str) -> pd.DataFrame:
        return ak.stock_board_concept_hist_em(symbol=symbol, period=period, start_date=start_date, end_date=end_date, adjust=adjust)

    def stock_board_concept_index_ths(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        return ak.stock_board_concept_index_ths(symbol=symbol, start_date=start_date, end_date=end_date)
    
    def stock_zh_index_hist_csindex(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        return ak.stock_zh_index_hist_csindex(symbol=symbol, start_date=start_date, end_date=end_date)
    
    def index_hist_cni(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        return ak.index_hist_cni(symbol=symbol, start_date=start_date, end_date=end_date)

    #---------------------------------exchange_data/reference_data--------------------------
    def stock_value_em(self, symbol: str) -> pd.DataFrame:
        return ak.stock_value_em(symbol=symbol)


class TuShareProvider:

    def daily(self, trade_date: str) -> pd.DataFrame:
        """个股每日行情数据"""
        return settings.TU_PRO.daily(trade_date=trade_date)
    
    def daily_basic(self, ts_code: str = '', trade_date: str = '', start_date: str = '', end_date: str = '') -> pd.DataFrame:
        """个股每日指标数据"""
        return settings.TU_PRO.daily_basic(ts_code=ts_code, trade_date=trade_date, start_date=start_date, end_date=end_date)
    
    def daily_moneyflow(self, ts_code: str = '', trade_date: str = '', start_date: str = '', end_date: str = '') -> pd.DataFrame:
        """个股资金流向"""
        return settings.TU_PRO.moneyflow(ts_code=ts_code, trade_date=trade_date, start_date=start_date, end_date=end_date)
    
    def stock_basic(self, ts_code: str = '', name: str = '', market: str = '', list_status: str = '', exchange: str = '', is_hs: str = '') -> pd.DataFrame:
        """股票基本信息"""
        return settings.TU_PRO.stock_basic(ts_code=ts_code, name=name, market=market, list_status=list_status, exchange=exchange, is_hs=is_hs)
    
    def index_basic(self, ts_code: str = '', name: str = '', market: str = '', publisher: str = '', category: str = '') -> pd.DataFrame:
        """指数基本信息"""
        return settings.TU_PRO.index_basic(ts_code=ts_code, name=name, market=market, publisher=publisher, category=category)
    
    def index_daily(self, ts_code: str = '', trade_date: str = '', start_date: str = '', end_date: str = '') -> pd.DataFrame:
        """指数日线行情"""
        return settings.TU_PRO.index_daily(ts_code=ts_code, trade_date=trade_date, start_date=start_date, end_date=end_date)