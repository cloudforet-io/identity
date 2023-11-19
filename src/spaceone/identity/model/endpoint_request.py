from typing import Union
from pydantic import BaseModel

__all__ = ["EndpointSearchQueryRequest"]


class EndpointSearchQueryRequest(BaseModel):
    query: Union[dict, None] = None
    service: Union[str, None] = None
