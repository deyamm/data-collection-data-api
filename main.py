from fastapi import FastAPI

from api.router import router as router_v1


app = FastAPI()

app.include_router(router_v1)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
