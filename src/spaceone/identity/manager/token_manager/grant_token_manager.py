import logging

from spaceone.identity.error.error_authentication import *
from spaceone.identity.error.error_user import (
    ERROR_USER_STATE_DISABLED,
    ERROR_APP_STATE_DISABLED,
)
from spaceone.identity.manager.user_manager import UserManager
from spaceone.identity.manager.app_manager import AppManager
from spaceone.identity.manager.token_manager.base import TokenManager
from spaceone.identity.manager.api_key_manager import APIKeyManager
from spaceone.identity.manager.role_binding_manager import RoleBindingManager

_LOGGER = logging.getLogger(__name__)


class GrantTokenManager(TokenManager):
    auth_type = "GRANT"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_mgr = UserManager()
        self.app_mgr = AppManager()
        self.api_key_mgr = APIKeyManager()
        self.rb_mgr = RoleBindingManager()

    def authenticate(self, domain_id, **kwargs):
        scope = kwargs["scope"]
        owner_type = kwargs["owner_type"]
        role_type = kwargs["role_type"]
        user_vo = kwargs.get("user_vo")
        app_vo = kwargs.get("app_vo")

        if owner_type == "USER":
            self.user = user_vo
            self._check_user_state()
            self._check_role_type_by_scope(role_type, scope)
            if scope == "WORKSPACE" and role_type == "DOMAIN_ADMIN":
                self.role_type = "WORKSPACE_OWNER"
            elif scope == "USER":
                self.role_type = "USER"
            else:
                self.role_type = role_type

        else:
            self.app = app_vo
            self._check_app_state()
            self._check_role_type_by_scope(role_type, scope)

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
    def _check_role_type_by_scope(role_type, scope):
        if scope == "SYSTEM":
            if role_type != "SYSTEM_ADMIN":
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
