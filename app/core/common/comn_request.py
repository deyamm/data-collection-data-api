from typing import Generic, Optional, TypeVar, Dict, Any
from pydantic import Field, ConfigDict
from pydantic.generics import GenericModel
import time
import uuid

TReq = TypeVar("TReq")

class ComnRequest(GenericModel, Generic[TReq]):
    """
    通用请求包裹结构：
    - trace_id: 链路追踪（可由前端/网关传入，也可服务端生成）
    - ts: 请求时间戳（秒或毫秒都行，这里用秒）
    - data: 业务请求体
    - meta: 扩展字段（可选，放客户端信息、版本号等）
    """
    model_config = ConfigDict(extra="ignore")  # 忽略多余字段，提升兼容性

    trace_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    ts: int = Field(default_factory=lambda: int(time.time()))
    data: TReq
    meta: Optional[Dict[str, Any]] = None