import logging
from typing import Union
from spaceone.core.service import (
    BaseService,
    transaction,
    convert_model,
    append_query_filter,
    append_keyword_filter,
)
from spaceone.identity.manager.project_group_manager import ProjectGroupManager
from spaceone.identity.model.project_group.request import *
from spaceone.identity.model.project_group.response import *

_LOGGER = logging.getLogger(__name__)


class ProjectGroupService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_group_mgr = ProjectGroupManager()

    @transaction
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
                'workspace_id': 'str',      # required
                'domain_id': 'str'          # required
            }
        Returns:
            ProjectGroupResponse:
        """

        if params.parent_group_id:
            self.project_group_mgr.get_project_group(
                params.parent_group_id, params.workspace_id, params.domain_id
            )

        project_group_vo = self.project_group_mgr.create_project_group(params.dict())
        return ProjectGroupResponse(**project_group_vo.to_dict())

    @transaction
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
                'domain_id': 'str',             # required
                'workspace_id': 'str',          # required
            }
            Returns:
                ProjectGroupResponse:
        """

        project_group_vo = self.project_group_mgr.get_project_group(
            params.project_group_id, params.workspace_id, params.domain_id
        )
        project_group_vo = self.project_group_mgr.update_project_group_by_vo(
            params.dict(exclude_unset=True), project_group_vo
        )

        return ProjectGroupResponse(**project_group_vo.to_dict())

    @transaction
    @convert_model
    def change_parent_group(
        self, params: ProjectChangeParentGroupRequest
    ) -> Union[ProjectGroupResponse, dict]:
        """Change parent project group

        Args:
            params (ProjectChangeParentGroupRequest): {
                'project_group_id': 'str',      # required
                'parent_group_id': 'str',       # required
                'workspace_id': 'str',          # required
                'domain_id': 'str'              # required
            }
            Returns:
                ProjectGroupResponse:
        """

        # Check parent project group is
        if params.parent_group_id:
            self.project_group_mgr.get_project_group(
                params.parent_group_id, params.workspace_id, params.domain_id
            )

        project_group_vo = self.project_group_mgr.get_project_group(
            params.project_group_id, params.workspace_id, params.domain_id
        )
        project_group_vo = self.project_group_mgr.update_project_group_by_vo(
            params.dict(), project_group_vo
        )

        return ProjectGroupResponse(**project_group_vo.to_dict())

    @transaction
    @convert_model
    def delete(self, params: ProjectGroupDeleteRequest) -> None:
        """Delete project group

        Args:
            params (ProjectGroupDeleteRequest): {
                'project_group_id': 'str',      # required
                'workspace_id': 'str',          # required
                'domain_id': 'str'              # required
            }
        Returns:
            None
        """

        project_group_vo = self.project_group_mgr.get_project_group(
            params.project_group_id, params.workspace_id, params.domain_id,
        )

        self.project_group_mgr.delete_project_group_by_vo(project_group_vo)

    @transaction
    @convert_model
    def get(self, params: ProjectGroupGetRequest) -> Union[ProjectGroupResponse, dict]:
        """Get project group

        Args:
            params (ProjectGroupGetRequest): {
                'project_group_id': 'str',      # required
                'workspace_id': 'str',          # required
                'domain_id': 'str'              # required
            }
        Returns:
            ProjectGroupResponse:
        """

        project_group_vo = self.project_group_mgr.get_project_group(
            params.project_group_id, params.workspace_id, params.domain_id
        )

        return ProjectGroupResponse(**project_group_vo.to_dict())

    @transaction
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
                'workspace_id': 'str',
                'domain_id': 'str',         # required
            }
        Returns:
            ProjectGroupsResponse:
        """

        query = params.query or {}
        project_vos, total_count = self.project_group_mgr.list_project_groups(query)
        projects_info = [project_vo.to_dict() for project_vo in project_vos]
        return ProjectGroupsResponse(results=projects_info, total_count=total_count)

    @transaction
    @append_query_filter(["workspace_id", "domain_id"])
    @append_keyword_filter(["project_group_id", "name"])
    @convert_model
    def stat(self, params: ProjectGroupStatQueryRequest) -> dict:
        """Stat project groups
        Args:
            params (ProjectGroupStatQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)', # required
                'domain_id': 'str',         # required
                'workspace_id': 'str'
            }
        Returns:
            dict: {
                'results': 'list',
                'total_count': 'int'
            }
        """

        query = params.query or {}
        return self.project_group_mgr.stat_project_groups(query)
