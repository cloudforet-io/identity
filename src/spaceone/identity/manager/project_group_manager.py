import logging
from typing import Tuple
from mongoengine import QuerySet
from spaceone.core.manager import BaseManager

from spaceone.identity.error.error_project_group import *
from spaceone.identity.manager.project_manager import ProjectManager
from spaceone.identity.model.project_group.database import ProjectGroup

_LOGGER = logging.getLogger(__name__)


class ProjectGroupManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_group_model = ProjectGroup

    def create_project_group(self, params: dict) -> ProjectGroup:
        def _rollback(vo: ProjectGroup):
            _LOGGER.info(
                f"[create_project_group._rollback] Delete project group: {vo.name} ({vo.project_group_id})"
            )
            vo.delete()

        project_group_vo = self.project_group_model.create(params)
        self.transaction.add_rollback(_rollback, project_group_vo)

        return project_group_vo

    def update_project_group_by_vo(self, params: dict, project_group_vo: ProjectGroup) -> ProjectGroup:
        def _rollback(old_data):
            _LOGGER.info(
                f'[update_project_group._rollback] Revert Data: {old_data["name"]} ({old_data["project_group_id"]})'
            )
            project_group_vo.update(old_data)

        self.transaction.add_rollback(_rollback, project_group_vo.to_dict())

        return project_group_vo.update(params)

    def delete_project_group_by_vo(self, project_group_vo: ProjectGroup) -> None:
        project_mgr = ProjectManager()
        project_vos = project_mgr.filter_projects(project_group_id=project_group_vo.project_group_id)
        for project_vo in project_vos:
            raise ERROR_RELATED_PROJECT_EXIST(project_id=project_vo.project_id)

        child_vos = self.filter_project_groups(parent_group_id=project_group_vo.project_group_id)
        for child_vo in child_vos:
            raise ERROR_RELATED_PROJECT_GROUP_EXIST(project_group_id=child_vo.project_group_id)

        project_group_vo.delete()

    def get_project_group(
        self, project_group_id: str, workspace_id: str, domain_id: str
    ) -> ProjectGroup:
        conditions = {
            "project_group_id": project_group_id,
            "workspace_id": workspace_id,
            "domain_id": domain_id,
        }

        return self.project_group_model.get(**conditions)

    def filter_project_groups(self, **conditions) -> QuerySet:
        return self.project_group_model.filter(**conditions)

    def list_project_groups(self, query: dict) -> Tuple[QuerySet, int]:
        return self.project_group_model.query(**query)

    def stat_project_groups(self, query: dict) -> dict:
        return self.project_group_model.stat(**query)
