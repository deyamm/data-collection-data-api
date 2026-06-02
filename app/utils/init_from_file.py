import logging

import pandas as pd
import numpy as np
import sys
sys.path.append(str(sys.path[0] + '/..'))

from core.config import settings
from core.db import ExchangeDataSession, exchange_data_engine, ExchangeBase
from core.db import BasicDataSession, basic_data_engine, BasicBase
from models.basic_data.stock_info import StockInfoPO
from models.basic_data.index_info import IndexInfoPO
from models.exchange_data.adjust_factor import AdjustFactorPO
from models.exchange_data.stock_k_data import StockKDataPO
from utils.column_translation import translate_column_name

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def k_data_init2base_CSMAR(folder_name: str | None = None):
    """
    
    freq [频度] - 新加，1:daily, 2:weekly, 3:monthly

    :param folder_name: 指定初始化的目录，如果为空，则初始化所有以'k-'开关的目录
    :type folder_name: str
    :return:
    """
    # 读取路径，static路径下的目录
    columns_name = ['full_symbol', 'trade_date', 'open', 'high', 'low', 'close',
                    'volume', 'turnover', 'pre_close', 'chg_pct']
    # 如果表不存在，先创建表
    with exchange_data_engine.connect() as conn:
        if not exchange_data_engine.dialect.has_table(conn, StockKDataPO.__tablename__):
            # 创建单个表，从Base.metadata里面指定表进行创建
            ExchangeBase.metadata.tables[StockKDataPO.__tablename__].create(conn)
            logging.info("create table: " + StockKDataPO.__tablename__)
    # db sessioin
    db_session = ExchangeDataSession()
    for child in settings.STATIC_DIR.iterdir():
        # k线数据的目录
        if child.is_dir() and child.name.startswith('k-'):
            # 指定目录时，只读取指定目录下的文件
            if folder_name is not None and child.name != folder_name:
                continue
            logging.info("date range: " + child.name + " start...")
            for file in child.iterdir():
                if file.suffix == '.csv':
                    logging.info("file: " + file.name + " start...")
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
                    db_session.bulk_save_objects(obj_list)
                    db_session.commit()
                    logging.info("file: " + file.name + " end...")
    db_session.close()


def adjust_factor_init2base_CSMAR():
    """
    国泰安（SCMAR）复权因子初始化到数据库中
    后续更新使用akshare
    非累计与累计的区别：
      非累计为单次除权的因子，累计为最新交易日往前多次除权得到的
    TradingDate [交易日期] - 以YYYY-MM-DD表示。
    Symbol [证券代码] - null
    FwardFactor [前复权因子] - foreward_adj_factor
        计算公式为：复权当日的昨收盘价（交易所）/复权前一交易日收盘价
    BwardFactor [后复权因子] - backward_adj_factor
        计算公式为：复权前一交易日收盘价/复权当日的昨收盘价（交易所）
    CumulateFwardFactor [前累计复权因子] - acc_foreward_adj_factor
        计算公式为：发行至今的所有前复权因子相乘。
    CumulateBwardFactor [后累计复权因子] - acc_backward_adj_factor
        计算公式为：发行至今的所有后复权因子相乘。
    :return:
    """
    file_path = settings.STATIC_DIR.joinpath('adj-factor/TRD_AdjustFactor.csv')
    if not file_path.exists():
        logging.error("adj-factor init file not exists, file path: " + str(file_path))
    # 判断表是否存在，不存在则创建
    with exchange_data_engine.connect() as conn:
        if not exchange_data_engine.dialect.has_table(conn, AdjustFactorPO.__tablename__):
            ExchangeBase.metadata.tables[AdjustFactorPO.__tablename__].create(conn)
            logging.info("create table: " + AdjustFactorPO.__tablename__)
    db_session = ExchangeDataSession()
    logging.info("adj-factor init start...")
    df = pd.read_csv(file_path, dtype={'Symbol': str})
    # 修改列名
    df.columns = ['trade_date', 'symbol', 'forward_adj_factor', 'backward_adj_factor',
                  'acc_forward_adj_factor', 'acc_backward_adj_factor']
    # 转换为AdjustFactor objects
    obj_list = [AdjustFactorPO(**row) for row in df.to_dict(orient='records')] # type: ignore
    # 批量新增
    db_session.bulk_save_objects(obj_list)
    db_session.commit()
    logging.info("adj-factor init end...")
    db_session.close()


def stock_basic_init2base_tushare():
    """
    根据从tushare获取股票基本信息csv文件，并初始化到数据库中
    包含股票代码、股票名称、上市日期、退市日期、是否停牌等信息
    :return:
    """
    file_path = settings.STATIC_DIR.joinpath('tushare_stock_basic.csv')
    if not file_path.exists():
        logging.error("stock-basic init file not exists, file path: " + str(file_path))
    # 判断表是否存在，不存在则创建
    with basic_data_engine.connect() as conn:
        if not basic_data_engine.dialect.has_table(conn, StockInfoPO.__tablename__):
            BasicBase.metadata.tables[StockInfoPO.__tablename__].create(conn)
            logging.info("create table: " + StockInfoPO.__tablename__)
    db_session = BasicDataSession()
    logging.info("stock-basic init start...")
    df = pd.read_csv(file_path)
    # replace nan with None
    df = df.replace({np.nan: None})
    # 修改列名
    df.columns = translate_column_name(df.columns.tolist(), api_source='ts')
    # 转换为StockInfo objects
    obj_list = [StockInfoPO(**row) for row in df.to_dict(orient='records')] # type: ignore
    # 批量新增
    db_session.bulk_save_objects(obj_list)
    db_session.commit()
    logging.info("stock-basic init end...")
    db_session.close()


def index_basic_init2base_tushare():
    """
    根据从tushare获取指数基本信息csv文件，并初始化到数据库中
    包含指数代码、指数名称、市场、发布方、指数风格、指数类别、基期、基点、发布日期、加权方式、描述等信息
     :return:
    """
    file_path = settings.STATIC_DIR.joinpath('tushare_index_basic.csv')
    if not file_path.exists():
        logging.error("index-basic init file not exists, file path: " + str(file_path))
    # 判断表是否存在，不存在则创建
    with basic_data_engine.connect() as conn:
        if not basic_data_engine.dialect.has_table(conn, IndexInfoPO.__tablename__):
            BasicBase.metadata.tables[IndexInfoPO.__tablename__].create(conn)
            logging.info("create table: " + IndexInfoPO.__tablename__)
    db_session = BasicDataSession()
    logging.info("index-basic init start...")
    df = pd.read_csv(file_path)
    # replace nan with None
    df = df.replace({np.nan: None})
    # 修改列名
    df.columns = translate_column_name(df.columns.tolist(), api_source='ts')
    # 转换为IndexInfo objects
    obj_list = [IndexInfoPO(**row) for row in df.to_dict(orient='records')] # type: ignore
    # 批量新增
    db_session.bulk_save_objects(obj_list)
    db_session.commit()
    logging.info("index-basic init end...")
    db_session.close()


if __name__ == '__main__':
    # adjust_factor_init2base_CSMAR()
    k_data_init2base_CSMAR('k-20260303-20260403')
