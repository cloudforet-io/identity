import logging
from typing import Union

from spaceone.core.auth.jwt import JWTAuthenticator
from spaceone.core.service import *
from spaceone.core.service.utils import *
from spaceone.identity.error.error_domain import *
from spaceone.identity.error.error_system import *
from spaceone.identity.manager.domain_manager import DomainManager
from spaceone.identity.manager.domain_secret_manager import DomainSecretManager
from spaceone.identity.manager.project_manager import ProjectManager
from spaceone.identity.manager.role_binding_manager import RoleBindingManager
from spaceone.identity.manager.role_manager import RoleManager
from spaceone.identity.manager.system_manager import SystemManager
from spaceone.identity.manager.user_group_manager import UserGroupManager
from spaceone.identity.manager.user_manager import UserManager
from spaceone.identity.manager.workspace_group_manager import WorkspaceGroupManager
from spaceone.identity.manager.workspace_manager import WorkspaceManager
from spaceone.identity.model.system.request import *
from spaceone.identity.model.system.response import *
from spaceone.identity.model.user.database import User

_LOGGER = logging.getLogger(__name__)


@event_handler
class SystemService(BaseService):
    resource = "System"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.domain_mgr = DomainManager()
        self.domain_secret_mgr = DomainSecretManager()
        self.user_mgr = UserManager()
        self.role_manager = RoleManager()
        self.role_binding_manager = RoleBindingManager()
        self.workspace_mgr = WorkspaceManager()
        self.workspace_group_mgr = WorkspaceGroupManager()
        self.user_mgr = UserManager()
        self.user_group_mgr = UserGroupManager()
        self.project_mgr = ProjectManager()
        self.workspace_group_mgr = WorkspaceGroupManager()

    @transaction()
    @convert_model
    def init(self, params: SystemInitRequest) -> Union[SystemResponse, dict]:
        """Init System
        Args:
            params (SystemInitRequest): {
                'admin': 'dict',    # required
                'force': 'bool'
            }
        Returns:
            SystemResponse:
        """

        system_mgr = SystemManager()

        root_domain_id = system_mgr.get_root_domain_id()
        root_domain_vos = self.domain_mgr.filter_domains(domain_id=root_domain_id)

        if root_domain_vos.count() == 0:
            _LOGGER.debug(f"[init] Create root domain: {root_domain_id}")
            root_domain_vo = self.domain_mgr.create_domain(
                {"domain_id": root_domain_id, "name": "root"}
            )

            self.domain_secret_mgr.delete_domain_secret(root_domain_vo.domain_id)
            self.domain_secret_mgr.create_domain_secret(root_domain_vo)

        else:
            if params.force is False:
                raise ERROR_SYSTEM_ALREADY_INITIALIZED()

            # Check System Token
            try:
                token = self.transaction.get_meta("token")
                root_pub_jwk = self.domain_secret_mgr.get_domain_public_key(
                    root_domain_id
                )
                JWTAuthenticator(root_pub_jwk).validate(token)
            except Exception:
                raise ERROR_UNKNOWN(message="Invalid System Token")

            root_domain_vo = root_domain_vos[0]

            _LOGGER.debug(
                f"[init] Reset root domain secret: {root_domain_vo.domain_id}"
            )
            self.domain_secret_mgr.delete_domain_secret(root_domain_vo.domain_id)
            self.domain_secret_mgr.create_domain_secret(root_domain_vo)

        if params.force:
            user_vos = self.user_mgr.filter_users(domain_id=root_domain_vo.domain_id)
            for user_vo in user_vos:
                _LOGGER.debug(
                    f"[init] Delete existing user in root domain: {user_vo.user_id}"
                )
                self._delete_user_by_vo(user_vo)

        # create admin user
        _LOGGER.debug(f"[init] Create admin user: {params.admin.user_id}")
        params_admin = params.admin.dict()
        params_admin["auth_type"] = "LOCAL"
        params_admin["domain_id"] = root_domain_vo.domain_id
        params_admin["role_type"] = "DOMAIN_ADMIN"
        params_admin["role_id"] = "managed-domain-admin"
        user_vo = self.user_mgr.create_user(params_admin)

        # create default role
        role_mgr = RoleManager()
        role_mgr.list_roles({}, root_domain_vo.domain_id)
        role_vos = self.role_manager.filter_roles(
            domain_id=root_domain_vo.domain_id, role_type="DOMAIN_ADMIN"
        )

        if len(role_vos) == 0:
            raise ERROR_DOMAIN_ADMIN_ROLE_IS_NOT_DEFINED()

        # create role binding
        _LOGGER.debug(
            f"[init] Create role binding: {user_vo.user_id} ({role_vos[0].role_id})"
        )
        role_binding_mgr = RoleBindingManager()
        params_rb = {
            "user_id": user_vo.user_id,
            "role_id": role_vos[0].role_id,
            "scope": "DOMAIN",
            "domain_id": user_vo.domain_id,
            "role_type": role_vos[0].role_type,
        }
        rb_vo = role_binding_mgr.create_role_binding(params_rb)
        self._update_workspace_user_count(rb_vo.workspace_id, rb_vo.domain_id)

        system_token = system_mgr.create_system_token(
            root_domain_vo.domain_id, user_vo.user_id
        )

        response = {
            "domain_id": root_domain_vo.domain_id,
            "name": root_domain_vo.name,
            "system_token": system_token,
        }

        return SystemResponse(**response)

    def _delete_user_by_vo(self, user_vo: User) -> None:
        # Delete role bindings
        rb_vos = self.role_binding_manager.filter_role_bindings(
            user_id=user_vo.user_id, domain_id=user_vo.domain_id
        )
        for rb_vo in rb_vos:
            self.role_binding_manager.delete_role_binding_by_vo(rb_vo)
            self._update_workspace_user_count(rb_vo.workspace_id, rb_vo.domain_id)

        # Delete user from user groups
        user_group_vos = self.user_group_mgr.filter_user_groups(
            users=user_vo.user_id, domain_id=user_vo.domain_id
        )
        for user_group_vo in user_group_vos:
            users = user_group_vo.users
            users.remove(user_vo.user_id)
            self.user_group_mgr.update_user_group_by_vo(
                {"users": users}, user_group_vo=user_group_vo
            )

        # Delete projects
        project_vos = self.project_mgr.filter_projects(
            users=user_vo.user_id, domain_id=user_vo.domain_id
        )
        for project_vo in project_vos:
            users = project_vo.users
            users.remove(user_vo.user_id)
            self.project_mgr.update_project_by_vo(
                {"users": users}, project_vo=project_vo
            )

        # Delete workspace groups
        workspace_group_vos = self.workspace_group_mgr.filter_workspace_groups(
            users__user_id=user_vo.user_id, domain_id=user_vo.domain_id
        )

        for workspace_group_vo in workspace_group_vos:
            workspace_group_dict = workspace_group_vo.to_mongo().to_dict()
            users = workspace_group_dict.get("users", [])

            if users:
                updated_users = [
                    user for user in users if user.get("user_id") != user_vo.user_id
                ]

                if len(updated_users) != len(users):
                    self.workspace_group_mgr.update_workspace_group_by_vo(
                        {"users": updated_users}, workspace_group_vo=workspace_group_vo
                    )

        self.user_mgr.delete_user(user_vo)

    def _get_workspace_user_count(self, workspace_id: str, domain_id: str) -> int:
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

    def _update_workspace_user_count(self, workspace_id: str, domain_id: str) -> None:
        if not workspace_id and not domain_id:
            return

        if workspace_id == "*":
            return

        workspace_vo = self.workspace_mgr.get_workspace(workspace_id, domain_id)

        if workspace_vo and workspace_vo.workspace_id != "*":
            user_rb_total_count = self._get_workspace_user_count(
                workspace_id, domain_id
            )
            self.workspace_mgr.update_workspace_by_vo(
                {"user_count": user_rb_total_count}, workspace_vo
            )
