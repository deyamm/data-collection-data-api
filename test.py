import asyncio

from app.core.providers import ak_provider
from app.core.providers import ts_provider

async def test():

    industry = await ts_provider.index_basic()

    print(industry.columns)
    print(industry.head())

asyncio.run(test())