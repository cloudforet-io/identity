from pydantic import BaseModel

__all__ = ["TokenResponse"]


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
