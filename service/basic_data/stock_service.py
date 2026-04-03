import time
import pandas as pd
from core.enum_params import StockMarketType
from utils.column_translation import translate_column_name
from core.deps import AkShareProvider, TuShareProvider


class StockBasicDataService:

    def __init__(self, ak_provider: AkShareProvider, ts_provider: TuShareProvider):
        self.ak = ak_provider
        self.ts = ts_provider
    
    def get_stock_info_collection_ak(self) -> pd.DataFrame:
        """从akshare获取股票的基本信息，该部分信息长期不会变更
        股票列表：
            上证（主板A、主板B、科创）：stock_info_sh_name_code，[证券代码、证券简称、公司全称、上市日期]
            深证（A股、B股、CDR、AB股）：stock_info_sz_name_code，[板块、A股代码、A股简称、A股上市日期、A股总股本、A股流通股本、所属行业]
            北证：stock_info_bj_name_code，[证券代码、证券简称、总股本、流通股本、上市日期、所属行业、地区、报告日期]

        Returns:
            pd.DataFrame: _description_
        """
        
        # 上证A股，获取其证券代码、证券简称、公司全称、上市日期
        sh_a_info = self.ak.stock_info_sh_name_code(symbol="主板A股")
        sh_a_info.columns = translate_column_name(sh_a_info.columns.to_list())
        sh_a_info['mkt_type'] = StockMarketType.SSE_A
        time.sleep(5)
        # 科创板，获取其证券代码、证券简称、公司全称、上市日期
        sh_kc_info = self.ak.stock_info_sh_name_code(symbol="科创板")
        sh_kc_info.columns = translate_column_name(sh_kc_info.columns.to_list())
        sh_kc_info['mkt_type'] = StockMarketType.SSE_KC
        time.sleep(5)
        # 深证A股，获取其证券代码、简称、上市日期、交易所板块、所属行业
        sz_a_info = self.ak.stock_info_sz_name_code(symbol="A股列表")
        sz_a_info.columns = translate_column_name(sz_a_info.columns.to_list())
        sz_a_info.loc[sz_a_info['board'] == '主板', 'mkt_type'] = StockMarketType.SZSE_A
        sz_a_info.loc[sz_a_info['board'] == '创业板', 'mkt_type'] = StockMarketType.SZSE_CY
        # 总股本和流通股本中各数字带','，需要去掉
        sz_a_info['total_share'] = sz_a_info['total_share'].apply(lambda x: x.replace(',', ''))
        sz_a_info['float_share'] = sz_a_info['float_share'].apply(lambda x: x.replace(',', ''))
        time.sleep(5)
        # 北证，获取其证券代码、简称、上市日期、所属行业、地区
        bz_a_info = self.ak.stock_info_bj_name_code().drop(columns='报告日期')
        bz_a_info.columns = translate_column_name(bz_a_info.columns.to_list())
        bz_a_info['mkt_type'] = StockMarketType.BSE
        # 合并
        stock_info_df = pd.concat([sh_a_info, sh_kc_info, sz_a_info, bz_a_info], ignore_index=True)
        # 将上市日期的object从datetime转换为str
        stock_info_df['list_date'] = stock_info_df['list_date'].astype(str)
        return stock_info_df
    
    def get_stock_info_collection_ts(self, full_symbol: str = '', name: str = '', market: str = '', list_status: str = '', exchange: str = '', is_hs: str = '') -> pd.DataFrame:
        stock_infos = self.ts.stock_basic(ts_code=full_symbol, name=name, market=market, list_status=list_status, exchange=exchange, is_hs=is_hs)
        # 转换列名
        stock_infos.columns = translate_column_name(stock_infos.columns.to_list(), api_source='ts')
        return stock_infos