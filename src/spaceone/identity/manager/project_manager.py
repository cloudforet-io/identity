import logging
from typing import Tuple

from spaceone.core import cache
from spaceone.core.manager import BaseManager

from spaceone.identity.model.project.database import Project

_LOGGER = logging.getLogger(__name__)


class ProjectManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_model = Project

    def create_project(self, params: dict) -> Project:
        def _rollback(vo: Project):
            _LOGGER.info(
                f"[create_project._rollback] Delete project : {vo.name} ({vo.project_id}) ({vo.workspace_id}) ({vo.domain_id})"
            )
            vo.delete()

        project_vo = self.project_model.create(params)
        self.transaction.add_rollback(_rollback, project_vo)

        return project_vo

    def update_project_by_vo(self, params: dict, project_vo: Project) -> Project:
        def _rollback(old_data):
            _LOGGER.info(
                f'[update_project._rollback] Revert Data : {old_data["name"]} ({old_data["project_id"]}, {old_data["domain_id"]})'
            )
            project_vo.update(old_data)

        self.transaction.add_rollback(_rollback, project_vo.to_dict())

        return project_vo.update(params)

    @staticmethod
    def delete_project_by_vo(project_vo: Project) -> None:
        project_vo.delete()

        cache.delete_pattern(
            f"project-state:{project_vo.domain_id}:{project_vo.workspace_id}:{project_vo.project_id}"
        )

    #
    # def enable_workspace(self, workspace_vo: Workspace) -> Workspace:
    #     def _rollback(old_data):
    #         _LOGGER.info(
    #             f'[enable_workspace._rollback] Revert Data : {old_data["name"]} ({old_data["workspace_id"]})'
    #         )
    #         workspace_vo.update(old_data)
    #
    #     if workspace_vo.state != "ENABLED":
    #         self.transaction.add_rollback(_rollback, workspace_vo.to_dict())
    #         workspace_vo.update({"state": "ENABLED"})
    #
    #         cache.delete_pattern(
    #             f"workspace-state:{workspace_vo.domain_id}:{workspace_vo.workspace_id}"
    #         )
    #
    #     return workspace_vo
    #
    # def disable_workspace(self, workspace_vo: Workspace) -> Workspace:
    #     def _rollback(old_data):
    #         _LOGGER.info(
    #             f'[disable_workspace._rollback] Revert Data : {old_data["name"]} ({old_data["workspace_id"]})'
    #         )
    #         workspace_vo.update(old_data)
    #
    #     if workspace_vo.state != "DISABLED":
    #         self.transaction.add_rollback(_rollback, workspace_vo.to_dict())
    #         workspace_vo.update({"state": "DISABLED"})
    #
    #         cache.delete_pattern(
    #             f"workspace-state:{workspace_vo.domain_id}:{workspace_vo.workspace_id}"
    #         )
    #
    #     return workspace_vo
    #
    def get_project(self, project_id, workspace_id, domain_id) -> Project:
        return self.project_model.get(
            project_id=project_id, workspace_id=workspace_id, domain_id=domain_id
        )

    def list_projects(self, query: dict) -> Tuple[list, int]:
        return self.project_model.query(**query)
