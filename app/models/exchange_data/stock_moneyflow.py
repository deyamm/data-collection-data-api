from typing import Optional

from sqlalchemy import Float, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from core.db import ExchangeBase


class StockMoneyflowPO(ExchangeBase):
    """
    个股资金流向
    """
    __tablename__ = "stock_moneyflow"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nautoincrement=True, comment="自增主键")

    full_symbol: Mapped[str] = mapped_column(String(16), comment="代码全称，带市场标识的股票代码，如000001.SZ")

    trade_date: Mapped[str] = mapped_column(String(16), comment="交易日，格式YYYYMMDD")

    buy_sm_vol: Mapped[Optional[int]] = mapped_column(Integer, comment="小单买入量（手）")

    buy_sm_amount: Mapped[Optional[float]] = mapped_column(Float, comment="小单买入金额（万元）")

    sell_sm_vol: Mapped[Optional[int]] = mapped_column(Integer, comment="小单卖出量（手）")

    sell_sm_amount: Mapped[Optional[float]] = mapped_column(Float, comment="小单卖出金额（万元）")

    buy_md_vol: Mapped[Optional[int]] = mapped_column(Integer, comment="中单买入量（手）")

    buy_md_amount: Mapped[Optional[float]] = mapped_column(Float, comment="中单买入金额（万元）")

    sell_md_vol: Mapped[Optional[int]] = mapped_column(Integer, comment="中单卖出量（手）")

    sell_md_amount: Mapped[Optional[float]] = mapped_column(Float, comment="中单卖出金额（万元）")

    buy_lg_vol: Mapped[Optional[int]] = mapped_column(Integer, comment="大单买入量（手）")

    buy_lg_amount: Mapped[Optional[float]] = mapped_column(Float, comment="大单买入金额（万元）")

    sell_lg_vol: Mapped[Optional[int]] = mapped_column(Integer, comment="大单卖出量（手）")

    sell_lg_amount: Mapped[Optional[float]] = mapped_column(Float, comment="大单卖出金额（万元）")

    buy_elg_vol: Mapped[Optional[int]] = mapped_column(Integer, comment="特大单买入量（手）")

    buy_elg_amount: Mapped[Optional[float]] = mapped_column(Float, comment="特大单买入金额（万元）")

    sell_elg_vol: Mapped[Optional[int]] = mapped_column(Integer, comment="特大单卖出量（手）")

    sell_elg_amount: Mapped[Optional[float]] = mapped_column(Float, comment="特大单卖出金额（万元）")

    net_mf_vol: Mapped[Optional[int]] = mapped_column(Integer, comment="净流入量（手）")

    net_mf_amount: Mapped[Optional[float]] = mapped_column(Float, comment="净流入额（万元）")

    __table_args__ = (
        UniqueConstraint(
            "full_symbol",
            "trade_date",
            name="uq_stock_moneyflow_symbol_trade_date",
        )
    )