from typing import Optional

from sqlalchemy import Integer, String, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column
from core.db import BasicBase


class StockInfoPO(BasicBase):
    __tablename__ = 'stock_info'
    
    full_symbol: Mapped[str] = mapped_column(String(16), comment="代码全称，完整股票代码", primary_key=True)

    symbol: Mapped[Optional[str]] = mapped_column(String(16), comment="证券代码，股票代码，纯代码，裸代码")

    name: Mapped[Optional[str]] = mapped_column(String(32), comment="证券简称，股票简称，名称")
    
    region: Mapped[Optional[str]] = mapped_column(String(16), comment="地区")
    
    industry: Mapped[Optional[str]] = mapped_column(String(32), comment="所属行业")
    
    full_name: Mapped[Optional[str]] = mapped_column(String(128), comment="公司全称")
    
    en_name: Mapped[Optional[str]] = mapped_column(String(128), comment="英文名称")
    
    cn_spell: Mapped[Optional[str]] = mapped_column(String(64), comment="英文拼写")
    
    market_type: Mapped[Optional[str]] = mapped_column(String(32), comment="市场类型")
    
    exchange: Mapped[Optional[str]] = mapped_column(String(16), comment="交易所代码")
    
    currency_type: Mapped[Optional[str]] = mapped_column(String(16), comment="交易货币")
    
    list_status: Mapped[Optional[str]] = mapped_column(String(16), comment="上市状态")
    
    list_date: Mapped[Optional[str]] = mapped_column(String(16), comment="上市日期，A股上市日期")
    
    delist_date: Mapped[Optional[str]] = mapped_column(String(16), comment="退市日期")
    
    is_hs: Mapped[Optional[str]] = mapped_column(String(8), comment="是否沪深港通标的")
    
    act_name: Mapped[Optional[str]] = mapped_column(String(128), comment="实控人名称")
    
    act_ent_type: Mapped[Optional[str]] = mapped_column(String(64), comment="实控人企业性质")

