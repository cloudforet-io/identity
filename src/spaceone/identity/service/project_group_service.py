import logging
from typing import Union, List

from mongoengine import QuerySet
from spaceone.core.service import *
from spaceone.core.service.utils import *

from spaceone.identity.error.error_project_group import *
from spaceone.identity.manager.project_group_manager import ProjectGroupManager
from spaceone.identity.manager.resource_manager import ResourceManager
from spaceone.identity.manager.workspace_user_manager import WorkspaceUserManager
from spaceone.identity.model import ProjectGroup
from spaceone.identity.model.project_group.request import *
from spaceone.identity.model.project_group.response import *

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class ProjectGroupService(BaseService):
    resource = "ProjectGroup"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_group_mgr = ProjectGroupManager()
        self.resource_mgr = ResourceManager()

    @transaction(
        permission="identity:ProjectGroup.write", role_types=["WORKSPACE_OWNER"]
    )
    @convert_model
    def create(
        self, params: ProjectGroupCreateRequest
    ) -> Union[ProjectGroupResponse, dict]:
        """Create project group

        Args:
            params (ProjectGroupCreateRequest): {
                'name': 'str',              # required
                'tags': 'dict',
                'parent_group_id': 'str',
                'workspace_id': 'str',      # injected from auth (required)
                'domain_id': 'str'          # injected from auth (required)
            }
        Returns:
            ProjectGroupResponse:
        """

        if params.parent_group_id:
            self.project_group_mgr.get_project_group(
                params.parent_group_id,
                params.domain_id,
                params.workspace_id,
            )

        project_group_vo = self.project_group_mgr.create_project_group(params.dict())
        return ProjectGroupResponse(**project_group_vo.to_dict())

    @transaction(
        permission="identity:ProjectGroup.write", role_types=["WORKSPACE_OWNER"]
    )
    @convert_model
    def update(
        self, params: ProjectGroupUpdateRequest
    ) -> Union[ProjectGroupResponse, dict]:
        """Update project group

        Args:
            params (ProjectGroupUpdateRequest): {
                'project_group_id': 'str',      # required
                'name': 'str',
                'tags': 'dict',
                'domain_id': 'str',             # injected from auth (required)
                'workspace_id': 'str',          # injected from auth (required)
            }
            Returns:
                ProjectGroupResponse:
        """

        project_group_vo = self.project_group_mgr.get_project_group(
            params.project_group_id,
            params.domain_id,
            params.workspace_id,
        )

        # Check is managed resource
        self.resource_mgr.check_is_managed_resource_by_trusted_account(project_group_vo)

        project_group_vo = self.project_group_mgr.update_project_group_by_vo(
            params.dict(exclude_unset=True), project_group_vo
        )

        return ProjectGroupResponse(**project_group_vo.to_dict())

    @transaction(
        permission="identity:ProjectGroup.write", role_types=["WORKSPACE_OWNER"]
    )
    @convert_model
    def change_parent_group(
        self, params: ProjectChangeParentGroupRequest
    ) -> Union[ProjectGroupResponse, dict]:
        """Change parent project group

        Args:
            params (ProjectChangeParentGroupRequest): {
                'project_group_id': 'str',      # required
                'parent_group_id': 'str',       # required
                'workspace_id': 'str',          # injected from auth (required)
                'domain_id': 'str'              # injected from auth (required)
            }
            Returns:
                ProjectGroupResponse:
        """

        project_group_vo = self.project_group_mgr.get_project_group(
            params.project_group_id,
            params.domain_id,
            params.workspace_id,
        )

        # Check is managed resource
        self.resource_mgr.check_is_managed_resource_by_trusted_account(project_group_vo)

        # Check parent project group is
        if params.parent_group_id:
            self.project_group_mgr.get_project_group(
                params.parent_group_id, params.domain_id, params.workspace_id
            )

            # Check parent project group is not sub project group
            project_group_vos = self.project_group_mgr.filter_project_groups(
                workspace_id=params.workspace_id, domain_id=params.domain_id
            )

            self._check_is_sub_project_group(
                params.parent_group_id,
                project_group_vo.project_group_id,
                project_group_vos,
            )

        project_group_vo = self.project_group_mgr.update_project_group_by_vo(
            params.dict(), project_group_vo
        )

        return ProjectGroupResponse(**project_group_vo.to_dict())

    @transaction(
        permission="identity:ProjectGroup.write", role_types=["WORKSPACE_OWNER"]
    )
    @convert_model
    def delete(self, params: ProjectGroupDeleteRequest) -> None:
        """Delete project group

        Args:
            params (ProjectGroupDeleteRequest): {
                'project_group_id': 'str',      # required
                'workspace_id': 'str',          # injected from auth (required)
                'domain_id': 'str'              # injected from auth (required)
            }
        Returns:
            None
        """

        project_group_vo = self.project_group_mgr.get_project_group(
            params.project_group_id,
            params.domain_id,
            params.workspace_id,
        )

        # Check is managed resource
        self.resource_mgr.check_is_managed_resource_by_trusted_account(project_group_vo)

        self.project_group_mgr.delete_project_group_by_vo(project_group_vo)

    @transaction(
        permission="identity:ProjectGroup.write", role_types=["WORKSPACE_OWNER"]
    )
    @convert_model
    def add_users(
        self, params: ProjectGroupAddUsersRequest
    ) -> Union[ProjectGroupResponse, dict]:
        """Add users to project group

        Args:
            params (ProjectGroupAddUsersRequest): {
                'project_group_id': 'str',      # required
                'users': 'list',             # required
                'domain_id': 'str',             # injected from auth (required)
                'workspace_id': 'str'           # injected from auth (required)
            }
        Returns:
            ProjectGroupResponse:
        """

        project_group_vo = self.project_group_mgr.get_project_group(
            params.project_group_id, params.domain_id, params.workspace_id
        )

        if len(params.users) > 0:
            workspace_user_mgr = WorkspaceUserManager()
            workspace_user_mgr.check_workspace_users(
                params.users, params.workspace_id, params.domain_id
            )

            users = project_group_vo.users or []
            users.extend(params.users)
            params.users = list(set(users))

            project_group_vo = self.project_group_mgr.update_project_group_by_vo(
                params.dict(exclude_unset=True), project_group_vo
            )

        return ProjectGroupResponse(**project_group_vo.to_dict())

    @transaction(
        permission="identity:ProjectGroup.write",
        role_types=["WORKSPACE_OWNER"],
    )
    @convert_model
    def remove_users(
        self, params: ProjectGroupRemoveUsersRequest
    ) -> ProjectGroupResponse:
        """Remove users from project group
        Args:
            params: (ProjectGroupRemoveUsersRequest): {
                'project_group_id': 'str',      # required
                'users': 'list',             # required
                'workspace_id': 'str',             # injected from auth (required)
                'domain_id': 'str'           # injected from auth (required)
            }

        """

        project_group_vo = self.project_group_mgr.get_project_group(
            params.project_group_id, params.domain_id, params.workspace_id
        )

        if len(params.users) > 0:
            workspace_user_mgr = WorkspaceUserManager()
            workspace_user_mgr.check_workspace_users(
                params.users, params.workspace_id, params.domain_id
            )

            users = project_group_vo.users or []
            params.users = list(set(users) - set(params.users))
            project_group_vo = self.project_group_mgr.update_project_group_by_vo(
                params.dict(exclude_unset=True), project_group_vo
            )

        return ProjectGroupResponse(**project_group_vo.to_dict())

    @transaction(
        permission="identity:ProjectGroup.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @convert_model
    def get(self, params: ProjectGroupGetRequest) -> Union[ProjectGroupResponse, dict]:
        """Get project group

        Args:
            params (ProjectGroupGetRequest): {
                'project_group_id': 'str',      # required
                'workspace_id': 'str',          # injected from auth
                'domain_id': 'str'              # injected from auth (required)
            }
        Returns:
            ProjectGroupResponse:
        """

        project_group_vo = self.project_group_mgr.get_project_group(
            params.project_group_id,
            params.domain_id,
            params.workspace_id,
        )

        return ProjectGroupResponse(**project_group_vo.to_dict())

    @transaction(
        permission="identity:ProjectGroup.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @append_query_filter(
        ["project_group_id", "name", "parent_group_id", "workspace_id", "domain_id"]
    )
    @append_keyword_filter(["project_group_id", "name"])
    @convert_model
    def list(
        self, params: ProjectGroupSearchQueryRequest
    ) -> Union[ProjectGroupsResponse, dict]:
        """List project groups

        Args:
            params (ProjectGroupSearchQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.Query)',
                'project_group_id': 'str',
                'name': 'str',
                'parent_group_id': 'str',
                'workspace_id': 'str',      # injected from auth
                'domain_id': 'str',         # injected from auth (required)
            }
        Returns:
            ProjectGroupsResponse:
        """

        query = params.query or {}
        project_vos, total_count = self.project_group_mgr.list_project_groups(query)

        projects_info = [project_vo.to_dict() for project_vo in project_vos]
        return ProjectGroupsResponse(results=projects_info, total_count=total_count)

    @transaction(
        permission="identity:ProjectGroup.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @append_query_filter(["workspace_id", "domain_id"])
    @append_keyword_filter(["project_group_id", "name"])
    @convert_model
    def stat(self, params: ProjectGroupStatQueryRequest) -> dict:
        """Stat project groups
        Args:
            params (ProjectGroupStatQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)', # required
                'workspace_id': 'str',    # injected from auth
                'domain_id': 'str',       # injected from auth (required)
            }
        Returns:
            dict: {
                'results': 'list',
                'total_count': 'int'
            }
        """

        query = params.query or {}
        return self.project_group_mgr.stat_project_groups(query)

    def _check_is_sub_project_group(
        self,
        change_parent_group_id: str,
        cur_group_id: str,
        project_group_vos: QuerySet,
    ) -> Union[None, Exception]:
        for project_group_vo in project_group_vos:
            if project_group_vo.parent_group_id == cur_group_id:
                if change_parent_group_id == project_group_vo.project_group_id:
                    raise ERROR_NOT_ALLOWED_TO_CHANGE_PARENT_GROUP_TO_SUB_PROJECT_GROUP(
                        project_group_id=change_parent_group_id
                    )
                else:
                    return self._check_is_sub_project_group(
                        change_parent_group_id,
                        project_group_vo.project_group_id,
                        project_group_vos,
                    )
        return None

    def _check_workspace_member_permission(
        self, project_group_vo: ProjectGroup
    ) -> None:
        role_type = self.transaction.get_meta("authorization.role_type")
        if role_type == "WORKSPACE_MEMBER":
            user_id = self.transaction.get_meta("authorization.user_id")
            project_group_users = project_group_vo.users or []
            if user_id not in project_group_users:
                raise ERROR_USER_NOT_IN_PROJECT_GROUP(
                    user_id=user_id, project_group_id=project_group_vo.project_group_id
                )
