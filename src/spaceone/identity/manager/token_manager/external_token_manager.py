import logging
from datetime import datetime
from spaceone.identity.connector import AuthPluginConnector
from spaceone.identity.error.error_authentication import *
from spaceone.identity.error.error_user import ERROR_USER_STATUS_CHECK_FAILURE
from spaceone.identity.manager.user_manager import UserManager
from spaceone.identity.manager.token_manager import JWTManager
from spaceone.identity.manager.domain_manager import DomainManager
from spaceone.identity.model.domain.database import Domain
from spaceone.identity.model.user.database import User

_LOGGER = logging.getLogger(__name__)


class ExternalTokenManager(JWTManager):
    domain: Domain = None
    auth_type = "EXTERNAL"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.domain_mgr = DomainManager()
        self.user_mgr = UserManager()

    def authenticate(self, user_id, domain_id, credentials):
        _LOGGER.debug(f"[authenticate] domain_id: {domain_id}")

        # Add User ID for External Authentication
        if user_id:
            credentials["user_id"] = user_id

        self.domain: Domain = self.domain_mgr.get_domain(domain_id)

        self._check_domain_state()

        endpoint = self.domain_mgr.get_auth_plugin_endpoint_by_vo(self.domain)
        auth_user_info = self._authenticate_with_plugin(endpoint, credentials)

        _LOGGER.info(
            f'[authenticate] Authentication success. (user_id={auth_user_info.get("user_id")})'
        )

        auto_user_sync = self.domain.plugin_info.options.get("auto_user_sync", False)

        self._verify_user_from_plugin_user_info(
            auth_user_info, domain_id, auto_user_sync
        )
        self._check_user_state()

        self.is_authenticated = True

    def issue_token(self, **kwargs):
        if self.is_authenticated is False:
            raise ERROR_NOT_AUTHENTICATED()

        if self.user.state == "PENDING":
            self.user: User = self.user.update({"state": "ENABLED"})

        # Issue token
        access_token = self.issue_access_token(
            "USER", self.user.user_id, self.user.domain_id, **kwargs
        )
        refresh_token = self.issue_refresh_token(
            "USER", self.user.user_id, self.user.domain_id, **kwargs
        )

        # Update user's last_accessed_at field
        self.user.update({"last_accessed_at": datetime.utcnow()})

        return {"access_token": access_token, "refresh_token": refresh_token}

    def refresh_token(self, user_id, domain_id, **kwargs):
        self.user: User = self.user_mgr.get_user(user_id, domain_id)
        self._check_user_state()

        return self.issue_token(**kwargs)

    def _verify_user_from_plugin_user_info(
        self, auth_user_info, domain_id, auto_user_sync=False
    ):
        if "user_id" not in auth_user_info:
            _LOGGER.error(
                f"[_verify_user_from_plugin_user_info] does not return user_id from plugin user info."
            )
            raise ERROR_AUTHENTICATION_FAILURE_PLUGIN(
                message="plugin response is invalid."
            )

        user_id = auth_user_info["user_id"]
        state = auth_user_info.get("state", "ENABLED")

        user_vos = self.user_mgr.filter_users(user_id=user_id, domain_id=domain_id)

        if user_vos.count() > 0:
            self.user: User = user_vos[0]
        else:
            if auto_user_sync:
                name = auth_user_info.get("name")
                email = auth_user_info.get("email")
                self.user: User = self._create_external_user(
                    user_id, state, domain_id, name, email
                )
            else:
                raise ERROR_NOT_FOUND(key="user_id", value=user_id)

    def _authenticate_with_plugin(self, endpoint, credentials):
        options = self.domain.plugin_info.options

        auth_plugin_conn: AuthPluginConnector = self.locator.get_connector(
            "AuthPluginConnector"
        )
        auth_plugin_conn.initialize(endpoint)

        return auth_plugin_conn.call_login(credentials, options, {})

    def _check_domain_state(self):
        if not self.domain.plugin_info:
            _LOGGER.error(
                "[_get_token_manager] This domain does not allow external authentication."
            )
            raise ERROR_AUTHENTICATION_FAILURE(user_id=self.user.user_id)

    def _check_user_state(self):
        if self.user.state not in ["ENABLED", "PENDING"]:
            raise ERROR_USER_STATUS_CHECK_FAILURE(user_id=self.user.user_id)

        if self.user.backend != "EXTERNAL":
            raise ERROR_NOT_FOUND(key="user_id", value=self.user.user_id)

    def _create_external_user(self, user_id, state, domain_id, name=None, email=None):
        _LOGGER.error(f"[_create_external_user] create user on first login: {user_id}")
        return self.user_mgr.create_user(
            {
                "user_id": user_id,
                "state": state,
                "name": name,
                "email": email,
                "user_type": "USER",
                "backend": "EXTERNAL",
                "domain_id": domain_id,
            },
            self.domain,
            is_first_login_user=True,
        )
