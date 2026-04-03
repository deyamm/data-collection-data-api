from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import Annotated

from core.config import settings

# create engine for basic data, exchange_data, finance_data
basic_data_engine = create_engine(settings.BASIC_DATA_URI)
exchange_data_engine = create_engine(settings.EXCHANGE_DATA_URI)
finance_data_engine = create_engine(settings.FINANCE_DATA_URI)

# session
BasicDataSession = sessionmaker(basic_data_engine)
ExchangeDataSession = sessionmaker(exchange_data_engine)
FinanceDataSession = sessionmaker(finance_data_engine)

# used for create table
BasicBase = declarative_base()
ExchangeBase = declarative_base()
FinanceBase = declarative_base()


def init_basic_tables():
    BasicBase.metadata.create_all(bind=basic_data_engine)


def init_exchange_tables():
    ExchangeBase.metadata.create_all(bind=exchange_data_engine)


def init_finance_tables():
    FinanceBase.metadata.create_all(bind=finance_data_engine)


class BasicDataBase:
    @classmethod
    def basic_data_session(cls):
        return BasicDataSession()


class ExchangeDataBase:
    @classmethod
    def exchange_data_session(cls):
        return ExchangeDataSession()


class FinanceDataBase:
    @classmethod
    def finance_data_session(cls):
        return FinanceDataSession()

# FastApi 依赖注入，获取数据库session
def get_basic_db():
    db = BasicDataSession()
    try:
        yield db
    finally:
        db.close()

def get_exchange_db():
    db = ExchangeDataSession()
    try:
        yield db
    finally:
        db.close()

def get_finance_db():
    db = FinanceDataSession()
    try:
        yield db
    finally:
        db.close()

basic_session_dep = Annotated[Session, Depends(get_basic_db)]
exchange_session_dep = Annotated[Session, Depends(get_exchange_db)]
finance_session_dep = Annotated[Session, Depends(get_finance_db)]