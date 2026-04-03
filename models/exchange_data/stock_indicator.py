from sqlalchemy import Integer, String, DateTime, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from core.db import ExchangeBase


class StockIndicatorPO(ExchangeBase):
    __tablename__ = 'stock_indicator'
    # 自增主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # 包含交易所标识的完整股票代码，例如"000001.SZ"
    full_symbol: Mapped[str] = mapped_column(String(16), comment="包含交易所标识的完整股票代码", nullable=False)
    # 交易日
    trade_date: Mapped[str] = mapped_column(String(16), comment="交易日", nullable=False)
    # 收盘价
    close: Mapped[float] = mapped_column(Float, comment="收盘价")
    # 换手率
    turnover_rate: Mapped[Optional[float]] = mapped_column(Float, comment="换手率")
    # 换手率（自由流通股）
    turnover_rate_f: Mapped[Optional[float]] = mapped_column(Float, comment="换手率（自由流通股）")
    # 量比
    volume_ratio: Mapped[Optional[float]] = mapped_column(Float, comment="量比")
    # PE
    pe: Mapped[Optional[float]] = mapped_column(Float, comment="PE")
    # PE(TTM)
    pe_ttm: Mapped[Optional[float]] = mapped_column(Float, comment="PE(TTM)")
    # 市净率
    pb: Mapped[Optional[float]] = mapped_column(Float, comment="市净率")
    # 市销率
    ps: Mapped[Optional[float]] = mapped_column(Float, comment="市销率")
    # 市销率(TTM)
    ps_ttm: Mapped[Optional[float]] = mapped_column(Float, comment="市销率(TTM)")
    # 股息率
    dv_ratio: Mapped[Optional[float]] = mapped_column(Float, comment="股息率")
    # 股息率(TTM)
    dv_ttm: Mapped[Optional[float]] = mapped_column(Float, comment="股息率(TTM)")
    # 总股本
    total_share: Mapped[Optional[float]] = mapped_column(Float, comment="总股本")
    # 流通股本
    float_share: Mapped[Optional[float]] = mapped_column(Float, comment="流通股本")
    # 自由流通股本
    free_share: Mapped[Optional[float]] = mapped_column(Float, comment="自由流通股本")
    # 总市值
    total_market_value: Mapped[Optional[float]] = mapped_column(Float, comment="总市值")
    # 流通市值
    float_market_value: Mapped[Optional[float]] = mapped_column(Float, comment="流通市值")

    __table_args__ = (
        # 创建联合索引，确保同一股票在同一交易日只有一条记录
        UniqueConstraint('full_symbol', 'trade_date', name='uix_full_symbol_trade_date'),
    )