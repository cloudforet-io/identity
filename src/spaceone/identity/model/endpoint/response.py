from typing import Union, List, Literal
from pydantic import BaseModel

__all__ = ["EndpointsResponse"]

State = Literal["ACTIVE", "INACTIVE"]


class EndpointResponse(BaseModel):
    name: Union[str, None] = None
    service: Union[str, None] = None
    endpoint: Union[str, None] = None
    internal_endpoint: Union[str, None] = None
    state: Union[State, None] = None
    version: Union[str, None] = None


class EndpointsResponse(BaseModel):
    results: List[EndpointResponse]
    total_count: int
