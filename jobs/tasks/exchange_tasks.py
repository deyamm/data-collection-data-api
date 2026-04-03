import datetime
import logging

from core.deps import get_stock_exchange_service
from core.deps import get_reference_exchange_service
from models.exchange_data.stock_k_data import StockKDataPO
from models.exchange_data.stock_indicator import StockIndicatorPO
from models.exchange_data.stock_moneyflow import StockMoneyflowPO
from core.db import ExchangeDataBase

def update_daily_stock_price_job():
    """
    将当天收盘后所有股票的历史价格数据更新到数据库中
    
    """
    exchange_session = ExchangeDataBase.exchange_data_session()
    service = get_stock_exchange_service()
    # 当天日期
    date = datetime.datetime.now().strftime('%Y%m%d')
    # 当天股票收盘价格
    history_df = service.get_daily_stock_price(date)
    add_count = 0
    # 将DataFrame转换为StockKDataPO对象列表
    for row in history_df.to_dict(orient='records'):
        stock_info = StockKDataPO(**row) # type: ignore
        # 检查是否存在相同股票代码和日期的记录
        obj = exchange_session.query(StockKDataPO).filter_by(full_symbol=stock_info.full_symbol, trade_date=stock_info.trade_date).first()
        if not obj:
            exchange_session.add(stock_info)
            add_count += 1
    exchange_session.commit()
    logging.info(f"已将当天股票价格数据更新到数据库中，共新增{add_count}条记录")

def update_daily_stock_indicator_job():
    """
    将当天收盘后所有股票的每日指标数据更新到数据库中
    
    """
    exchange_session = ExchangeDataBase.exchange_data_session()
    service = get_reference_exchange_service()
    # 当天日期
    date = datetime.datetime.now().strftime('%Y%m%d')
    # 当天股票每日指标数据
    indicator_df = service.get_stock_daily_indictor_ts(trade_date=date)
    add_count = 0
    for row in indicator_df.to_dict(orient='records'):
        stock_indicator = StockIndicatorPO(**row) # type: ignore
        # 检查是否存在相同股票代码和日期的记录
        obj = exchange_session.query(StockIndicatorPO).filter_by(full_symbol=stock_indicator.full_symbol, trade_date=stock_indicator.trade_date).first()
        if not obj:
            exchange_session.add(stock_indicator)
            add_count += 1
    exchange_session.commit()
    logging.info(f"已将当天股票每日指标数据更新到数据库中，共新增{add_count}条记录")
    
def update_daily_stock_moneyflow_job():
    """
    将当天收盘后所有股票的每日资金流向数据更新到数据库中
    
    """
    exchange_session = ExchangeDataBase.exchange_data_session()
    service = get_reference_exchange_service()
    # 当天日期
    date = datetime.datetime.now().strftime('%Y%m%d')
    # 当天股票每日资金流向数据
    moneyflow_df = service.get_stock_daily_moneyflow(trade_date=date)
    add_count = 0
    for row in moneyflow_df.to_dict(orient='records'):
        stock_moneyflow = StockMoneyflowPO(**row) # type: ignore
        # 检查是否存在相同股票代码和日期的记录
        obj = exchange_session.query(StockMoneyflowPO).filter_by(full_symbol=stock_moneyflow.full_symbol, trade_date=stock_moneyflow.trade_date).first()
        if not obj:
            exchange_session.add(stock_moneyflow)
            add_count += 1
    exchange_session.commit()
    logging.info(f"已将当天股票每日资金流向数据更新到数据库中，共新增{add_count}条记录")
