from api.exchange_data.market_data.stock_price import get_current_snapshot, get_stock_history_price
from schemas.exchange_data.price_snapshot import PriceSnapshot
from schemas.exchange_data.stock_k_data import StockKData
import akshare as ak


def test_get_current_snapshot():
    snap = get_current_snapshot()
    print(snap)
    assert isinstance(snap, list)
    assert len(snap) > 0
    assert isinstance(snap[0], dict)

snap_df = ak.stock_zh_a_spot_em().drop(columns="序号")
print(snap_df.head())