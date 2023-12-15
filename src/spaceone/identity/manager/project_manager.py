import logging
from typing import Tuple, List
from mongoengine import QuerySet

from spaceone.core import cache
from spaceone.core.manager import BaseManager

from spaceone.identity.model.project.database import Project
from spaceone.identity.error.error_project import *
from spaceone.identity.manager.service_account_manager import ServiceAccountManager

_LOGGER = logging.getLogger(__name__)


class ProjectManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_model = Project

    def create_project(self, params: dict) -> Project:
        def _rollback(vo: Project):
            _LOGGER.info(
                f"[create_project._rollback] Delete project: {vo.name} ({vo.project_id})"
            )
            vo.delete()

        project_vo = self.project_model.create(params)
        self.transaction.add_rollback(_rollback, project_vo)

        return project_vo

    def update_project_by_vo(self, params: dict, project_vo: Project) -> Project:
        def _rollback(old_data):
            _LOGGER.info(
                f'[update_project._rollback] Revert Data: {old_data["name"]} ({old_data["project_id"]})'
            )
            project_vo.update(old_data)

        self.transaction.add_rollback(_rollback, project_vo.to_dict())

        return project_vo.update(params)

    @staticmethod
    def delete_project_by_vo(project_vo: Project) -> None:
        service_account_mgr = ServiceAccountManager()
        service_account_vos = service_account_mgr.filter_service_accounts(
            project_id=project_vo.project_id
        )
        for service_account_vo in service_account_vos:
            raise ERROR_RELATED_SERVICE_ACCOUNT_EXIST(
                service_account_id=service_account_vo.service_account_id
            )

        project_vo.delete()

    def get_project(
        self,
        project_id: str,
        domain_id: str,
        workspace_id: str = None,
        user_projects: List[str] = None,
    ) -> Project:
        if user_projects and project_id not in user_projects:
            raise ERROR_PERMISSION_DENIED()

        conditions = {
            "project_id": project_id,
            "domain_id": domain_id,
        }

        if workspace_id:
            conditions.update({"workspace_id": workspace_id})

        return self.project_model.get(**conditions)

    def filter_projects(self, **conditions) -> QuerySet:
        return self.project_model.filter(**conditions)

    def list_projects(self, query: dict) -> Tuple[QuerySet, int]:
        return self.project_model.query(**query)

    def stat_projects(self, query: dict) -> dict:
        return self.project_model.stat(**query)
