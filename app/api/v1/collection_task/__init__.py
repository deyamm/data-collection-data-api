"""
用于与后端交互的collection_task相关API路由模块
"""
from fastapi import APIRouter

from .collection_task import router

collection_task_router = APIRouter(prefix='/collection-task', tags=['collection_task'])

collection_task_router.include_router(router)