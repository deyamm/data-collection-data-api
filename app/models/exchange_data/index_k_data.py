from sqlalchemy import Integer, String, DateTime, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from core.db import ExchangeBase


class IndexKDataPO(ExchangeBase):
    __tablename__ = 'index_k_data'
    # 自增主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # 包含交易所标识的完整指数代码，例如"000001.SH"
    full_symbol: Mapped[str] = mapped_column(String(16), comment='指数代码', nullable=False)
    # 交易日期
    trade_date: Mapped[datetime] = mapped_column(DateTime, comment='交易日期', nullable=False)
    # 开盘点位
    open: Mapped[float] = mapped_column(Float, comment='开盘点位')
    # 最高点位
    high: Mapped[float] = mapped_column(Float, comment='最高点位')
    # 最低点位
    low: Mapped[float] = mapped_column(Float, comment='最低点位')
    # 收盘点位
    close: Mapped[float] = mapped_column(Float, comment='收盘点位')
    # 交易量
    volume: Mapped[float] = mapped_column(Float, comment='交易量')
    # 交易额
    turnover: Mapped[float] = mapped_column(Float, comment='交易额')
    # 前一日收盘点
    pre_close: Mapped[float] = mapped_column(Float, comment='前一日收盘点')
    # 涨跌幅
    chg_pct: Mapped[float] = mapped_column(Float, comment='涨跌幅')
    # 涨跌点
    chg_amt: Mapped[float] = mapped_column(Float, comment='涨跌点')

    __table_args__ = (
        # 创建联合索引，确保同一指数在同一交易日只有一条记录
        UniqueConstraint('full_symbol', 'trade_date', name='uix_full_symbol_trade_date'),
    )