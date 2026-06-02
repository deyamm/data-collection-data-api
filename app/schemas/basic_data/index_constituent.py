from pydantic import BaseModel

class IndexConstituent(BaseModel):
    index_code: str
    symbol: str
    name: str
    index_source: int