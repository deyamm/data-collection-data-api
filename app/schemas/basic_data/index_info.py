from pydantic import BaseModel

class IndexInfo(BaseModel):
    
    full_symbol: str
    symbol: str
    full_name: str
    market: str
    publisher: str
    index_type: str
    category: str
    base_date: str | None = None
    base_point: float | None = None
    list_date: str | None = None
    weight_rule: str | None = None
    desc: str | None = None
    exp_date: str | None = None