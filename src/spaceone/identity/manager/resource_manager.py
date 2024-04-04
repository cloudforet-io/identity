from typing import Union

from spaceone.core.manager import BaseManager

from spaceone.identity.error.custom import ERROR_MANAGED_RESOURCE_CAN_NOT_BE_MODIFIED
from spaceone.identity.model.service_account.database import ServiceAccount
from spaceone.identity.model.trusted_account.database import TrustedAccount
from spaceone.identity.model.project.database import Project
from spaceone.identity.model.project_group.database import ProjectGroup
from spaceone.identity.model.workspace.database import Workspace


class ResourceManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trusted_account_model = TrustedAccount

    def check_is_managed_resource(
        self,
        resource_vo: Union[ServiceAccount, Project, ProjectGroup, Workspace],
    ) -> None:
        if resource_vo.is_managed:
            trusted_account_vo = self.trusted_account_model.get(
                trusted_account_id=resource_vo.trusted_account_id,
                domain_id=resource_vo.domain_id,
            )
            if trusted_account_vo.schedule.get("state") != "ENABLED":
                raise ERROR_MANAGED_RESOURCE_CAN_NOT_BE_MODIFIED()
