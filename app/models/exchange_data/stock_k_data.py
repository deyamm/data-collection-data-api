from sqlalchemy import Integer, String, DateTime, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from typing import Optional
from core.db import ExchangeBase


class StockKDataPO(ExchangeBase):
    __tablename__ = 'stock_k_data'
    # 自增主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # 包含交易所标识的完整股票代码，例如"000001.SZ"
    full_symbol: Mapped[str] = mapped_column(String(16), comment='证券代码', nullable=False)
    # 交易日期
    trade_date: Mapped[datetime] = mapped_column(DateTime, comment='交易日期', nullable=False)
    # 开盘价
    open: Mapped[float] = mapped_column(Float, comment='开盘价')
    # 最高价
    high: Mapped[float] = mapped_column(Float, comment='最高价')
    # 最低价
    low: Mapped[float] = mapped_column(Float, comment='最低价')
    # 收盘价
    close: Mapped[float] = mapped_column(Float, comment='收盘价')
    # 交易量
    volume: Mapped[float] = mapped_column(Float, comment='交易量')
    # 交易额
    turnover: Mapped[float] = mapped_column(Float, comment='交易额')
    # 前一日收盘价
    pre_close: Mapped[Optional[float]] = mapped_column(Float, comment='前一日收盘价')
    # 涨跌幅
    chg_pct: Mapped[Optional[float]] = mapped_column(Float, comment='涨跌幅')
    # 涨跌额
    chg_amt: Mapped[Optional[float]] = mapped_column(Float, comment='涨跌额')
    # k线周期
    period: Mapped[int] = mapped_column(Integer, comment='周期')

    __table_args__ = (
        # 创建联合索引，确保同一股票在同一交易日只有一条记录
        UniqueConstraint('full_symbol', 'trade_date', name='uix_full_symbol_trade_date'),
    )
