from typing import Union, Literal
from pydantic import BaseModel

__all__: ["TokenIssueRequest"]

AuthType = Literal["LOCAL", "EXTERNAL"]


class TokenIssueRequest(BaseModel):
    credentials: dict
    auth_type: AuthType
    timeout: Union[int, None] = None
    refresh_count: Union[int, None] = None
    verify_code: Union[str, None] = None
    domain_id: str
