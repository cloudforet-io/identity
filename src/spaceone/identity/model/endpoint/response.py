from typing import Union, List
from pydantic import BaseModel

__all__ = ["EndpointsResponse"]


class EndpointResponse(BaseModel):
    name: Union[str, None] = None
    service: Union[str, None] = None
    endpoint: Union[str, None] = None
    state: Union[str, None] = None
    version: Union[str, None] = None


class EndpointsResponse(BaseModel):
    results: List[EndpointResponse]
    total_count: int
