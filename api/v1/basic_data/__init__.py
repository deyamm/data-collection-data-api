from fastapi import APIRouter
from .market_basic_info import router as market_basic_info_router
from .stock_basic_info import router as stock_basic_info_router

basic_data_router = APIRouter(prefix='/basic_data')

basic_data_router.include_router(market_basic_info_router)
basic_data_router.include_router(stock_basic_info_router)