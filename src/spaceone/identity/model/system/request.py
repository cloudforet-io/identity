from pydantic import BaseModel
from spaceone.identity.model.domain.request import AdminUser

__all__ = [
    "SystemInitRequest",
]


class SystemInitRequest(BaseModel):
    admin: AdminUser
    force: bool = False
