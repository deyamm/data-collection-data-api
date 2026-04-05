import json
from typing import List
from fastapi import APIRouter, Query, Depends

from core.enum_params import PricePeriodType, PriceAdjustType
from schemas.exchange_data.price_snapshot import PriceSnapshot
from schemas.exchange_data.stock_k_data import StockKData
from schemas.common.comn_response import ComnResponse
from service.exchange_data.stock_service import StockExchangeDataService

from core.deps import get_stock_exchange_service

router = APIRouter(prefix='/stock_data')

@router.get("/current_snapshot", response_model=ComnResponse[List[PriceSnapshot]])
def current_snapshot(service: StockExchangeDataService = Depends(get_stock_exchange_service)):
    """
    获取当前所有股票的实时行情.

    Returns:
        List of PriceSnapshot.
    """
    snap_df = service.get_current_snapshot()
    return ComnResponse.ok(data=json.loads(snap_df.to_json(orient="records", force_ascii=False)))


@router.get("/stock_history_price", response_model=ComnResponse[List[StockKData]])
def stock_history_price(
        symbol: str = Query(pattern="[0-9]{6}"),
        period: PricePeriodType = PricePeriodType.DAILY,
        start_date: str = Query(default="19700101"),
        end_date: str = Query(default="20500101"),
        adjust: PriceAdjustType = PriceAdjustType.DEFAULT,
        service: StockExchangeDataService = Depends(get_stock_exchange_service)
):
    """

    获取历史股票价格数据.

    Args:
        symbol (str): 股票代码，不包含交易所标识，6位数字.
        period (PricePeriodType): K线周期类型，缺省为日线.
        start_date (str): 开始日期，YYYYMMDD格式，缺省为'19700101'.
        end_date (str): 结束日期，YYYYMMDD格式，缺省为'20500101'.
        adjust (PriceAdjustType): 价格调整类型，缺省为不调整.
        service (StockExchangeDataService): StockExchangeDataService dependency.

    Returns:
        List of StockKData.

    """
    history_df = service.get_stock_history_price(symbol, period, start_date, end_date, adjust)
    return ComnResponse.ok(data=json.loads(history_df.to_json(orient="records", force_ascii=False)))


@router.get("/daily_stock_price/{date}", response_model=ComnResponse[List[StockKData]])
def daily_stock_price(date: str, service: StockExchangeDataService = Depends(get_stock_exchange_service)):
    """
    获取指定日期所有股票的历史价格数据.

    Uses tushare.pro interface.
    Args:
        date (str): YYYYMMDD格式日期字符串
        service: StockExchangeDataService dependency.

    Returns:
        List of StockKData.
    """
    daily_price = service.get_daily_stock_price(date)
    return ComnResponse.ok(data=json.loads(daily_price.to_json(orient="records", force_ascii=False)))
