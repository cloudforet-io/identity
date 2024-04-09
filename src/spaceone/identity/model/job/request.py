from typing import Union, Literal
from pydantic import BaseModel

__all__ = [
    "JobDeleteRequest",
    "JobGetRequest",
    "JobSearchQueryRequest",
    "JobStatQueryRequest",
]


class JobDeleteRequest(BaseModel):
    job_id: str
    workspace_id: Union[str, None] = None
    domain_id: str


class JobGetRequest(BaseModel):
    job_id: str
    workspace_id: Union[list, str, None] = None
    domain_id: str


class JobSearchQueryRequest(BaseModel):
    query: Union[dict, None] = None
    job_id: Union[str, None] = None
    trusted_account_id: Union[str, None] = None
    plugin_id: Union[str, None] = None
    workspace_id: Union[list, str, None] = None
    domain_id: str


class JobStatQueryRequest(BaseModel):
    query: dict
    workspace_id: Union[str, None] = None
    domain_id: str
