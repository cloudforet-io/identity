from pydantic import BaseModel

__all__ = [
    "SystemResponse",
]


class SystemResponse(BaseModel):
    domain_id: str
    name: str
    system_token: str
