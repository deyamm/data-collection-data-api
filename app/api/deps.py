from app.core.providers import AkShareProvider, TuShareProvider
from app.service.basic_data.market_service import MarketBasicDataService
from app.service.basic_data.stock_service import StockBasicDataService
from app.service.exchange_data.stock_service import StockExchangeDataService
from app.service.exchange_data.index_service import IndexExchangeDataService
from app.service.exchange_data.reference_service import ReferenceExchangeDataService

ak = AkShareProvider()
ts = TuShareProvider()

# basic data
def get_market_basic_data_service() -> MarketBasicDataService:
    return MarketBasicDataService(ak_provider=ak, ts_provider=ts)


def get_stock_basic_data_service() -> StockBasicDataService:
    return StockBasicDataService(ak_provider=ak, ts_provider=ts)


# exchange data
def get_stock_exchange_service() -> StockExchangeDataService:
    return StockExchangeDataService(ak_provider=ak, ts_provider=ts)


def get_index_exchange_service() -> IndexExchangeDataService:
    return IndexExchangeDataService(ak_provider=ak, ts_provider=ts)


def get_reference_exchange_service() -> ReferenceExchangeDataService:
    return ReferenceExchangeDataService(ak_provider=ak, ts_provider=ts)


# finance data
