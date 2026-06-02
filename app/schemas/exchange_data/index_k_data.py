from pydantic import BaseModel

class IndexKData(BaseModel):
    # 指数代码
    full_symbol: str
    # 交易日
    trade_date: str
    # 开盘点位
    open: float
    # 收盘点位
    close: float
    # 最高点位
    high: float
    # 最低点位
    low: float
    # 成交量（手）
    volume: float
    # 成交额（千元）
    turnover: float
    # 涨跌幅（%）
    chg_pct: float
    # 涨跌点
    chg_amt: float
    # 昨日收盘点
    pre_close: float


