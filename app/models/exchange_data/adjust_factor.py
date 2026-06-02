from sqlalchemy import Integer, String, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from core.db import ExchangeBase


class AdjustFactorPO(ExchangeBase):
    __tablename__ = 'adjust_factor'
    # 自增主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # 交易日期
    trade_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="交易日期")
    # 不包含交易所标识的股票代码，例如"000001"
    symbol: Mapped[str] = mapped_column(String(10), comment="不包含交易所标识的股票代码", nullable=False)
    # 前复权因子
    forward_adj_factor: Mapped[float] = mapped_column(Float, comment="前复权因子")
    # 后复权因子
    backward_adj_factor: Mapped[float] = mapped_column(Float, comment="后复权因子")
    # 前累计复权因子
    acc_forward_adj_factor: Mapped[float] = mapped_column(Float, comment="前累计复权因子")
    # 后累计复权因子
    acc_backward_adj_factor: Mapped[float] = mapped_column(Float, comment="后累计复权因子")
