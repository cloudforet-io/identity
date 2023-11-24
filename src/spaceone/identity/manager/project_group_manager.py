import logging
from spaceone.core import cache
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
        def _rollback(project_group_vo: ProjectGroup):
            _LOGGER.info(
                f"[create_project_group._rollback] Delete project group : {project_group_vo.name} ({project_group_vo.project_group_id})"
            )
            project_group_vo.delete()

        project_group_vo = self.project_group_model.create(params)
        self.transaction.add_rollback(_rollback, project_group_vo)

        # if params.get("parent_group_id") is not None:
        #     parent_group_id = params["parent_group_id"]
        #     cache.delete_pattern(f"project-path:*{parent_group_id}*")
        #     self._delete_parent_project_group_cache(parent_group_id)

        return project_group_vo

    def update_project_group(self, params):
        project_group_vo = self.get_project_group(
            params["project_group_id"], params["domain_id"]
        )
        return self.update_project_group_by_vo(params, project_group_vo)

    def update_project_group_by_vo(self, params, project_group_vo):
        def _rollback(old_data):
            _LOGGER.info(
                f'[update_project_group._rollback] Revert Data : {old_data["name"]} ({old_data["project_group_id"]})'
            )
            project_group_vo.update(old_data)

        self.transaction.add_rollback(_rollback, project_group_vo.to_dict())

        if params.get("parent_project_group") is not None:
            parent_project_group_id = params["parent_project_group_id"]
            project_group_id = project_group_vo.project_group_id

            if parent_project_group_id is not None:
                cache.delete_pattern(f"project-path:*{parent_project_group_id}*")
                cache.delete_pattern(f"role-bindings:*{parent_project_group_id}*")
                cache.delete_pattern(f"user-scopes:*{parent_project_group_id}*")
                # self._delete_parent_project_group_cache(params["parent_project_group"])

            cache.delete_pattern(f"project-path:*{project_group_id}*")
            cache.delete_pattern(f"role-bindings:*{project_group_id}*")
            cache.delete_pattern(f"user-scopes:*{project_group_id}*")
            # self._delete_parent_project_group_cache(project_group_vo)

        return project_group_vo.update(params)

    def delete_project_group_by_vo(self, project_group_vo: ProjectGroup):
        conditions = {
            "parent_group_id": project_group_vo.project_group_id,
            "workspace_id": project_group_vo.workspace_id,
            "domain_id": project_group_vo.domain_id,
        }
        project_group_vos = self.filter_project_groups(**conditions)
        for pg_vo in project_group_vos:
            raise ERROR_PROJECT_GROUP_USED_IN_CHILD_PROJECT_GORUP(
                project_group_id=pg_vo.project_group_id
            )
        project_mgr = ProjectManager()
        conditions = {
            "project_group_id": project_group_vo.project_group_id,
            "workspace_id": project_group_vo.workspace_id,
            "domain_id": project_group_vo.domain_id,
        }
        project_vos = project_mgr.filter_projects(**conditions)
        for project_vo in project_vos:
            raise ERROR_PROJECT_GROUP_USED_IN_PROJECT(
                project_group_id=project_vo.project_group_id
            )

        cache.delete_pattern(f"project-path:*{project_group_vo.project_group_id}*")
        cache.delete_pattern(f"role-bindings:*{project_group_vo.project_group_id}*")
        cache.delete_pattern(f"role-bindings:*:")
        cache.delete_pattern(f"user-scopes:*{project_group_vo.project_group_id}*")
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

    def get_parent_project_group(
        self, project_group_id: str, workspace_id: str, domain_id: str
    ):
        conditions = {
            "project_group_id": project_group_id,
            "workspace_id": workspace_id,
            "domain_id": domain_id,
        }

        return self.project_group_model.get(**conditions)

    def filter_project_groups(self, **conditions):
        return self.project_group_model.filter(**conditions)

    def list_project_groups(self, query):
        return self.project_group_model.query(**query)

    def stat_project_groups(self, query):
        return self.project_group_model.stat(**query)
