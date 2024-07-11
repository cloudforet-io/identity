import logging
from typing import Union

from spaceone.core.service import *
from spaceone.core.service.utils import *

from spaceone.identity.manager.role_binding_manager import RoleBindingManager
from spaceone.identity.manager.project_manager import ProjectManager
from spaceone.identity.manager.project_group_manager import ProjectGroupManager
from spaceone.identity.manager.resource_manager import ResourceManager
from spaceone.identity.manager.workspace_manager import WorkspaceManager
from spaceone.identity.manager.workspace_user_manager import WorkspaceUserManager
from spaceone.identity.model.project.request import *
from spaceone.identity.model.project.response import *
from spaceone.identity.error.error_project import *

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class ProjectService(BaseService):
    resource = "Project"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rb_mgr = RoleBindingManager()
        self.project_mgr = ProjectManager()
        self.project_group_mgr = ProjectGroupManager()
        self.resource_mgr = ResourceManager()
        self.workspace_mgr = WorkspaceManager()

    @transaction(permission="identity:Project.write", role_types=["WORKSPACE_OWNER"])
    @convert_model
    def create(self, params: ProjectCreateRequest) -> Union[ProjectResponse, dict]:
        """Create project
        Args:
            params (ProjectCreateRequest): {
                'name': 'str',                  # required
                'project_type': 'str',          # required
                'tags': 'dict',
                'project_group_id': 'str',
                'workspace_id': 'str',          # injected from auth (required)
                'domain_id': 'str',             # injected from auth (required)
            }
        Returns:
        """

        if params.project_group_id:
            self.project_group_mgr.get_project_group(
                params.project_group_id,
                params.domain_id,
                params.workspace_id,
            )

        params_data = params.dict()
        params_data["created_by"] = self.transaction.get_meta("authorization.user_id")

        project_vo = self.project_mgr.create_project(params_data)

        return ProjectResponse(**project_vo.to_dict())

    @transaction(
        permission="identity:Project.write",
        role_types=["WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @convert_model
    def update(self, params: ProjectUpdateRequest) -> Union[ProjectResponse, dict]:
        """Update project
        Args:
            params (ProjectUpdateRequest): {
                'project_id': 'str',        # required
                'name': 'str',
                'tags': 'dict',
                'workspace_id': 'str',      # injected from auth (required)
                'domain_id': 'str',         # injected from auth (required)
                'user_projects': 'list'     # injected from auth
            }
        Returns:
            ProjectResponse:
        """

        project_vo = self.project_mgr.get_project(
            params.project_id,
            params.domain_id,
            params.workspace_id,
            params.user_projects,
        )

        # Check is managed resource
        self.resource_mgr.check_is_managed_resource_by_trusted_account(project_vo)

        project_vo = self.project_mgr.update_project_by_vo(
            params.dict(exclude_unset=True), project_vo
        )

        return ProjectResponse(**project_vo.to_dict())

    @transaction(permission="identity:Project.write", role_types=["WORKSPACE_OWNER"])
    @convert_model
    def update_project_type(
        self, params: ProjectUpdateProjectTypeRequest
    ) -> Union[ProjectResponse, dict]:
        """Update project type
        Args:
            params (ProjectUpdateProjectTypeRequest): {
                'project_id': 'str',        # required
                'project_type': 'str',      # required
                'workspace_id': 'str',      # injected from auth (required)
                'domain_id': 'str'          # injected from auth (required)
            }
        Returns:
            ProjectResponse:
        """

        project_vo = self.project_mgr.get_project(
            params.project_id, params.domain_id, params.workspace_id
        )

        # Check is managed resource
        self.resource_mgr.check_is_managed_resource_by_trusted_account(project_vo)

        params_dict = params.dict(exclude_unset=True)
        if params.project_type == "PUBLIC":
            params_dict["users"] = []

        project_vo = self.project_mgr.update_project_by_vo(params_dict, project_vo)

        return ProjectResponse(**project_vo.to_dict())

    @transaction(permission="identity:Project.write", role_types=["WORKSPACE_OWNER"])
    @convert_model
    def change_project_group(
        self, params: ProjectChangeProjectGroupRequest
    ) -> Union[ProjectResponse, dict]:
        """Change project group
        Args:
            params (ProjectChangeProjectGroupRequest): {
                'project_id': 'str',            # required
                'project_group_id': 'str',      # required
                'workspace_id': 'str',          # injected from auth (required)
                'domain_id': 'str'              # injected from auth (required)
            }
        Returns:
            ProjectResponse:
        """

        if params.project_group_id:
            self.project_group_mgr.get_project_group(
                params.project_group_id,
                params.domain_id,
                params.workspace_id,
            )

        project_vo = self.project_mgr.get_project(
            params.project_id,
            params.domain_id,
            params.workspace_id,
        )

        # Check is managed resource
        self.resource_mgr.check_is_managed_resource_by_trusted_account(project_vo)

        project_vo = self.project_mgr.update_project_by_vo(params.dict(), project_vo)

        return ProjectResponse(**project_vo.to_dict())

    @transaction(permission="identity:Project.write", role_types=["WORKSPACE_OWNER"])
    @convert_model
    def delete(self, params: ProjectDeleteRequest) -> None:
        """Delete project
        Args:
            params (ProjectDeleteRequest): {
                'project_id': 'str',        # required
                'workspace_id': 'str',      # injected from auth (required)
                'domain_id': 'str'          # injected from auth (required)
            }
        Returns:
            None:
        """

        project_vo = self.project_mgr.get_project(
            params.project_id,
            params.domain_id,
            params.workspace_id,
        )

        # Check is managed resource
        self.resource_mgr.check_is_managed_resource_by_trusted_account(project_vo)

        self.project_mgr.delete_project_by_vo(project_vo)

    @transaction(
        permission="identity:Project.write",
        role_types=["WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @convert_model
    def add_users(self, params: ProjectAddUsersRequest) -> Union[ProjectResponse, dict]:
        """Add users to project
        Args:
            params (ProjectAddUsersRequest): {
                'project_id': 'str',        # required
                'users': 'list',            # required
                'workspace_id': 'str',      # injected from auth (required)
                'domain_id': 'str',         # injected from auth (required)
                'user_projects': 'list'     # injected from auth
            }
        Returns:
            ProjectResponse:
        """

        project_vo = self.project_mgr.get_project(
            params.project_id,
            params.domain_id,
            params.workspace_id,
            params.user_projects,
        )

        if project_vo.project_type == "PUBLIC":
            raise ERROR_NOT_ALLOWED_ADD_USER_TO_PUBLIC_PROJECT()

        if len(params.users) > 0:
            workspace_user_mgr = WorkspaceUserManager()
            workspace_user_mgr.check_workspace_users(
                params.users, params.workspace_id, params.domain_id
            )

            users = project_vo.users or []
            users.extend(params.users)
            params.users = list(set(users))

            project_vo = self.project_mgr.update_project_by_vo(
                params.dict(exclude_unset=True), project_vo
            )

        return ProjectResponse(**project_vo.to_dict())

    @transaction(
        permission="identity:Project.write",
        role_types=["WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @convert_model
    def remove_users(
        self, params: ProjectRemoveUsersRequest
    ) -> Union[ProjectResponse, dict]:
        """Remove users from project
        Args:
            params (ProjectRemoveUsersRequest): {
                'project_id': 'str',        # required
                'users': 'list',            # required
                'workspace_id': 'str',      # injected from auth (required)
                'domain_id': 'str',         # injected from auth (required)
                'user_projects': 'list'     # injected from auth
            }
        Returns:
            ProjectResponse:
        """

        project_vo = self.project_mgr.get_project(
            params.project_id,
            params.domain_id,
            params.workspace_id,
            params.user_projects,
        )

        if len(params.users) > 0:
            workspace_user_mgr = WorkspaceUserManager()
            workspace_user_mgr.check_workspace_users(
                params.users, params.workspace_id, params.domain_id
            )

            users = project_vo.users or []
            params.users = list(set(users) - set(params.users))

        project_vo = self.project_mgr.update_project_by_vo(
            params.dict(exclude_unset=True), project_vo
        )

        return ProjectResponse(**project_vo.to_dict())

    @transaction(
        permission="identity:Project.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @convert_model
    def get(self, params: ProjectGetRequest) -> Union[ProjectResponse, dict]:
        """Get project
        Args:
            params (ProjectGetRequest): {
                'project_id': 'str',    # required
                'workspace_id': 'str',  # injected from auth
                'domain_id': 'str',     # injected from auth (required)
                'user_projects': 'list' # injected from auth
            }
        Returns:
            ProjectResponse:
        """

        project_vo = self.project_mgr.get_project(
            params.project_id,
            params.domain_id,
            params.workspace_id,
            params.user_projects,
        )

        return ProjectResponse(**project_vo.to_dict())

    @transaction(
        permission="identity:Project.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @append_query_filter(
        [
            "project_id",
            "name",
            "project_type",
            "created_by",
            "user_id",
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
                'created_by': 'str',
                'include_children': 'bool',
                'user_id': 'str',
                'project_group_id': 'str',
                'workspace_id': 'str',      # injected from auth
                'domain_id': 'str',         # injected from auth (required)
                'user_projects': 'list'     # injected from auth
            }
        Returns:
            ProjectsResponse:
        """

        include_children = params.include_children or False
        project_group_id = params.project_group_id
        query = params.query or {}

        if include_children and project_group_id:
            project_group_ids = self._get_child_group_ids(project_group_id)
            project_group_ids.append(project_group_id)
            query["filter"].append(
                {"k": "project_group_id", "v": project_group_ids, "o": "in"}
            )
        elif project_group_id:
            query["filter"].append(
                {"k": "project_group_id", "v": project_group_id, "o": "eq"}
            )

        project_vos, total_count = self.project_mgr.list_projects(query)

        projects_info = [project_vo.to_dict() for project_vo in project_vos]
        return ProjectsResponse(results=projects_info, total_count=total_count)

    @transaction(
        permission="identity:Project.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @append_query_filter(["workspace_id", "domain_id", "user_projects"])
    @append_keyword_filter(["project_id", "name"])
    @convert_model
    def stat(self, params: ProjectStatQueryRequest) -> dict:
        """Stat workspaces
        Args:
            params (dict): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)', # required
                'workspace_id': 'str',      # injected from auth
                'domain_id': 'str',         # injected from auth (required)
                'user_projects': 'list'     # injected from auth
            }
        Returns:
            dict: {
                'results': 'list',
                'total_count': 'int'
            }
        """

        query = params.query or {}
        return self.project_mgr.stat_projects(query)

    def _get_child_group_ids(self, project_group_id: str) -> list:
        pg_vos = self.project_group_mgr.filter_project_groups(
            parent_group_id=project_group_id
        )
        project_group_ids = [pg.project_group_id for pg in pg_vos]

        for pg in pg_vos:
            project_group_ids.extend(self._get_child_group_ids(pg.project_group_id))

        return project_group_ids
