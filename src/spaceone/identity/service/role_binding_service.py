import logging
from typing import Union

from spaceone.core.service import *
from spaceone.core.service.utils import *

from spaceone.identity.error import ERROR_NOT_ALLOWED_TO_DELETE_ROLE_BINDING
from spaceone.identity.error.error_role import *
from spaceone.identity.manager.role_binding_manager import RoleBindingManager
from spaceone.identity.manager.role_manager import RoleManager
from spaceone.identity.manager.user_manager import UserManager
from spaceone.identity.manager.workspace_manager import WorkspaceManager
from spaceone.identity.model import RoleBinding
from spaceone.identity.model.role_binding.request import *
from spaceone.identity.model.role_binding.response import *

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class RoleBindingService(BaseService):
    resource = "RoleBinding"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role_binding_manager = RoleBindingManager()
        self.user_mgr = UserManager()
        self.workspace_mgr = WorkspaceManager()

    @transaction(
        permission="identity:RoleBinding.write",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER"],
    )
    @convert_model
    def create(
        self, params: RoleBindingCreateRequest
    ) -> Union[RoleBindingResponse, dict]:
        """create role binding

         Args:
            params (RoleBindingCreateRequest): {
                'user_id': 'str',                   # required
                'role_id': 'str',                   # required
                'resource_group': 'str',            # required
                'workspace_id': 'str',              # injected from auth
                'domain_id': 'str'                  # injected from auth (required)
            }

        Returns:
            RoleBindingResponse:
        """

        rb_vo = self.create_role_binding(params.dict())
        return RoleBindingResponse(**rb_vo.to_dict())

    def create_role_binding(self, params: dict):
        user_id = params["user_id"]
        role_id = params["role_id"]
        resource_group = params["resource_group"]
        domain_id = params["domain_id"]
        workspace_group_id = params.get("workspace_group_id")
        workspace_id = params.get("workspace_id")

        # Check user
        user_vo = self.user_mgr.get_user(user_id, domain_id)

        workspace_vo = None

        # Check workspace
        if resource_group == "WORKSPACE":
            workspace_mgr = WorkspaceManager()
            workspace_vo = workspace_mgr.get_workspace(workspace_id, domain_id)
        else:
            params["workspace_id"] = "*"
            workspace_id = "*"

        # Check role
        role_mgr = RoleManager()
        role_vo = role_mgr.get_role(role_id, domain_id)

        if resource_group == "DOMAIN":
            if role_vo.role_type != "DOMAIN_ADMIN":
                raise ERROR_NOT_ALLOWED_ROLE_TYPE(
                    request_role_id=role_vo.role_id,
                    request_role_type=role_vo.role_type,
                    supported_role_type="DOMAIN_ADMIN",
                )
            self.check_duplicate_domain_admin_role(
                domain_id, user_id, role_vo.role_type
            )
        else:
            if role_vo.role_type not in ["WORKSPACE_OWNER", "WORKSPACE_MEMBER"]:
                raise ERROR_NOT_ALLOWED_ROLE_TYPE(
                    request_role_id=role_vo.role_id,
                    request_role_type=role_vo.role_type,
                    supported_role_type=["WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
                )
            self.check_duplicate_workspace_role(
                domain_id, workspace_group_id, workspace_id, user_id
            )

        params["role_type"] = role_vo.role_type

        # Update user role type
        latest_role_type = self._get_latest_role_type(
            user_vo.role_type, role_vo.role_type
        )

        user_role_info = {"role_type": latest_role_type}
        if role_vo.role_type in ["DOMAIN_ADMIN"]:
            user_role_info.update({"role_id": role_vo.role_id})

        self.user_mgr.update_user_by_vo(user_role_info, user_vo)

        # Create role binding
        rb_vo = self.role_binding_manager.create_role_binding(params)

        if workspace_vo:
            self.update_workspace_user_count(domain_id, workspace_id)

        return rb_vo

    @transaction(
        permission="identity:RoleBinding.write",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER"],
    )
    @convert_model
    def update_role(
        self, params: RoleBindingUpdateRoleRequest
    ) -> Union[RoleBindingResponse, dict]:
        """update role of role binding

         Args:
            params (RoleBindingUpdateRoleRequest): {
                'role_binding_id': 'str',           # required
                'role_id': 'str',                   # required
                'workspace_id': 'str',              # injected from auth
                'domain_id': 'str',                 # injected from auth (required)
            }

        Returns:
            RoleBindingResponse:
        """

        request_user_id = self.transaction.get_meta("authorization.user_id")

        rb_vo = self.role_binding_manager.get_role_binding(
            params.role_binding_id, params.domain_id, params.workspace_id
        )

        self.check_self_update_and_delete(request_user_id, rb_vo.user_id)

        if rb_vo.workspace_group_id:
            raise ERROR_PERMISSION_DENIED(
                key="role_binding_id", value=params.role_binding_id
            )

        # Check role
        role_mgr = RoleManager()
        new_role_vo = role_mgr.get_role(params.role_id, params.domain_id)

        if rb_vo.role_type in ["WORKSPACE_OWNER", "WORKSPACE_MEMBER"]:
            if new_role_vo.role_type not in ["WORKSPACE_OWNER", "WORKSPACE_MEMBER"]:
                raise ERROR_NOT_ALLOWED_ROLE_TYPE(
                    request_role_id=new_role_vo.role_id,
                    request_role_type=new_role_vo.role_type,
                    supported_role_type=["WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
                )
            self.check_last_workspace_owner_role_binding(
                new_role_vo.role_type, rb_vo.workspace_id, rb_vo.domain_id
            )
        elif rb_vo.role_type == new_role_vo.role_type:
            self.check_last_domain_admin_role_binding(
                new_role_vo.role_type, rb_vo.domain_id
            )
        else:
            raise ERROR_NOT_ALLOWED_ROLE_TYPE(
                request_role_id=new_role_vo.role_id,
                request_role_type=new_role_vo.role_type,
                supported_role_type=[rb_vo.role_type],
            )

        user_vo = self.user_mgr.get_user(rb_vo.user_id, rb_vo.domain_id)

        latest_role_type = self._get_latest_role_type(
            user_vo.role_type, new_role_vo.role_type
        )

        user_role_info = {"role_type": latest_role_type}
        if latest_role_type and new_role_vo.role_type in ["DOMAIN_ADMIN"]:
            user_role_info.update({"role_id": new_role_vo.role_id})

        self.user_mgr.update_user_by_vo(user_role_info, user_vo)

        rb_vo = self.role_binding_manager.update_role_binding_by_vo(
            {"role_id": params.role_id, "role_type": new_role_vo.role_type}, rb_vo
        )

        return RoleBindingResponse(**rb_vo.to_dict())

    @transaction(
        permission="identity:RoleBinding.write",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER"],
    )
    @convert_model
    def delete(self, params: RoleBindingDeleteRequest) -> None:
        """delete role binding

         Args:
            params (RoleBindingDeleteRequest): {
                'role_binding_id': 'str',       # required
                'workspace_id': 'str',          # injected from auth
                'domain_id': 'str',             # injected from auth (required)
            }

        Returns:
            None
        """

        request_user_id = self.transaction.get_meta("authorization.user_id")

        rb_vo = self.role_binding_manager.get_role_binding(
            params.role_binding_id, params.domain_id, params.workspace_id
        )

        if rb_vo.workspace_group_id:
            raise ERROR_NOT_ALLOWED_TO_DELETE_ROLE_BINDING(
                workspace_group_id=rb_vo.workspace_group_id,
                role_binding_id=rb_vo.role_binding_id,
            )

        self.check_self_update_and_delete(request_user_id, rb_vo.user_id)

        if rb_vo.role_type == "DOMAIN_ADMIN":
            self.check_last_domain_admin_role_binding(None, rb_vo.domain_id)
        elif rb_vo.role_type == "WORKSPACE_OWNER":
            self.check_last_workspace_owner_role_binding(
                None, rb_vo.workspace_id, rb_vo.domain_id
            )

        # Update user role type
        remain_rb_vos = self.role_binding_manager.filter_role_bindings(
            domain_id=params.domain_id, user_id=rb_vo.user_id
        )

        latest_role_type = "USER"
        for remain_rb_vo in remain_rb_vos:
            if remain_rb_vo.role_binding_id == params.role_binding_id:
                continue

            latest_role_type = self._get_latest_role_type(
                latest_role_type, remain_rb_vo.role_type
            )

        user_role_info = {"role_type": latest_role_type}
        if latest_role_type == "USER":
            user_role_info.update({"role_id": None})

        user_vo = self.user_mgr.get_user(rb_vo.user_id, rb_vo.domain_id)

        self.user_mgr.update_user_by_vo(user_role_info, user_vo)
        self.delete_role_binding_by_vo(rb_vo, params.domain_id, params.workspace_id)

    @transaction(
        permission="identity:RoleBinding.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @convert_model
    def get(self, params: RoleBindingGetRequest) -> Union[RoleBindingResponse, dict]:
        """get role binding

         Args:
            params (RoleBindingGetRequest): {
                'role_binding_id': 'str',       # required
                'workspace_id': 'list',         # injected from auth
                'domain_id': 'str',             # injected from auth (required)
            }

        Returns:
             RoleBindingResponse:
        """

        rb_vo = self.role_binding_manager.get_role_binding(
            params.role_binding_id, params.domain_id, params.workspace_id
        )

        return RoleBindingResponse(**rb_vo.to_dict())

    @transaction(
        permission="identity:RoleBinding.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @append_query_filter(
        [
            "role_binding_id",
            "user_id",
            "role_id",
            "workspace_id",
            "domain_id",
        ]
    )
    @append_keyword_filter(["role_binding_id", "user_id", "role_id"])
    @convert_model
    def list(
        self, params: RoleBindingSearchQueryRequest
    ) -> Union[RoleBindingsResponse, dict]:
        """list role bindings

        Args:
            params (RoleBindingSearchQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.Query)',
                'role_binding_id': 'str',
                'role_type': 'str',
                'user_id': 'str',
                'role_id': 'str',
                'workspace_id': 'list',         # injected from auth
                'domain_id': 'str',             # injected from auth (required)
            }

        Returns:
            RoleBindingsResponse:
        """

        query = params.query or {}
        rb_vos, total_count = self.role_binding_manager.list_role_bindings(query)

        rbs_info = [rb_vo.to_dict() for rb_vo in rb_vos]
        return RoleBindingsResponse(results=rbs_info, total_count=total_count)

    @transaction(
        permission="identity:RoleBinding.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @append_query_filter(["workspace_id", "domain_id"])
    @append_keyword_filter(["role_binding_id", "user_id", "role_id"])
    @convert_model
    def stat(self, params: RoleBindingStatQueryRequest) -> dict:
        """stat role bindings

        Args:
            params (RoleBindingStatQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)', # required
                'workspace_id': 'list',     # injected from auth
                'domain_id': 'str',         # injected from auth (required)
            }

        Returns:
            dict: {
                'results': 'list',
                'total_count': 'int'
            }
        """

        query = params.query or {}
        return self.role_binding_manager.stat_role_bindings(query)

    def check_duplicate_domain_admin_role(
        self, domain_id: str, user_id: str, role_type: str
    ) -> None:
        rb_vos = self.role_binding_manager.filter_role_bindings(
            domain_id=domain_id,
            user_id=user_id,
            role_type=role_type,
        )

        if rb_vos.count() > 0:
            raise ERROR_DUPLICATED_ROLE_BINDING(role_type=role_type)

    def check_duplicate_workspace_role(
        self, domain_id: str, workspace_group_id: str, workspace_id: str, user_id: str
    ) -> None:
        conditions = {
            "domain_id": domain_id,
            "workspace_id": workspace_id,
            "user_id": user_id,
        }
        if workspace_group_id:
            conditions["workspace_group_id"] = workspace_group_id

        rb_vos = self.role_binding_manager.filter_role_bindings(**conditions)

        if rb_vos.count() >= 1:
            raise ERROR_DUPLICATED_WORKSPACE_ROLE_BINDING(
                allowed_role_type=["WORKSPACE_OWNER", "WORKSPACE_MEMBER"]
            )

    def check_last_domain_admin_role_binding(
        self, new_role_type: Union[str, None], domain_id: str
    ) -> None:

        user_ids = self._get_enabled_user_ids(domain_id)
        rb_vos = self.role_binding_manager.filter_role_bindings(
            domain_id=domain_id,
            role_type="DOMAIN_ADMIN",
            user_id=user_ids,
        )

        if rb_vos.count() == 1 and new_role_type != "DOMAIN_ADMIN":
            raise ERROR_LAST_DOMAIN_ADMIN_CANNOT_DELETE()

    def check_last_workspace_owner_role_binding(
        self, new_role_type: Union[str, None], workspace_id: str, domain_id: str
    ) -> None:

        user_ids = self._get_enabled_user_ids(domain_id)
        rb_vos = self.role_binding_manager.filter_role_bindings(
            domain_id=domain_id,
            workspace_id=workspace_id,
            user_id=user_ids,
            role_type="WORKSPACE_OWNER",
        )

        if rb_vos.count() == 1 and new_role_type != "WORKSPACE_OWNER":
            raise ERROR_LAST_WORKSPACE_OWNER_CANNOT_DELETE()

    def _get_enabled_user_ids(self, domain_id: str) -> list:
        user_vos = self.user_mgr.filter_users(
            domain_id=domain_id,
            state="ENABLED",
        )

        return [user_vo.user_id for user_vo in user_vos]

    @staticmethod
    def check_self_update_and_delete(requested_user_id: str, user_id: str) -> None:
        if user_id == requested_user_id:
            raise ERROR_NOT_ALLOWED_TO_UPDATE_OR_DELETE_ROLE_BY_SELF()

    @staticmethod
    def _get_latest_role_type(before: str, after: str) -> str:
        priority = {
            "DOMAIN_ADMIN": 1,
            "WORKSPACE_OWNER": 2,
            "WORKSPACE_MEMBER": 3,
            "USER": 4,
        }

        before_priority = priority.get(before, 4)
        after_priority = priority.get(after, 4)

        if before_priority < after_priority:
            return before
        else:
            if after in ["WORKSPACE_OWNER", "WORKSPACE_MEMBER"]:
                return "USER"

            return after

    def update_workspace_user_count(self, domain_id: str, workspace_id: str) -> None:
        workspace_vo = self.workspace_mgr.get_workspace(
            domain_id=domain_id, workspace_id=workspace_id
        )

        if workspace_vo:
            user_rb_total_count = self._get_workspace_user_count(
                domain_id, workspace_id
            )
            self.workspace_mgr.update_workspace_by_vo(
                {"user_count": user_rb_total_count}, workspace_vo
            )

    def delete_role_binding_by_vo(
        self, rb_vo: RoleBinding, domain_id: str, workspace_id: str = None
    ):
        self.role_binding_manager.delete_role_binding_by_vo(rb_vo)

        if workspace_id:
            self.update_workspace_user_count(domain_id, workspace_id)

    def _get_workspace_user_count(self, domain_id: str, workspace_id: str) -> int:
        user_rb_ids = self.role_binding_manager.stat_role_bindings(
            query={
                "distinct": "user_id",
                "filter": [
                    {"k": "workspace_id", "v": workspace_id, "o": "eq"},
                    {"k": "domain_id", "v": domain_id, "o": "eq"},
                ],
            }
        ).get("results", [])
        return len(user_rb_ids)
