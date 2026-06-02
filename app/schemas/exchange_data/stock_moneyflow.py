from pydantic import BaseModel


class StockMoneyflow(BaseModel):
    """
    个股资金流向
    """

    # 代码全称
    full_symbol: str
    # 交易日
    trade_date: str

    # 小单买入量（手）
    buy_sm_vol: int
    # 小单买入金额（万元）
    buy_sm_amount: float
    # 小单卖出量（手）
    sell_sm_vol: int
    # 小单卖出金额（万元）
    sell_sm_amount: float

    # 中单买入量（手）
    buy_md_vol: int
    # 中单买入金额（万元）
    buy_md_amount: float
    # 中单卖出量（手）
    sell_md_vol: int
    # 中单卖出金额（万元）
    sell_md_amount: float

    # 大单买入量（手）
    buy_lg_vol: int
    # 大单买入金额（万元）
    buy_lg_amount: float
    # 大单卖出量（手）
    sell_lg_vol: int
    # 大单卖出金额（万元）
    sell_lg_amount: float

    # 特大单买入量（手）
    buy_elg_vol: int
    # 特大单买入金额（万元）
    buy_elg_amount: float
    # 特大单卖出量（手）
    sell_elg_vol: int
    # 特大单卖出金额（万元）
    sell_elg_amount: float

    # 净流入量（手）
    net_mf_vol: int
    # 净流入额（万元）
    net_mf_amount: float

