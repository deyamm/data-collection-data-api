from sqlalchemy import Integer, String, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column
from core.db import BasicBase
from typing import Optional

class IndexInfoPO(BasicBase):

    __tablename__ = 'index_info'
    
    # 指数代码全称，包含市场标识和指数代码，例如：'000001.SH'、'399001.SZ'等，标识统一为大写，作为主键
    full_symbol: Mapped[str] = mapped_column(String(16), nullable=False, primary_key=True, comment="指数代码全称，包含市场标识和指数代码，例如：'000001.SH'、'399001.SZ'等，标识统一为大写")
    # 指数名称，例如：'上证指数'、'深证成指'
    name: Mapped[str] = mapped_column(String(64), nullable=False, comment="指数名称，例如：'上证指数'、'深证成指'")
    # 指数全称
    full_name: Mapped[str] = mapped_column(String(128), nullable=False, comment="指数全称")
    # 市场
    market: Mapped[str] = mapped_column(String(16), nullable=False, comment="市场")
    # 发布方
    publisher: Mapped[str] = mapped_column(String(32), nullable=False, comment="发布方")
    # 指数风格
    index_type: Mapped[Optional[str]] = mapped_column(String(32), comment="指数风格")
    # 指数类别
    category: Mapped[str] = mapped_column(String(32), nullable=False, comment="指数类别")
    # 基期
    base_date: Mapped[Optional[str]] = mapped_column(String(16), comment="基期")
    # 基点
    base_point: Mapped[Optional[float]] = mapped_column(Float, comment="基点")
    # 发布日期
    list_date: Mapped[Optional[str]] = mapped_column(String(16), comment="发布日期")
    # 加权方式
    weight_rule: Mapped[Optional[str]] = mapped_column(String(32), comment="加权方式")
    # 描述
    desc: Mapped[Optional[str]] = mapped_column(String(2048), comment="描述")
    # 终止日期
    exp_date: Mapped[Optional[str]] = mapped_column(String(16), comment="终止日期")
