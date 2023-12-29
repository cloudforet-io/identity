import logging

from spaceone.identity.error.error_authentication import *
from spaceone.identity.error.error_user import (
    ERROR_USER_STATE_DISABLED,
    ERROR_APP_STATE_DISABLED,
)
from spaceone.identity.manager.user_manager import UserManager
from spaceone.identity.manager.app_manager import AppManager
from spaceone.identity.manager.token_manager.base import TokenManager
from spaceone.identity.manager.role_binding_manager import RoleBindingManager
from spaceone.identity.manager.system_manager import SystemManager

_LOGGER = logging.getLogger(__name__)


class GrantTokenManager(TokenManager):
    auth_type = "GRANT"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_mgr = UserManager()
        self.app_mgr = AppManager()
        self.rb_mgr = RoleBindingManager()

    def authenticate(self, domain_id, **kwargs):
        scope = kwargs["scope"]
        role_type = kwargs["role_type"]

        self.user = kwargs["user_vo"]
        self._check_user_state()
        self._check_role_type_by_scope(role_type, scope, self.user.domain_id)
        if scope == "WORKSPACE" and role_type == "DOMAIN_ADMIN":
            self.role_type = "WORKSPACE_OWNER"
        elif scope == "USER":
            self.role_type = "USER"
        elif scope == "SYSTEM":
            self.role_type = "SYSTEM_ADMIN"
        else:
            self.role_type = role_type

        self.is_authenticated = True

    @staticmethod
    def _parse_password(credentials):
        pw_to_check = credentials.get("password", None)

        if pw_to_check is None:
            raise ERROR_INVALID_CREDENTIALS()

        return pw_to_check

    def _check_user_state(self):
        if self.user.state == "DISABLED":
            raise ERROR_USER_STATE_DISABLED(user_id=self.user.user_id)

    def _check_app_state(self):
        if self.app.state == "DISABLED":
            raise ERROR_APP_STATE_DISABLED(app_id=self.app.app_id)

    def _get_user_role_type(self, workspace_id=None):
        role_type = self.user.role_type

        if role_type in ["WORKSPACE_OWNER", "WORKSPACE_MEMBER"]:
            rb_vos = self.rb_mgr.filter_role_bindings(
                user_id=self.user.user_id,
                domain_id=self.user.domain_id,
                role_type=["WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
                workspace_id=workspace_id,
            )

            if rb_vos.count() > 0:
                role_type = rb_vos[0].role_type

        return role_type

    @staticmethod
    def _check_role_type_by_scope(role_type, scope, user_domain_id):
        if scope == "SYSTEM":
            if not (
                role_type == "DOMAIN_ADMIN"
                and user_domain_id == SystemManager.get_root_domain_id()
            ):
                raise ERROR_PERMISSION_DENIED()
        elif scope == "DOMAIN":
            if role_type != "DOMAIN_ADMIN":
                raise ERROR_PERMISSION_DENIED()
        elif scope == "WORKSPACE":
            if role_type not in [
                "DOMAIN_ADMIN",
                "WORKSPACE_OWNER",
                "WORKSPACE_MEMBER",
            ]:
                raise ERROR_PERMISSION_DENIED()
