import logging
from typing import Union

from spaceone.core.service import (
    BaseService,
    transaction,
    convert_model,
    append_query_filter,
    append_keyword_filter,
)

from spaceone.identity.manager.role_binding_manager import RoleBindingManager
from spaceone.identity.manager.project_manager import ProjectManager
from spaceone.identity.manager.project_group_manager import ProjectGroupManager
from spaceone.identity.manager.workspace_manager import WorkspaceManager
from spaceone.identity.model.project.request import *
from spaceone.identity.model.project.response import *
from spaceone.identity.error.error_project import *

_LOGGER = logging.getLogger(__name__)


class ProjectService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rb_mgr = RoleBindingManager()
        self.project_mgr = ProjectManager()
        self.project_group_mgr = ProjectGroupManager()
        self.workspace_mgr = WorkspaceManager()

    @transaction(append_meta={"authorization.scope": "WORKSPACE"})
    @convert_model
    def create(self, params: ProjectCreateRequest) -> Union[ProjectResponse, dict]:
        """Create project
        Args:
            params (ProjectCreateRequest): {
                'name': 'str',              # required
                'project_type': 'str',      # required
                'tags': 'dict',
                'project_group_id': 'str',
                'workspace_id': 'str',      # required
                'domain_id': 'str'          # required
            }
        Returns:
            ProjectResponse:
        """

        if params.project_group_id:
            self.project_group_mgr.get_project_group(
                params.project_group_id, params.workspace_id, params.domain_id
            )

        project_vo = self.project_mgr.create_project(params.dict())

        return ProjectResponse(**project_vo.to_dict())

    @transaction(append_meta={"authorization.scope": "PROJECT"})
    @convert_model
    def update(self, params: ProjectUpdateRequest) -> Union[ProjectResponse, dict]:
        """Update project
        Args:
            params (ProjectUpdateRequest): {
                'project_id': 'str',        # required
                'name': 'str',
                'tags': 'dict',
                'workspace_id': 'str',      # required
                'domain_id': 'str'          # required
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
            params (ProjectUpdateProjectTypeRequest): {
                'project_id': 'str',        # required
                'project_type': 'str',      # required
                'workspace_id': 'str',      # required
                'domain_id': 'str'          # required
            }
        Returns:
            ProjectResponse:
        """

        project_vo = self.project_mgr.get_project(
            params.project_id, params.workspace_id, params.domain_id
        )

        params_dict = params.dict(exclude_unset=True)
        if params.project_type == 'PUBLIC':
            params_dict['users'] = []
            params_dict['user_groups'] = []

        project_vo = self.project_mgr.update_project_by_vo(
            params_dict, project_vo
        )

        return ProjectResponse(**project_vo.to_dict())

    @transaction(append_meta={"authorization.scope": "WORKSPACE"})
    @convert_model
    def change_project_group(
        self, params: ProjectChangeProjectGroupRequest
    ) -> Union[ProjectResponse, dict]:
        """Change project group
        Args:
            params (ProjectChangeProjectGroupRequest): {
                'project_id': 'str',            # required
                'project_group_id': 'str',      # required
                'workspace_id': 'str',          # required
                'domain_id': 'str'              # required
            }
        Returns:
            ProjectResponse:
        """

        if params.project_group_id:
            self.project_group_mgr.get_project_group(
                params.project_group_id, params.workspace_id, params.domain_id
            )

        project_vo = self.project_mgr.get_project(
            params.project_id, params.workspace_id, params.domain_id
        )
        project_vo = self.project_mgr.update_project_by_vo(
            params.dict(), project_vo
        )

        return ProjectResponse(**project_vo.to_dict())

    @transaction(append_meta={"authorization.scope": "WORKSPACE"})
    @convert_model
    def delete(self, params: ProjectDeleteRequest) -> None:
        """Delete project
        Args:
            params (ProjectDeleteRequest): {
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
        """Add users to project
        Args:
            params (ProjectAddUsersRequest): {
                'project_id': 'str',        # required
                'users': 'list',            # required
                'workspace_id': 'str',      # required
                'domain_id': 'str'          # required
            }
        Returns:
            ProjectResponse:
        """

        project_vo = self.project_mgr.get_project(
            params.project_id, params.workspace_id, params.domain_id
        )

        if project_vo.project_type == 'PUBLIC':
            raise ERROR_NOT_ALLOWED_ADD_USER_TO_PUBLIC_PROJECT()

        if len(params.users) > 0:
            self._check_exist_user(params.users, params.workspace_id, params.domain_id)
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
        """Remove users from project
        Args:
            params (ProjectRemoveUsersRequest): {
                'project_id': 'str',        # required
                'users': 'list',            # required
                'workspace_id': 'str',      # required
                'domain_id': 'str'          # required
            }
        Returns:
            ProjectResponse:
        """

        project_vo = self.project_mgr.get_project(
            project_id=params.project_id,
            workspace_id=params.workspace_id,
            domain_id=params.domain_id,
        )

        if len(params.users) > 0:
            self._check_exist_user(params.users, params.workspace_id, params.domain_id)
            users = project_vo.users or []
            params.users = list(set(users) - set(params.users))

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
            params (ProjectGetRequest): {
                'project_id': 'str',    # required
                'workspace_id': 'str',  # required
                'domain_id': 'str'      # required
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
            'project_type',
            "user_id",
            "user_group_id",
            "project_group_id",
            "workspace_id",
            "domain_id",
            "user_projects",
        ]
    )
    @append_keyword_filter(["project_id", "name"])
    @convert_model
    def list(self, params: ProjectSearchQueryRequest) -> Union[ProjectsResponse, dict]:
        """List projects
        Args:
            params (ProjectSearchQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.Query)',
                'project_id': 'str',
                'name': 'str',
                'project_type': 'str',
                'user_id': 'str',
                'user_group_id': 'str',
                'project_group_id': 'str',
                'workspace_id': 'str',
                'domain_id': 'str',         # required
                'user_projects': 'list'     # from meta
            }
        Returns:
            ProjectsResponse:
        """

        query = params.query or {}
        project_vos, total_count = self.project_mgr.list_projects(query)

        projects_info = [project_vo.to_dict() for project_vo in project_vos]
        return ProjectsResponse(results=projects_info, total_count=total_count)

    @transaction(append_meta={"authorization.scope": "PROJECT_READ"})
    @append_query_filter(['workspace_id', 'domain_id', 'user_projects'])
    @append_keyword_filter(["project_id", "name"])
    @convert_model
    def stat(self, params: ProjectStatQueryRequest) -> dict:
        """Stat workspaces
        Args:
            params (dict): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)', # required
                'workspace_id': 'str',
                'domain_id': 'str',         # required
                'user_projects': 'list'     # from meta
            }
        Returns:
            dict: {
                'results': 'list',
                'total_count': 'int'
            }
        """

        query = params.query or {}
        return self.project_mgr.stat_projects(query)

    def _check_exist_user(self, users, workspace_id, domain_id):
        rb_vos = self.rb_mgr.filter_role_bindings(
            user_id=users,
            workspace_id=[workspace_id, '*'],
            role_type=['WORKSPACE_OWNER', 'WORKSPACE_MEMBER'],
            domain_id=domain_id
        )
        existing_users = list(set([rb.user_id for rb in rb_vos]))
        not_existing_users = list(set(users) - set(existing_users))
        for user_id in not_existing_users:
            raise ERROR_USER_NOT_EXIST_IN_WORKSPACE(user_id=user_id, workspace_id=workspace_id)
