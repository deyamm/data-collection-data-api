from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from app.core.config import settings


# 注意：
# 这里的 URI 必须使用 SQLAlchemy 异步驱动。
#
# 示例：
# PostgreSQL: postgresql+asyncpg://user:password@host:5432/dbname
# MySQL:      mysql+aiomysql://user:password@host:3306/dbname
# MySQL:      mysql+asyncmy://user:password@host:3306/dbname
# SQLite:     sqlite+aiosqlite:///./test.db


# create async engine for basic data, exchange_data, finance_data
basic_data_engine = create_async_engine(
    settings.BASIC_DATA_URI,
    pool_pre_ping=True,
)

exchange_data_engine = create_async_engine(
    settings.EXCHANGE_DATA_URI,
    pool_pre_ping=True,
)

finance_data_engine = create_async_engine(
    settings.FINANCE_DATA_URI,
    pool_pre_ping=True,
)


# async session factories
BasicDataSession = async_sessionmaker(
    bind=basic_data_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

ExchangeDataSession = async_sessionmaker(
    bind=exchange_data_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

FinanceDataSession = async_sessionmaker(
    bind=finance_data_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# used for db models
BasicBase = declarative_base()
ExchangeBase = declarative_base()
FinanceBase = declarative_base()


# async def init_basic_tables() -> None:
#     async with basic_data_engine.begin() as conn:
#         await conn.run_sync(BasicBase.metadata.create_all)


# async def init_exchange_tables() -> None:
#     async with exchange_data_engine.begin() as conn:
#         await conn.run_sync(ExchangeBase.metadata.create_all)


# async def init_finance_tables() -> None:
#     async with finance_data_engine.begin() as conn:
#         await conn.run_sync(FinanceBase.metadata.create_all)


# async def init_all_tables() -> None:
#     await init_basic_tables()
#     await init_exchange_tables()
#     await init_finance_tables()


def get_engine_by_schema(schema_name: str):
    if schema_name == "type_basic_data":
        return basic_data_engine
    elif schema_name == "type_exchange_data":
        return exchange_data_engine
    elif schema_name == "type_finance_data":
        return finance_data_engine
    else:
        raise ValueError(f"不支持的 schema: {schema_name}")


async def dispose_all_engines() -> None:
    await basic_data_engine.dispose()
    await exchange_data_engine.dispose()
    await finance_data_engine.dispose()


class BasicDataBase:
    @classmethod
    def basic_data_session(cls) -> AsyncSession:
        return BasicDataSession()


class ExchangeDataBase:
    @classmethod
    def exchange_data_session(cls) -> AsyncSession:
        return ExchangeDataSession()


class FinanceDataBase:
    @classmethod
    def finance_data_session(cls) -> AsyncSession:
        return FinanceDataSession()


# FastAPI 依赖注入，获取异步数据库 session
async def get_basic_db() -> AsyncGenerator[AsyncSession, None]:
    async with BasicDataSession() as db:
        yield db


async def get_exchange_db() -> AsyncGenerator[AsyncSession, None]:
    async with ExchangeDataSession() as db:
        yield db


async def get_finance_db() -> AsyncGenerator[AsyncSession, None]:
    async with FinanceDataSession() as db:
        yield db


basic_session_dep = Annotated[AsyncSession, Depends(get_basic_db)]
exchange_session_dep = Annotated[AsyncSession, Depends(get_exchange_db)]
finance_session_dep = Annotated[AsyncSession, Depends(get_finance_db)]