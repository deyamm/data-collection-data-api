from enum import Enum
import logging


class PriceAdjustType(str, Enum):
    """
    股价的复权方法
    DEFAULT: ""，不复权
    FORWARD: qfq，前复权
    BACKWARD: hfq，后复权
    """
    DEFAULT = ""
    FORWARD = "qfq"
    BACKWARD = "hfq"


class PricePeriodType(str, Enum):
    """
    K线级别
    DAILY: daily，日K线
    WEEKLY：weekly，周K线
    MONTHLY：monthly，月k线
    """
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

    def db_code(self) -> int:
        return {'daily': 1, 'weekly': 2, 'monthly': 3}[self.value]

    def em_period_chg(self) -> str:
        return {'daily': '日k', 'weekly': '周k', 'monthly': '月k'}[self.value]


class StockMarketType(str, Enum):
    """
    股票所上市的市场
    """
    # 上交所主板A股
    SSE_A = 1
    # 上证B股
    SSE_B = 2
    # 深交所主板
    SZSE_A = 4
    # 深交所B股
    SZSE_B = 8
    # 深交所创业板
    SZSE_CY = 16
    # 上交所科创板
    SSE_KC = 32
    # 北交所
    BSE = 64
    # 其他市场，包含未上市的股票、港股、美股等
    OTHER = 99


class IndexMarket(str, Enum):
    """
    基于Tushare指数基本信息接口中的市场分类，添加了东方财富指数和同花顺指数的分类
    """
    num: int
    label: str

    # 上交所指数
    SSE = ('SSE', 1, '上交所指数')
    # 深交所指数
    SZSE = ('SZSE', 2, '深交所指数')
    # 中证指数
    CSI = ('CSI', 3, '中证指数')
    # 国证指数
    CNI = ('CNI', 4, '国证指数')
    # 中金指数
    CICC = ('CICC', 5, '中金指数')
    # 申万指数
    SW = ('SW', 6, '申万指数')
    # MSCI
    MSCI = ('MSCI', 7, 'MSCI指数')
    # 东方财富指数
    EM = ('EM', 8, '东方财富指数')
    # 同花顺指数
    THS = ('THS', 9, '同花顺指数')
    # 其他指数
    OTH = ('OTH', 99, '其他指数')

    def __new__(cls, code: str, num: int, label: str):
        obj = str.__new__(cls, code)
        obj._value_ = code
        obj.num = num
        obj.label = label
        return obj

    def __str__(self) -> str:
        return self.value

    @classmethod
    def search_value(cls, value: str) -> "IndexMarket":
        for item in cls:
            if item.value == value:
                return item
        logging.warning(f"未找到匹配的指数市场类型，value={value}，返回默认值OTH")
        return cls.OTH

    @classmethod
    def from_num(cls, num: int) -> "IndexMarket":
        for item in cls:
            if item.num == num:
                return item
        raise ValueError(f"No IndexMarket with num={num}")

    @classmethod
    def from_label(cls, label: str) -> "IndexMarket":
        for item in cls:
            if item.label == label:
                return item
        raise ValueError(f"No IndexMarket with label={label}")

    def to_dict(self) -> dict:
        return {
            "code": self.value,
            "num": self.num,
            "label": self.label,
        }


class IndexCategory(str, Enum):
    """
    指数类别，基于Tushare指数基本信息接口中的分类
    """
    num: int
    label: str

    COMPOSITE = ('COMPOSITE', 1, '综合指数')
    SIZE = ('SIZE', 2, '规模指数')
    STYLE = ('STYLE', 3, '风格指数')
    THEMATIC = ('THEMATIC', 4, '主题指数')
    INDUSTRY = ('INDUSTRY', 5, '行业指数')
    STRATEGY = ('STRATEGY', 6, '策略指数')
    GROWTH = ('GROWTH', 7, '成长指数')
    VALUE = ('VALUE', 8, '价值指数')
    CONCEPT = ('CONCEPT', 9, '概念指数') # 用于同花顺和东方财富的概念指数分类
    OTHER = ('OTHER', 99, '其他指数')

    def __new__(cls, code: str, num: int, label: str):
        obj = str.__new__(cls, code)
        obj._value_ = code
        obj.num = num
        obj.label = label
        return obj

    def __str__(self) -> str:
        return self.value

    @classmethod
    def search_value(cls, value: str) -> "IndexCategory":
        for item in cls:
            if item.value == value:
                return item
        logging.warning(f"未找到匹配的指数分类，value={value}，返回默认值OTHER")
        return cls.OTHER

    @classmethod
    def from_num(cls, num: int) -> "IndexCategory":
        for item in cls:
            if item.num == num:
                return item
        raise ValueError(f"No IndexCategory with num={num}")

    @classmethod
    def from_label(cls, label: str) -> "IndexCategory":
        for item in cls:
            if item.label == label:
                return item
        raise ValueError(f"No IndexCategory with label={label}")

    def to_dict(self) -> dict:
        return {
            "code": self.value,
            "num": self.num,
            "label": self.label,
        }