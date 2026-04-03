import json
from typing import List

from fastapi import APIRouter, Query, Depends
import akshare as ak

from utils.column_translation import translate_column_name

from schemas.exchange_data.stock_indicator import StockIndicator
from schemas.common.comn_response import ComnResponse
from core.deps import get_reference_exchange_service
from service.exchange_data.reference_service import ReferenceExchangeDataService

router = APIRouter()


@router.get("/stock_daily_indictor", response_model=ComnResponse[List[StockIndicator]])
def stock_daily_indictor(
    full_symbol: str = '',
    trade_date: str = '',
    start_date: str = '',
    end_date: str = '', 
    service: ReferenceExchangeDataService = Depends(get_reference_exchange_service)):
    """个股的历史每日指标
    Args:
        symbol (str, optional): _description_. Defaults to Query(pattern="[0-9]{6}").
        service (ReferenceExchangeDataService, optional): _description_. Defaults to Depends(get_reference_exchange_service).

    Returns:
        ComnResponse[List[StockValuation]]: _description_
    """
    if full_symbol == '' and trade_date == '':
        return ComnResponse.fail(400, message="symbol和trade_date不能同时为空，请至少提供一个参数")
    valuation_df = service.get_stock_daily_indictor_ts(full_symbol=full_symbol, trade_date=trade_date, start_date=start_date, end_date=end_date)
    return ComnResponse.ok(json.loads(valuation_df.to_json(orient="records", force_ascii=False)))