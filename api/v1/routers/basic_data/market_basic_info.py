import json
from typing import List

from fastapi import APIRouter, Query, Depends

from schemas.basic_data.index_constituent import IndexConstituent
from schemas.basic_data.index_info import IndexInfo
from schemas.common.comn_response import ComnResponse

from service.basic_data.market_service import MarketBasicDataService
from core.deps import get_market_basic_data_service


router = APIRouter()

@router.get("/industry_info_em", response_model=ComnResponse[List[IndexInfo]])
def industry_info_em(service: MarketBasicDataService = Depends(get_market_basic_data_service)):
    """
    
    Returns:
        ComnResponse[List[IndexInfo]]: List of IndexInfo objects containing industry information.
    """
    data = service.get_industry_info_em()
    return ComnResponse.ok(data=json.loads(data.to_json(orient="records", force_ascii=False)))


@router.get("/industry_constituent_em", response_model=ComnResponse[List[IndexConstituent]])
def industry_constituent_em(
        symbol: str = Query(pattern="BK[0-9]{4}"),
        service: MarketBasicDataService = Depends(get_market_basic_data_service)
):
    """
    Returns:
        ComnResponse[List[IndexInfo]]: 
    """
    data = service.get_industry_constituent_em(symbol=symbol)
    return ComnResponse.ok(data=json.loads(data.to_json(orient="records", force_ascii=False)))


@router.get("/industry_info_ths", response_model=ComnResponse[List[IndexInfo]])
def industry_info_ths(service: MarketBasicDataService = Depends(get_market_basic_data_service)):
    """
    
    Returns:
        ComnResponse[List[IndexInfo]]: 
    """
    data = service.get_industry_info_ths()
    return ComnResponse.ok(data=json.loads(data.to_json(orient="records", force_ascii=False)))


@router.get("/concept_info_em", response_model=ComnResponse[List[IndexInfo]])
def concept_info_em(service: MarketBasicDataService = Depends(get_market_basic_data_service)):
    """
    
    Returns:
        ComnResponse[List[IndexInfo]]: 
    """
    data = service.get_concept_info_em()
    return ComnResponse.ok(data=json.loads(data.to_json(orient="records", force_ascii=False)))


@router.get("/concept_constituent_em", response_model=ComnResponse[List[IndexConstituent]])
def concept_constituent_em(
        symbol: str = Query(pattern="BK[0-9]{4}"),
        service: MarketBasicDataService = Depends(get_market_basic_data_service)
):
    """
    
    Returns:
        ComnResponse[List[IndexConstituent]]: 
    """
    data = service.get_concept_constituent_em(symbol=symbol)
    return ComnResponse.ok(data=json.loads(data.to_json(orient="records", force_ascii=False)))


@router.get("/concept_info_ths", response_model=ComnResponse[List[IndexInfo]])
def concept_info_ths(service: MarketBasicDataService = Depends(get_market_basic_data_service)):
    """
    
    Returns:
        ComnResponse[List[IndexInfo]]: 
    """
    data = service.get_concept_info_ths()
    return ComnResponse.ok(data=json.loads(data.to_json(orient="records", force_ascii=False)))


@router.get("/index_info_csi", response_model=ComnResponse[List[IndexInfo]])
def index_info_csi(service: MarketBasicDataService = Depends(get_market_basic_data_service)):
    """
    
    Returns:
        ComnResponse[List[IndexInfo]]: 
    """
    info = service.get_index_csindex_all()
    return ComnResponse.ok(data=json.loads(info.to_json(orient="records", force_ascii=False)))


@router.get("/index_constituent_csi", response_model=ComnResponse[List[IndexConstituent]])
def index_constituent_csi(symbol: str, service: MarketBasicDataService = Depends(get_market_basic_data_service)):
    """
    Returns:
        ComnResponse[List[IndexConstituent]]: 
    """
    data = service.get_index_constituent_csi(symbol=symbol)
    return ComnResponse.ok(data=json.loads(data.to_json(orient="records", force_ascii=False)))


@router.get("/index_info_cni", response_model=ComnResponse[List[IndexInfo]])
def index_info_cni(service: MarketBasicDataService = Depends(get_market_basic_data_service)):
    """
    
    Returns:
        ComnResponse[List[IndexInfo]]: 
    """
    info = service.get_index_info_cni()
    return ComnResponse.ok(data=json.loads(info.to_json(orient="records", force_ascii=False)))


@router.get("/index_constituent_cni", response_model=ComnResponse[List[IndexConstituent]])
def index_constituent_cni(
    symbol: str, 
    date: str|None = None, 
    service: MarketBasicDataService = Depends(get_market_basic_data_service)
    ):
    """
    
    Returns:
        ComnResponse[List[IndexConstituent]]: 
    """
    cons = service.get_index_constituent_cni(symbol=symbol, date=date)
    return ComnResponse.ok(data=json.loads(cons.to_json(orient="records", force_ascii=False)))


@router.get("/index_info_general", response_model=ComnResponse[List[IndexInfo]])
def index_info_general(service: MarketBasicDataService = Depends(get_market_basic_data_service)):
    """
    
    Returns:
        ComnResponse[List[IndexInfo]]: 
    """
    info = service.get_index_info_general()
    return ComnResponse.ok(data=json.loads(info.to_json(orient="records", force_ascii=False)))


@router.get("/index_basic", response_model=ComnResponse[List[IndexInfo]])
def index_basic(
    full_symbol: str = '',
    name: str = '',
    market: str = '',
    publisher: str = '',
    category: str = '',
    service: MarketBasicDataService = Depends(get_market_basic_data_service)
):
    """
    获取指数基本信息
    """
    data = service.get_index_basic_info(full_symbol=full_symbol, name=name, market=market, publisher=publisher, category=category)
    return ComnResponse.ok(data=json.loads(data.to_json(orient="records", force_ascii=False)))
