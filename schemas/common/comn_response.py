from typing import Generic, Optional, TypeVar, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from pydantic.generics import GenericModel

TRes = TypeVar("TRes")


class ComnError(BaseModel):
    """
    可选：用于返回字段级错误/校验错误的统一结构
    """
    field: Optional[str] = None
    message: str
    code: Optional[str] = None


class ComnResponse(GenericModel, Generic[TRes]):
    """
    通用响应结构：
    - code: 0 表示成功，非 0 表示失败（你也可以用 200/非200）
    - message: 文案
    - trace_id: 回传链路追踪
    - data: 成功时业务数据
    - errors: 失败时可带详细错误
    """
    model_config = ConfigDict(extra="ignore")

    code: int = 200
    message: str = "OK"
    trace_id: Optional[str] = None
    data: Optional[TRes] = None
    errors: Optional[List[ComnError]] = None

    @classmethod
    def ok(cls, data: TRes = None, trace_id: Optional[str] = None, message: str = "OK"):
        return cls(code=200, message=message, trace_id=trace_id, data=data)

    @classmethod
    def fail(cls, code: int, message: str, trace_id: Optional[str] = None, errors: Optional[List[ComnError]] = None):
        return cls(code=code, message=message, trace_id=trace_id, errors=errors)
