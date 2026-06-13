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


# def adjust_factor_init2base_CSMAR():
#     """
#     国泰安（SCMAR）复权因子初始化到数据库中
#     后续更新使用akshare
#     非累计与累计的区别：
#       非累计为单次除权的因子，累计为最新交易日往前多次除权得到的
#     TradingDate [交易日期] - 以YYYY-MM-DD表示。
#     Symbol [证券代码] - null
#     FwardFactor [前复权因子] - foreward_adj_factor
#         计算公式为：复权当日的昨收盘价（交易所）/复权前一交易日收盘价
#     BwardFactor [后复权因子] - backward_adj_factor
#         计算公式为：复权前一交易日收盘价/复权当日的昨收盘价（交易所）
#     CumulateFwardFactor [前累计复权因子] - acc_foreward_adj_factor
#         计算公式为：发行至今的所有前复权因子相乘。
#     CumulateBwardFactor [后累计复权因子] - acc_backward_adj_factor
#         计算公式为：发行至今的所有后复权因子相乘。
#     :return:
#     """
#     file_path = settings.STATIC_DIR.joinpath('adj-factor/TRD_AdjustFactor.csv')
#     if not file_path.exists():
#         logging.error("adj-factor init file not exists, file path: " + str(file_path))
#     # 判断表是否存在，不存在则创建
#     with exchange_data_engine.connect() as conn:
#         if not exchange_data_engine.dialect.has_table(conn, AdjustFactorPO.__tablename__):
#             ExchangeBase.metadata.tables[AdjustFactorPO.__tablename__].create(conn)
#             logging.info("create table: " + AdjustFactorPO.__tablename__)
#     db_session = ExchangeDataSession()
#     logging.info("adj-factor init start...")
#     df = pd.read_csv(file_path, dtype={'Symbol': str})
#     # 修改列名
#     df.columns = ['trade_date', 'symbol', 'forward_adj_factor', 'backward_adj_factor',
#                   'acc_forward_adj_factor', 'acc_backward_adj_factor']
#     # 转换为AdjustFactor objects
#     obj_list = [AdjustFactorPO(**row) for row in df.to_dict(orient='records')] # type: ignore
#     # 批量新增
#     db_session.bulk_save_objects(obj_list)
#     db_session.commit()
#     logging.info("adj-factor init end...")
#     db_session.close()


# def index_basic_init2base_tushare():
#     """
#     根据从tushare获取指数基本信息csv文件，并初始化到数据库中
#     包含指数代码、指数名称、市场、发布方、指数风格、指数类别、基期、基点、发布日期、加权方式、描述等信息
#      :return:
#     """
#     file_path = settings.STATIC_DIR.joinpath('tushare_index_basic.csv')
#     if not file_path.exists():
#         logging.error("index-basic init file not exists, file path: " + str(file_path))
#     # 判断表是否存在，不存在则创建
#     with basic_data_engine.connect() as conn:
#         if not basic_data_engine.dialect.has_table(conn, IndexInfoPO.__tablename__):
#             BasicBase.metadata.tables[IndexInfoPO.__tablename__].create(conn)
#             logging.info("create table: " + IndexInfoPO.__tablename__)
#     db_session = BasicDataSession()
#     logging.info("index-basic init start...")
#     df = pd.read_csv(file_path)
#     # replace nan with None
#     df = df.replace({np.nan: None})
#     # 修改列名
#     df.columns = translate_column_name(df.columns.tolist(), api_source='ts')
#     # 转换为IndexInfo objects
#     obj_list = [IndexInfoPO(**row) for row in df.to_dict(orient='records')] # type: ignore
#     # 批量新增
#     db_session.bulk_save_objects(obj_list)
#     db_session.commit()
#     logging.info("index-basic init end...")
#     db_session.close()
