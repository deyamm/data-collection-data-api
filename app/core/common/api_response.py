from typing import Generic, Optional, TypeVar
from pydantic import ConfigDict
from pydantic.generics import GenericModel

TRes = TypeVar("TRes")

class ApiResponse(GenericModel, Generic[TRes]):
    """
    通用响应结构：
    - code: 0 表示成功，非 0 表示失败
    - message: 信息描述
    - request_id: 回传链路追踪
    - data: 成功时业务数据
    """
    model_config = ConfigDict(extra="ignore")

    code: int = 0
    message: str = "Success"
    request_id: Optional[str] = None
    data: Optional[TRes] = None

    @classmethod
    def ok(cls, data: TRes = None, request_id: Optional[str] = None, message: str = "Success"):
        return cls(code=0, message=message, request_id=request_id, data=data)

    @classmethod
    def fail(cls, code: int, message: str, request_id: Optional[str] = None):
        return cls(code=code, message=message, request_id=request_id)
