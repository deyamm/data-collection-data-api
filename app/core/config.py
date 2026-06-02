import logging
from pathlib import Path
from pydantic import PrivateAttr
import tushare as ts
from typing import Any

from pydantic_settings import BaseSettings


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class Settings(BaseSettings):

    # the root path of project
    BASE_DIR: Path = Path(__file__).resolve().parent.parent

    # the path of static folder
    STATIC_DIR: Path = Path.joinpath(BASE_DIR, "static")

    # sys schema
    SYS_URI: str = "mysql+aiomysql://root:qq16281091@localhost/basic_info?charset=utf8mb4"

    # basic data schema
    BASIC_DATA_URI: str = "mysql+aiomysql://root:qq16281091@localhost/type_basic_data?charset=utf8mb4"

    # exchange data schema
    EXCHANGE_DATA_URI: str = "mysql+aiomysql://root:qq16281091@localhost/type_exchange_data?charset=utf8mb4"

    # finance data schema
    FINANCE_DATA_URI: str = "mysql+aiomysql://root:qq16281091@localhost/type_finance_data?charset=utf8mb4"

    # tushare account
    TUSHARE_TOKEN: str = "92c6ece658c377bcc32995a68319cf01696e1266ed60be0ae0dd0947"

    _tu_pro: Any = PrivateAttr()

    TIMEZONE: str = "Asia/Shanghai"
    # Spring Boot callback endpoint base URL (used to POST final results)
    SPRING_CALLBACK_BASE_URL: str = "http://localhost:8080"

    # 具体实现方式后期再定
    allowed_schema_set: set[str] = {"type_basic_data", "type_exchange_data", "type_finance_data"}

    # 批量采集的批次大小
    batch_size: int = 5000

    def model_post_init(self, context: Any) -> None:
        self._tu_pro = ts.pro_api(self.TUSHARE_TOKEN)

    @property
    def TU_PRO(self):
        return self._tu_pro


settings = Settings()