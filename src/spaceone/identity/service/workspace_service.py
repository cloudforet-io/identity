import logging
from typing import Generator, Union
from spaceone.core.service import BaseService, transaction, convert_model
from spaceone.identity.model.workspace_request import *
from spaceone.identity.model.workspace_response import *

_LOGGER = logging.getLogger(__name__)


class WorkspaceService(BaseService):
    @transaction
    @convert_model
    def create(self, params: WorkspaceCreateRequest) -> Union[WorkspaceResponse, dict]:
        return {}

    @transaction
    @convert_model
    def update(self, params: WorkspaceUpdateRequest) -> Union[WorkspaceResponse, dict]:
        return {}

    @transaction
    @convert_model
    def delete(self, params: WorkspaceDeleteRequest) -> None:
        pass

    @transaction
    @convert_model
    def enable(self, params: WorkspaceEnableRequest) -> Union[WorkspaceResponse, dict]:
        return {}

    @transaction
    @convert_model
    def disable(
        self, params: WorkspaceDisableRequest
    ) -> Union[WorkspaceResponse, dict]:
        return {}

    @transaction
    @convert_model
    def get(self, params: WorkspaceGetRequest) -> Union[WorkspaceResponse, dict]:
        return {}

    @transaction
    @convert_model
    def list(
        self, params: WorkspaceSearchQueryRequest
    ) -> Union[WorkspacesResponse, dict]:
        return {}

    @transaction
    @convert_model
    def stat(self, params: WorkspaceStatQueryRequest) -> dict:
        return {}
