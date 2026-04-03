from fastapi import FastAPI

from api.basic_data import basic_data_api
from api.exchange_data import exchange_data_api


app = FastAPI()

app.include_router(basic_data_api.router, prefix="/api/basic_data", tags=["basic_data"])
app.include_router(exchange_data_api.router, prefix="/api/exchange_data", tags=["exchange_data"])

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
