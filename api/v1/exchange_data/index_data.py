import json
from typing import List

from fastapi import APIRouter, Query, Depends

from schemas.exchange_data.index_k_data import IndexKData
from core.enum_params import PricePeriodType, PriceAdjustType
from service.exchange_data.index_service import IndexExchangeDataService
from core.deps import get_index_exchange_service
from schemas.common.comn_response import ComnResponse


router = APIRouter(prefix='/index_data')

@router.get("/industry_history_price_em", response_model=ComnResponse[List[IndexKData]])
def industry_history_price_em(
        symbol: str = Query(pattern="BK[0-9]{4}"),
        period: PricePeriodType = PricePeriodType.DAILY,
        start_date: str = Query(default="19700101"),
        end_date: str = Query(default="20500101"),
        adjust: PriceAdjustType = PriceAdjustType.DEFAULT,
        service: IndexExchangeDataService = Depends(get_index_exchange_service)
):
    """
    
    :return: ComnResponse[List[IndexKData]]
    """
    info = service.get_industry_history_price_em(symbol, period, start_date, end_date, adjust)
    return ComnResponse.ok(data=json.loads(info.to_json(orient="records", force_ascii=False)))


@router.get("/industry_history_price_ths", response_model=ComnResponse[List[IndexKData]])
def get_industry_history_price_ths(
        symbol: str,
        start_date: str = Query(default="19700101"),
        end_date: str = Query(default="20500101"),
        service: IndexExchangeDataService = Depends(get_index_exchange_service)
):
    info = service.get_industry_history_price_ths(symbol, start_date, end_date)
    return ComnResponse.ok(data=json.loads(info.to_json(orient="records", force_ascii=False)))


@router.get("/concept_history_price_em", response_model=ComnResponse[List[IndexKData]])
def get_concept_history_price_em(
        symbol: str,
        period: PricePeriodType = PricePeriodType.DAILY,
        start_date: str = Query(default="19700101"),
        end_date: str = Query(default="20500101"),
        adjust: PriceAdjustType = PriceAdjustType.DEFAULT,
        service: IndexExchangeDataService = Depends(get_index_exchange_service)
):
    info = service.get_concept_history_price_em(symbol, period, start_date, end_date, adjust)
    return ComnResponse.ok(data=json.loads(info.to_json(orient="records", force_ascii=False)))


@router.get("/concept_history_price_ths", response_model=ComnResponse[List[IndexKData]])
def get_concept_history_price_ths(
        symbol: str,
        start_date: str = Query(default="19700101"),
        end_date: str = Query(default="20500101"),
        service: IndexExchangeDataService = Depends(get_index_exchange_service)
):
    info = service.get_concept_history_price_ths(symbol, start_date, end_date)
    return ComnResponse.ok(data=json.loads(info.to_json(orient="records", force_ascii=False)))


@router.get("/index_history_price_csi", response_model=ComnResponse[List[IndexKData]])
def get_index_history_price_csi(
        symbol: str,
        start_date: str = Query(default="19700101"),
        end_date: str = Query(default="20500101"),
        service: IndexExchangeDataService = Depends(get_index_exchange_service)
):
    info = service.get_index_history_price_csi(symbol, start_date, end_date)
    return ComnResponse.ok(data=json.loads(info.to_json(orient="records", force_ascii=False)))


@router.get("/index_history_price_cni", response_model=ComnResponse[List[IndexKData]])
def get_index_history_price_cni(
        symbol: str,
        start_date: str = Query(default="19700101"),
        end_date: str = Query(default="20500101"),
        service: IndexExchangeDataService = Depends(get_index_exchange_service)
):
    info = service.get_index_history_price_cni(symbol, start_date, end_date)
    return ComnResponse.ok(data=json.loads(info.to_json(orient="records", force_ascii=False)))


@router.get("/index_daily_ts", response_model=ComnResponse[List[IndexKData]])
def get_index_daily_ts(
        full_symbol: str = Query(default=''),
        trade_date: str = Query(default=''),
        start_date: str = Query(default=''),
        end_date: str = Query(default=''),
        service: IndexExchangeDataService = Depends(get_index_exchange_service)
):
    info = service.get_index_daily_ts(full_symbol=full_symbol, trade_date=trade_date, start_date=start_date, end_date=end_date)
    return ComnResponse.ok(data=json.loads(info.to_json(orient="records", force_ascii=False)))
