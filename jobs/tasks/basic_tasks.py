import json
import logging

from core.config import settings
from core.deps import get_stock_basic_data_service
from core.db import BasicDataBase
from models.basic_data.stock_info import StockInfoPO



def update_weekly_stock_info_job():
    """每周五收盘后更新股票基本信息并保存到数据库中
    """
    session = BasicDataBase.basic_data_session()
    service = get_stock_basic_data_service()

    stock_info_df = service.get_stock_info_collection_ts()
    session.delete(StockInfoPO)  # 删除原有数据
    logging.info("已清除原有的股票基本信息数据")
    # 将DataFrame转换为StockInfoPO对象列表
    for row in stock_info_df.to_dict(orient='records'):
        session.add(StockInfoPO(**row)) # type: ignore
    session.commit()
    logging.info(f"已将股票基本信息更新到数据库中，共{len(stock_info_df)}条记录")