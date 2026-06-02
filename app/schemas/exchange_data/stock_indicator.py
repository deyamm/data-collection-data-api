from pydantic import BaseModel


class StockIndicator(BaseModel):
    """
    股票估值数据，主要包括pe、pb、ps等指标
    """
    # 代码全称
    full_symbol: str
    # 交易日
    trade_date: str
    # 收盘价
    close: float
    # 换手率
    turnover_rate: float
    # 换手率（自由流通股）
    turnover_rate_f: float
    # 量比
    volume_ratio: float
    # PE
    pe: float
    # PE(TTM)
    pe_ttm: float
    # 市净率
    pb: float
    # 市销率
    ps: float
    # 市销率(TTM)
    ps_ttm: float
    # 股息率
    dv_ratio: float
    # 股息率(TTM)
    dv_ttm: float
    # 总股本
    total_share: float
    # 流通股本
    float_share: float
    # 自由流通股本
    free_share: float
    # 总市值
    total_market_value: float
    # 流通市值
    float_market_value: float