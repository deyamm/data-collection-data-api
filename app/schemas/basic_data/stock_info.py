from pydantic import BaseModel

class StockInfo(BaseModel):
    full_symbol: str
    symbol: str
    name: str
    region: str
    industry: str
    company_name: str
    en_name: str
    en_spell: str
    market_type: str
    exchange: str
    currency_type: str
    list_status: str
    list_date: str
    delist_date: str | None
    is_hs: str
    act_name: str
    act_ent_type: str
