from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.router import router as router_v1
from fastapi.middleware.cors import CORSMiddleware
from app.core.logger import setup_logging
from app.tasks import register_all_tasks

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 应用启动时执行的代码
    setup_logging()
    register_all_tasks()
    yield
    

app = FastAPI(lifespan=lifespan)

app.include_router(router_v1)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

# CORS 配置（开发环境放开，生产环境按需收紧）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)