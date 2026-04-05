from fastapi import APIRouter
from .basic_data import basic_data_router
from .exchange_data import exchange_data_router

router = APIRouter(prefix='/v1')

router.include_router(basic_data_router)
router.include_router(exchange_data_router)