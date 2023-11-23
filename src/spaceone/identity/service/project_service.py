import logging
from typing import Union

from spaceone.core.service import (
    BaseService,
    transaction,
    convert_model,
    append_query_filter,
    append_keyword_filter,
)

from spaceone.identity.manager.user_manager import UserManager
from spaceone.identity.manager.project_manager import ProjectManager
from spaceone.identity.manager.workspace_manager import WorkspaceManager
from spaceone.identity.model.project.request import *
from spaceone.identity.model.project.response import *

_LOGGER = logging.getLogger(__name__)


class ProjectService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_mgr = UserManager()
        self.project_mgr = ProjectManager()
        self.workspace_mgr = WorkspaceManager()

    @transaction(append_meta={"authorization.scope": "WORKSPACE"})
    @convert_model
    def create(self, params: ProjectCreateRequest) -> Union[ProjectResponse, dict]:
        """Create project
        Args:
            params (dict): {
                'name': 'str', # required
                'project_type': 'str',
                'tags': 'dict',
                'project_group_id': 'str',
                'workspace_id': 'str', # required
                'domain_id': 'str' # required
            }
        Returns:
            ProjectResponse:
        """

        project_vo = self.project_mgr.create_project(params.dict())

        return ProjectResponse(**project_vo.to_dict())

    @transaction(append_meta={"authorization.scope": "PROJECT"})
    @convert_model
    def update(self, params: ProjectUpdateRequest) -> Union[ProjectResponse, dict]:
        """Update project
        Args:
            params (dict): {
                'project_id': 'str', # required
                'name': 'str',
                'tags': 'dict',
                'workspace_id': 'str', # required
                'domain_id': 'str' # required
            }
        Returns:
            ProjectResponse:
        """

        project_vo = self.project_mgr.get_project(
            params.project_id, params.workspace_id, params.domain_id
        )
        project_vo = self.project_mgr.update_project_by_vo(
            params.dict(exclude_unset=True), project_vo
        )

        return ProjectResponse(**project_vo.to_dict())

    @transaction(append_meta={"authorization.scope": "WORKSPACE"})
    @convert_model
    def update_project_type(
        self, params: ProjectUpdateProjectTypeRequest
    ) -> Union[ProjectResponse, dict]:
        """Update project type
        Args:
            params (dict): {
                'project_id': 'str', # required
                'project_type': 'str', # required
                'workspace_id': 'str', # required
                'domain_id': 'str' # required
            }
        Returns:
            ProjectResponse:
        """

        project_vo = self.project_mgr.get_project(
            params.project_id, params.workspace_id, params.domain_id
        )
        project_vo = self.project_mgr.update_project_by_vo(
            params.dict(exclude_unset=True), project_vo
        )

        return ProjectResponse(**project_vo.to_dict())

    @transaction(append_meta={"authorization.scope": "WORKSPACE"})
    @convert_model
    def change_project_group(
        self, params: ProjectChangeProjectGroupRequest
    ) -> Union[ProjectResponse, dict]:
        """Change project group
        Args:
            params (dict): {
                'project_id': 'str', # required
                'project_group_id': 'str', # required
                'workspace_id': 'str', # required
                'domain_id': 'str' # required
            }
        Returns:
            ProjectResponse:
        """
        project_vo = self.project_mgr.get_project(
            params.project_id, params.workspace_id, params.domain_id
        )
        project_vo = self.project_mgr.update_project_by_vo(
            params.dict(exclude_unset=True), project_vo
        )
        return ProjectResponse(**project_vo.to_dict())

    @transaction(append_meta={"authorization.scope": "WORKSPACE"})
    @convert_model
    def delete(self, params: ProjectDeleteRequest) -> None:
        """Delete project
        Args:
            params (dict): {
                'project_id': 'str', # required
                'workspace_id': 'str', # required
                'domain_id': 'str' # required
            }
        Returns:
            None:
        """
        project_vo = self.project_mgr.get_project(
            params.project_id, params.workspace_id, params.domain_id
        )
        self.project_mgr.delete_project_by_vo(project_vo)

    @transaction(append_meta={"authorization.scope": "PROJECT"})
    @convert_model
    def add_users(self, params: ProjectAddUsersRequest) -> Union[ProjectResponse, dict]:
        project_vo = self.project_mgr.get_project(
            params.project_id, params.workspace_id, params.domain_id
        )

        if len(params.users) > 0:
            self._check_exist_user(params.users, params.domain_id)
            users = project_vo.users or []
            users.extend(params.users)
            params.users = list(set(users))

            project_vo = self.project_mgr.update_project_by_vo(
                params.dict(exclude_unset=True), project_vo
            )

        return ProjectResponse(**project_vo.to_dict())

    @transaction(append_meta={"authorization.scope": "PROJECT"})
    @convert_model
    def remove_users(
        self, params: ProjectRemoveUsersRequest
    ) -> Union[ProjectResponse, dict]:
        project_vo = self.project_mgr.get_project(
            project_id=params.project_id,
            workspace_id=params.workspace_id,
            domain_id=params.domain_id,
        )

        params.users = list(set(project_vo.users) - set(params.users))
        project_vo = self.project_mgr.update_project_by_vo(
            params.dict(exclude_unset=True), project_vo
        )

        return ProjectResponse(**project_vo.to_dict())

    @transaction(append_meta={"authorization.scope": "PROJECT"})
    @convert_model
    def add_user_groups(
        self, params: ProjectAddUserGroupsRequest
    ) -> Union[ProjectResponse, dict]:
        return {}

    @transaction(append_meta={"authorization.scope": "PROJECT"})
    @convert_model
    def remove_user_groups(
        self, params: ProjectRemoveUserGroupsRequest
    ) -> Union[ProjectResponse, dict]:
        return {}

    @transaction(append_meta={"authorization.scope": "PROJECT_READ"})
    @convert_model
    def get(self, params: ProjectGetRequest) -> Union[ProjectResponse, dict]:
        """Get project
        Args:
            params (dict): {
                'project_id': 'str', # required
                'workspace_id': 'str', # required
                'domain_id': 'str' # required
            }
        Returns:
            ProjectResponse:
        """

        project_vo = self.project_mgr.get_project(
            params.project_id, params.workspace_id, params.domain_id
        )
        return ProjectResponse(**project_vo.to_dict())

    @transaction(append_meta={"authorization.scope": "PROJECT_READ"})
    @append_query_filter(
        [
            "project_id",
            "name",
            "user_id",
            "user_group_id",
            "project_group_id",
            "workspace_id",
            "domain_id",
        ]
    )
    @append_keyword_filter(["project_id", "name"])
    @convert_model
    def list(self, params: ProjectSearchQueryRequest) -> Union[ProjectsResponse, dict]:
        """List projects
        Args:
            params (dict): {
                'query': 'dict (spaceone.api.core.v1.Query)',
                'project_id': 'str',
                'name': 'str',
                'user_id': 'str',
                'user_group_id': 'str',
                'project_group_id': 'str',
                'workspace_id': 'str',
                'domain_id': 'str' # required
            }
        Returns:
            ProjectsResponse:
        """
        query = params.query or {}
        project_vos, total_count = self.project_mgr.list_projects(query)
        projects_info = [project_vo.to_dict() for project_vo in project_vos]
        return ProjectsResponse(results=projects_info, total_count=total_count)

    @transaction(append_meta={"authorization.scope": "PROJECT_READ"})
    @convert_model
    def stat(self, params: ProjectStatQueryRequest) -> dict:
        return {}

    def _check_exist_user(self, users, domain_id):
        _filter = [
            {"k": "user_id", "v": users, "o": "in"},
            {"k": "domain_id", "v": domain_id, "o": "eq"},
        ]
        self.user_mgr.list_users({"filter": _filter})
