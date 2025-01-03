from typing import Union, Literal
from pydantic import BaseModel

__all__ = ["EndpointSearchQueryRequest"]

EndpointType = Literal["PUBLIC", "INTERNAL"]


class EndpointSearchQueryRequest(BaseModel):
    query: Union[dict, None] = None
    service: Union[str, None] = None
    endpoint_type: Union[EndpointType, None] = None
