from fastapi import APIRouter
from .collection_task import collection_task_router

router = APIRouter(prefix='/v1')

router.include_router(collection_task_router)

