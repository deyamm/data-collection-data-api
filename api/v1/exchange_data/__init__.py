from fastapi import APIRouter
from .index_data import router as index_data_router
from .reference_data import router as reference_data_router
from .stock_data import router as stock_data_router

exchange_data_router = APIRouter(prefix='/exchange_data')

exchange_data_router.include_router(index_data_router)
exchange_data_router.include_router(reference_data_router)
exchange_data_router.include_router(stock_data_router)