import akshare as ak
import pandas as pd
from datetime import datetime

from app.core.common.enum import IndexMarket, IndexCategory
from app.core.providers import AkShareProvider, TuShareProvider
from app.utils.column_translation import translate_column_name

class MarketBasicDataService:
    def __init__(self, ak_provider: AkShareProvider, ts_provider: TuShareProvider):
        self.ak = ak_provider
        self.ts = ts_provider

    def get_industry_info_em(self) -> pd.DataFrame:
        """获取东方财富当前所有的行业信息
        取akshare接口中的板块名称、代码、个股数量等基本信息

        接口：stock_board_industry_name_em
        目标地址：https://quote.eastmoney.com/center/boardlist.html#industry_board
        接口地址：https://akshare.akfamily.xyz/data/stock/stock.html#id358

        Returns:
            pd.DataFrame: _description_
        """
        # 获取所有行业的信息
        info = self.ak.stock_board_industry_name_em()
        # 计算每个行业的个股数量
        info['sample_count'] = info['上涨家数'] + info['下跌家数']
        # 取出名称、代码、个股数量属性
        basic_info = info[['板块名称', '板块代码', 'sample_count']].copy()
        basic_info.columns = ['index_name', 'index_code', 'sample_count']
        # 指数市场
        basic_info['market'] = IndexMarket.EM
        # 指数类别
        basic_info['category'] = IndexCategory.INDUSTRY
        return basic_info

    def get_industry_constituent_em(self, symbol: str) -> pd.DataFrame:
        """获取东方财富行业在当前时刻的成分股，该接口一次性返回行业中当前时刻所有股票的行情

        Args:
            symbol (str): 板块名称或板块代码，这里输入的行业限定为代码

        Returns:
            pd.DataFrame: _description_
        """
        info = self.ak.stock_board_industry_cons_em(symbol=symbol)
        # 获取指定列并修改列名
        basic_info = info[['代码', '名称']].copy()
        basic_info.columns = ['symbol', 'name']
        # 添加行业代码列
        basic_info['index_code'] = symbol
        # 指数市场
        basic_info['market'] = IndexMarket.EM
        # 添加指数类别
        basic_info['category'] = IndexCategory.INDUSTRY
        return basic_info

    def get_industry_info_ths(self) -> pd.DataFrame:
        """获取同花顺的行业名称及代码
        接口：stock_board_industry_name_ths
        获取同花顺行业一览表，即当前各行业的实时行情
        接口：stock_board_industry_summary_ths
        两个接口按照行业名称进行拼接，获取板块名称、代码、个股数量

        Returns:
            pd.DataFrame: _description_
        """
        # 获取所有行业的名称和代码
        info_code = self.ak.stock_board_industry_name_ths()
        info_code.columns = ["板块", "代码"]
        # 获取所有行业的一览表
        info_summary = self.ak.stock_board_industry_summary_ths()
        # 按照行业名称连接
        info = pd.merge(info_code, info_summary, how="left", on="板块")
        # 计算行业的个股数量
        info['sample_count'] = info['上涨家数'] + info['下跌家数']
        # 保留名称、代码、样本数量
        basic_info = info[['板块', '代码', 'sample_count']].copy()
        basic_info.columns = ['index_name', 'index_code', 'sample_count']
        # 指数市场
        basic_info['market'] = IndexMarket.THS
        # 设置指数类别
        basic_info['category'] = IndexCategory.INDUSTRY
        return basic_info

    def get_concept_info_em(self) -> pd.DataFrame:
        """获取东方财富当前所有的概念信息
        返回akshare接口中的概念名称、代码、个股数量
        接口：stock_board_concept_name_em
        目标地址：https://quote.eastmoney.com/center/boardlist.html#concept_board        
        接口地址：https://akshare.akfamily.xyz/data/stock/stock.html#id349

        Returns:
            pd.DataFrame: _description_
        """
        # 获取所有概念的信息
        info = self.ak.stock_board_concept_name_em()
        # 计算每个概念的个股数量
        info['sample_count'] = info['上涨家数'] + info['下跌家数']
        # 取出名称、代码、个股数量属性
        basic_info = info[['板块名称', '板块代码', 'sample_count']].copy()
        basic_info.columns = ['index_name', 'index_code', 'sample_count']
        # 概念指数市场
        basic_info['market'] = IndexMarket.EM
        # 设置指数类别
        basic_info['category'] = IndexCategory.CONCEPT
        return basic_info

    def get_concept_constituent_em(self, symbol: str) -> pd.DataFrame:
        """获取东方财富概念在当前时刻的成分股，该接口一次性返回概念在当前时刻所有股票的行情

        Args:
            symbol (str): 概念名称或概念代码，这里输入的概念限定为代码
        
        Returns:
            pd.DataFrame: _description_
        """
        info = self.ak.stock_board_concept_cons_em(symbol=symbol)
        # 获取指定列并修改列名
        basic_info = info[['代码', '名称']].copy()
        basic_info.columns = ['symbol', 'name']
        # 添加行业代码列
        basic_info['index_code'] = symbol
        # 添加指数市场
        basic_info['market'] = IndexMarket.EM
        # 设置指数类别
        basic_info['category'] = IndexCategory.CONCEPT
        return basic_info

    def get_concept_info_ths(self) -> pd.DataFrame:
        """获取同花顺的概念名称及代码
        接口：stock_board_industry_name_ths
        TODO: 同花顺概念个股数量

        Returns:
            pd.DataFrame: _description_
        """
        # 获取所有概念的名称和代码
        info_code = self.ak.stock_board_concept_name_ths()
        info_code.columns = ["板块", "代码"]
        # 指数市场
        info_code['market'] = IndexMarket.THS
        # 指数类别
        info_code['category'] = IndexCategory.CONCEPT
        return info_code

    def get_index_constituent_csi(self, symbol: str) -> pd.DataFrame:
        """获取中证指数的成分股
        接口：index_stock_cons_csindex
        目标地址：http://www.csindex.com.cn/zh-CN/indices/index-detail/000300

        Args:
            symbol (str): 指数代码，不包含市场标识

        Returns:
            pd.DataFrame: _description_
        """
        info = self.ak.index_stock_cons_csindex(symbol=symbol)
        # 获取指定列
        info_cons = info[['指数代码', '成分券代码', '成分券名称']].copy()
        # 修改列名
        info_cons.columns = ['index_code', 'symbol', 'name']
        # 添加指数市场
        info_cons['market'] = IndexMarket.CSI
        return info_cons

    def get_index_info_cni(self) -> pd.DataFrame:
        """获取国证指数的基本信息
        接口：index_all_cni
        目标地址：http://www.cnindex.com.cn/zh_indices/sese/index.html?act_menu=1&index_type=-1

        Returns:
            pd.DataFrame: _description_
        """
        return self.ak.index_all_cni()

    def get_index_csindex_all(self) -> pd.DataFrame:
        return self.ak.index_csindex_all()

    def get_index_constituent_cni(self, symbol: str, date: str | None = None) -> pd.DataFrame:
        """获取国证指数的成分股
        接口：index_detail_cni
        目标地址：http://www.cnindex.com.cn/module/index-detail.html?act_menu=1&indexCode=399001

        Args:
            symbol (str):  不包含市场标识的指数代码
            date (str | None, optional): 指定指数成分的年月，以‘YYYYMM’格式给出. Defaults to None.

        Returns:
            pd.DataFrame: _description_
        """
        if date is None:
            date = datetime.today().strftime('%Y%m')
        info = self.ak.index_detail_cni(symbol=symbol)
        # 获取指定列
        cons = info[['样本代码', '样本简称']].copy()
        # 修改列名
        cons.columns = ['symbol', 'name']
        # 添加指数代码与指数来源列
        cons['index_code'] = symbol
        cons['market'] = IndexMarket.CNI
        return cons

    def get_index_info_general(self) -> pd.DataFrame:
        """来自聚宽的指数列表，可能包含部分上交所指数、深交所指数、中证、国证指数，但没有标明
        具体来源还需要进一步分别，实际使用可以使用该接口中的指数

        Returns:
            pd.DataFrame: _description_
        """
        return self.ak.index_stock_info()
    
    def get_index_basic_info(self, full_symbol: str = '', name: str = '', market: str = '', publisher: str = '', category: str = '') -> pd.DataFrame:
        """获取指数基本信息"""
        df = self.ts.index_basic(ts_code=full_symbol, name=name, market=market, publisher=publisher, category=category)
        # Convert column names to match the schema
        df.columns = translate_column_name(df.columns.tolist(), api_source='ts')
        # 将标识符转换为大写
        df['full_symbol'] = df['full_symbol'].str.upper()
        # 将Tushare指数市场以及分类转换为统一的指数类型，如果在Enum中找不到对应的值，则默认为OTH
        df['market'] = df['market'].apply(lambda x: IndexMarket.search_value(x))
        # 将Tushare指数分类转换为统一的指数分类，如果在Enum中找不到对应的值，则默认为OTHER
        df['category'] = df['category'].apply(lambda x: IndexCategory.search_value(x))
        return df


