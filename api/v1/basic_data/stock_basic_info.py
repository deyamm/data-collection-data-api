from typing import List
import json

from fastapi import APIRouter, Depends

from schemas.basic_data.stock_info import StockInfo
from schemas.common.comn_response import ComnResponse
from service.basic_data.stock_service import StockBasicDataService
from core.deps import get_stock_basic_data_service

router = APIRouter(prefix='/stock_basic')

@router.get("/stock_info_collection", response_model=ComnResponse[List[StockInfo]])
def stock_info_collection(service: StockBasicDataService = Depends(get_stock_basic_data_service)):
    """
    
    :return: ComnResponse[List[StockInfo]]
    """
    stock_info = service.get_stock_info_collection_ts(
        full_symbol='',
        name='',
        market='',
        list_status='',
        exchange='',
        is_hs=''
    )
    return  ComnResponse.ok(data=json.loads(stock_info.to_json(orient="records", force_ascii=False)))