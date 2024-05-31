from typing import Union

from pydantic import BaseModel


class PluginResponse(BaseModel):
    metadata: dict


class UserResponse(BaseModel):
    state: Union[str, None] = None
    user_id: Union[str, None] = None
    name: Union[str, None] = None
    email: Union[str, None] = None
    mobile: Union[str, None] = None
    group: Union[str, None] = None
