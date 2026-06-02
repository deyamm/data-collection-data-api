from pydantic import BaseModel

class StockKData(BaseModel):
    # 股票代码
    full_symbol: str
    # 交易日
    trade_date: str
    # 开盘价
    open: float
    # 收盘价
    close: float
    # 最高
    high: float
    # 最低
    low: float
    # 成交量
    volume: float
    # 成交额
    turnover: float
    # 涨跌幅
    chg_pct: float
    # 涨跌额
    chg_amt: float
    # 昨收
    pre_close: float
    # k线周期，1:daily, 2:weekly, 3:monthly
    period: int


