from typing import Union

from spaceone.core.manager import BaseManager

from spaceone.identity.error.custom import ERROR_MANAGED_RESOURCE_CAN_NOT_BE_MODIFIED
from spaceone.identity.model.service_account.database import ServiceAccount
from spaceone.identity.model.project.database import Project
from spaceone.identity.model.project_group.database import ProjectGroup
from spaceone.identity.model.workspace.database import Workspace


class ResourceManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    @staticmethod
    def check_is_managed_resource(resource_vo: Union[ServiceAccount, Project, ProjectGroup, Workspace]) -> None:
        if resource_vo.is_managed:
            raise ERROR_MANAGED_RESOURCE_CAN_NOT_BE_MODIFIED()
