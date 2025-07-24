import copy
import logging
import re
import secrets
import string
from typing import Union

from spaceone.core import config
from spaceone.core.service import *
from spaceone.core.service.utils import *
from spaceone.identity.error.error_mfa import *
from spaceone.identity.error.error_user import *
from spaceone.identity.manager import SecretManager
from spaceone.identity.manager.config_manager import ConfigManager
from spaceone.identity.manager.domain_manager import DomainManager
from spaceone.identity.manager.domain_secret_manager import DomainSecretManager
from spaceone.identity.manager.email_manager import EmailManager
from spaceone.identity.manager.external_auth_manager import ExternalAuthManager
from spaceone.identity.manager.token_manager.local_token_manager import (
    LocalTokenManager,
)
from spaceone.identity.manager.user_manager import UserManager
from spaceone.identity.model.user.database import User
from spaceone.identity.model.user.request import *
from spaceone.identity.model.user.response import *

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class UserService(BaseService):
    resource = "User"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_mgr = UserManager()
        self.domain_mgr = DomainManager()
        self.domain_secret_mgr = DomainSecretManager()

    @transaction(permission="identity:User.write", role_types=["DOMAIN_ADMIN"])
    @convert_model
    def create(self, params: UserCreateRequest) -> Union[UserResponse, dict]:
        """Create user
        Args:
            params (UserCreateRequest): {
                'user_id': 'str',           # required
                'password': 'str',
                'name': 'str',
                'email': 'str',
                'auth_type': 'str',
                'language': 'str',
                'timezone': 'str',
                'tags': 'dict',
                'reset_password': 'bool',
                'domain_id': 'str',          # injected from auth (required)
                'enforce_mfa_state': 'ENABLED | DISABLED',
                'enforce_mfa_type': 'OTP | EMAIL'    # conditionally required
            }
        Returns:
            UserResponse:
        """

        user_vo = self.create_user(params.dict())
        return UserResponse(**user_vo.to_dict())

    def create_user(self, params: dict) -> User:
        user_id = params["user_id"]
        auth_type = params["auth_type"]
        reset_password = params["reset_password"]
        domain_id = params["domain_id"]
        email = params.get("email")
        language = self._get_domain_default_language(domain_id, params.get("language"))
        params["language"] = language
        params["timezone"] = params.get("timezone", "UTC")
        mfa_enforce = params["enforce_mfa_state"]
        mfa_enforce_type = params["enforce_mfa_type"]

        if mfa_enforce:
            if mfa_enforce_type is None:
                raise ERROR_REQUIRED_PARAMETER(key="mfa.mfa_type")
            else:
                params["mfa"] = {
                    "mfa_type": mfa_enforce_type,
                    "state": "DISABLED",
                    "options": {"enforce": mfa_enforce},
                }
                params["required_actions"] = ["ENFORCE_MFA"]
        else:
            if mfa_enforce_type is not None:
                raise ERROR_INVALID_PARAMETER(
                    key="mfa.mfa_type",
                    reason="Type can only be set when mfa enforce is True.",
                )

        if reset_password:
            self._check_reset_password_eligibility(user_id, auth_type, email)

            email_manager = EmailManager()

            temp_password = self._generate_temporary_password()
            params["password"] = copy.deepcopy(temp_password)
            reset_password_type = config.get_global(
                "RESET_PASSWORD_TYPE", "ACCESS_TOKEN"
            )

            domain_name = self._get_domain_name(domain_id)
            domain_display_name = self._get_domain_display_name(domain_id, domain_name)

            if reset_password_type == "ACCESS_TOKEN":
                identity_conf = config.get_global("IDENTITY", {}) or {}
                token_conf = identity_conf.get("token", {})
                timeout = token_conf.get("invite_token_timeout", 604800)

                token = self._issue_temporary_token(user_id, domain_id, timeout)
                reset_password_link = self._get_console_sso_url(
                    domain_name, token["access_token"]
                )

                params.get("required_actions", []).append("UPDATE_PASSWORD")

                user_vo = self.user_mgr.create_user(params)
                user_id = user_vo.user_id
                email_manager.send_reset_password_email_when_user_added(
                    domain_display_name, user_id, email, reset_password_link, language
                )
            else:
                console_link = self._get_console_url(domain_name)

                user_vo = self.user_mgr.create_user(params)
                user_id = user_vo.user_id

                email_manager.send_temporary_password_email_when_user_added(
                    domain_display_name,
                    user_id,
                    email,
                    console_link,
                    temp_password,
                    language,
                )
        else:
            user_vo = self.user_mgr.create_user(params)
            user_id = user_vo.user_id

            if (
                auth_type == "EXTERNAL"
                and self._check_invite_external_user_eligibility(user_id, user_id)
            ):
                email_mgr = EmailManager()

                domain_name = self._get_domain_name(domain_id)
                domain_display_name = self._get_domain_display_name(
                    domain_id, domain_name
                )

                console_link = self._get_console_url(domain_name)
                external_auth_provider = self._get_external_auth_provider(domain_id)

                email_mgr.send_invite_email_when_external_user_added(
                    domain_display_name,
                    user_id,
                    user_id,
                    console_link,
                    language,
                    external_auth_provider,
                )

        return user_vo

    @transaction(permission="identity:User.write", role_types=["DOMAIN_ADMIN"])
    @convert_model
    def update(self, params: UserUpdateRequest) -> Union[UserResponse, dict]:
        """
        Args:
            params (UserUpdateRequest): {
                'user_id': 'str',           # required
                'password': 'str',
                'name': 'str',
                'email': 'str',
                'language': 'str',
                'timezone': 'str',
                'tags': 'dict',
                'reset_password': 'bool',
                'domain_id': 'str',          # injected from auth (required)
                'enforce_mfa_state': 'ENABLED | DISABLED',
                'enforce_mfa_type': 'OTP | EMAIL'    # conditionally required
            }
        Returns:
            UserResponse:

        """
        user_vo = self.user_mgr.get_user(params.user_id, params.domain_id)
        domain_id = params.domain_id

        update_user_vo = {}
        update_require_actions = list(user_vo.required_actions)

        if params.reset_password:
            domain_name = self._get_domain_name(domain_id)
            user_id = user_vo.user_id
            auth_type = user_vo.auth_type
            email = params.email or user_vo.email
            email_verified = user_vo.email_verified

            language = user_vo.language

            self._check_reset_password_eligibility(user_id, auth_type, email)

            if email_verified is False:
                raise ERROR_VERIFICATION_UNAVAILABLE(user_id=user_id)

            reset_password_type = config.get_global("RESET_PASSWORD_TYPE")
            email_manager = EmailManager()
            temp_password = self._generate_temporary_password()
            update_user_vo["password"] = temp_password

            if "UPDATE_PASSWORD" not in update_require_actions:
                update_require_actions.append("UPDATE_PASSWORD")

            if reset_password_type == "ACCESS_TOKEN":
                token = self._issue_temporary_token(user_id, domain_id)
                reset_password_link = self._get_console_sso_url(
                    domain_name, token["access_token"]
                )

                email_manager.send_reset_password_email(
                    user_id, email, reset_password_link, language
                )
            elif reset_password_type == "PASSWORD":
                console_link = self._get_console_url(domain_name)

                email_manager.send_temporary_password_email(
                    user_id, email, console_link, temp_password, language
                )

        if params.enforce_mfa_state is not None:
            mfa_enforce = params.enforce_mfa_state == "ENABLED"
            mfa_type = params.enforce_mfa_type
            user_vo_mfa = user_vo.mfa.to_dict() if user_vo.mfa else {}
            user_vo_mfa_type = user_vo_mfa.get("mfa_type", None)
            user_vo_mfa_state = user_vo_mfa.get("state", "DISABLED")
            user_vo_mfa_options = user_vo_mfa.get("options", {})

            update_mfa = {
                "state": user_vo_mfa_state,
                "mfa_type": user_vo_mfa_type,
                "options": user_vo_mfa_options,
            }

            if mfa_enforce:
                if mfa_type is None:
                    raise ERROR_REQUIRED_PARAMETER(
                        key="enforce_mfa_type",
                    )
                if mfa_type != user_vo_mfa_type:
                    if user_vo_mfa_type == "OTP":
                        self.__delete_otp_secret(user_vo, domain_id)
                    update_mfa["mfa_type"] = mfa_type
                    update_mfa["state"] = "DISABLED"
                update_mfa["options"] = {"enforce": mfa_enforce}
                update_require_actions.append("ENFORCE_MFA")

            else:
                if mfa_type is not None:
                    raise ERROR_INVALID_PARAMETER(
                        key="mfa.mfa_type",
                        reason="Type can only be set when mfa enforce is True.",
                    )
                update_mfa["options"].pop("enforce", None)
                update_require_actions = [
                    actions
                    for actions in update_require_actions
                    if actions != "ENFORCE_MFA"
                ]

            update_user_vo["mfa"] = update_mfa

        general_params = params.dict(
            exclude_unset=True, exclude={"reset_password", "mfa"}
        )
        update_user_vo.update(general_params)
        update_user_vo["required_actions"] = list(
            set(update_require_actions)
        )

        user_vo = self.user_mgr.update_user_by_vo(update_user_vo, user_vo)

        return UserResponse(**user_vo.to_dict())

    @transaction(permission="identity:User.write", role_types=["DOMAIN_ADMIN"])
    @convert_model
    def verify_email(self, params: UserVerifyEmailRequest) -> None:
        """Verify email

        Args:
            params (UserVerifyEmailRequest): {
                'user_id': 'str',       # required
                'email': 'str',
                'domain_id': 'str'      # injected from auth (required)
            }


        Returns:
            None
        """
        user_id = params.user_id
        domain_id = params.domain_id

        user_vo = self.user_mgr.get_user(user_id, domain_id)

        params = params.dict(exclude_unset=True)
        params.update({"email_verified": True})
        self.user_mgr.update_user_by_vo(params, user_vo)

    @transaction(permission="identity:User.write", role_types=["DOMAIN_ADMIN"])
    @convert_model
    def disable_mfa(self, params: UserDisableMFARequest) -> Union[UserResponse, dict]:
        """Disable MFA

        Args:
            params (UserDisableMFARequest): {
                'user_id': 'str',       # required
                'domain_id': 'str'      # injected from auth (required)
        Returns:
            UserResponse:
        """

        user_id = params.user_id
        domain_id = params.domain_id

        user_vo = self.user_mgr.get_user(user_id, domain_id)
        user_mfa = user_vo.mfa.to_dict() if user_vo.mfa else {}
        mfa_type = user_mfa.get("mfa_type")
        mfa_enforce = user_mfa.get("options", {}).get("enforce", False)

        if (
            user_mfa.get("state", "DISABLED") == "DISABLED" or mfa_type is None
        ) and mfa_enforce is None:
            raise ERROR_MFA_ALREADY_DISABLED(user_id=user_id)

        if mfa_type == "OTP" and user_mfa.get("state", "DISABLED") == "ENABLED":
            self.__delete_otp_secret(user_vo, domain_id)

        update_user_vo: dict = {}
        update_required_actions = set(user_vo.required_actions)

        update_user_vo["mfa"] = {
            "state": "DISABLED",
            "mfa_type": mfa_type,
        }

        if mfa_enforce:
            update_required_actions.add("ENFORCE_MFA")
            update_user_vo["mfa"]["options"] = {"enforce": mfa_enforce}
        else:
            update_required_actions.discard("ENFORCE_MFA")

        update_user_vo["required_actions"] = list(update_required_actions)
        user_vo = self.user_mgr.update_user_by_vo(update_user_vo, user_vo)

        return UserResponse(**user_vo.to_dict())

    @transaction(permission="identity:User.write", role_types=["DOMAIN_ADMIN"])
    @convert_model
    def set_required_actions(
        self, params: UserSetRequiredActionsRequest
    ) -> Union[UserResponse, dict]:
        """Set required actions

        Args:
            params (UserSetRequiredActionsRequest): {
                'user_id': 'str',               # required
                'required_actions': 'list',     # required
                'domain_id': 'str'              # injected from auth (required)
            }
        Returns:
            UserResponse:
        """
        new_actions = params.required_actions or []
        user_vo = self.user_mgr.get_user(params.user_id, params.domain_id)

        if "UPDATE_PASSWORD" in new_actions:
            if user_vo.auth_type == "EXTERNAL":
                raise ERROR_NOT_ALLOWED_ACTIONS(user_id=user_vo.user_id)

        required_actions = list(set(user_vo.required_actions + new_actions))
        user_vo = self.user_mgr.update_user_by_vo(
            {"required_actions": required_actions}, user_vo
        )

        return UserResponse(**user_vo.to_dict())

    @transaction(permission="identity:User.write", role_types=["DOMAIN_ADMIN"])
    @convert_model
    def set_refresh_timeout(
        self, params: UserSetRefreshTimeout
    ) -> Union[UserResponse, dict]:
        """
        Args:
            params (UserProfileSetRefreshTimeout): {
                "user_id": "str",
                "refresh_timeout": "int",
                "domain_id": "str"          # inject from auth
            }
        Returns:
            UserResponse:
        """

        user_id = params.user_id
        domain_id = params.domain_id
        user_vo = self.user_mgr.get_user(user_id, domain_id)

        if user_vo.role_type != "DOMAIN_ADMIN":
            raise ERROR_PERMISSION_DENIED()

        refresh_timeout = self._get_refresh_timeout_from_config(params.refresh_timeout)
        user_vo = self.user_mgr.update_user_by_vo(
            {"refresh_timeout": refresh_timeout}, user_vo
        )

        return UserResponse(**user_vo.to_dict())

    @transaction(permission="identity:User.write", role_types=["DOMAIN_ADMIN"])
    @convert_model
    def delete(self, params: UserDeleteRequest) -> None:
        """Delete user

        Args:
            params (UserDeleteRequest): {
                'user_id': 'str',       # required
                'domain_id': 'str'      # injected from auth (required)
            }

        Returns:
            None
        """
        user_vo = self.user_mgr.get_user(params.user_id, params.domain_id)

        if user_vo.role_type == "DOMAIN_ADMIN" and user_vo.state == "ENABLED":
            self._check_last_admin_user(params.domain_id, user_vo)

        self.user_mgr.delete_user_by_vo(user_vo)

    @transaction(permission="identity:User.write", role_types=["DOMAIN_ADMIN"])
    @convert_model
    def enable(self, params: UserEnableRequest) -> Union[UserResponse, dict]:
        """Enable user

        Args:
            params (UserEnableRequest): {
                'user_id': 'str',       # required
                'domain_id': 'str'      # injected from auth (required)
            }

        Returns:
            UserResponse:
        """

        user_vo = self.user_mgr.get_user(params.user_id, params.domain_id)
        user_vo = self.user_mgr.update_user_by_vo({"state": "ENABLED"}, user_vo)

        return UserResponse(**user_vo.to_dict())

    @transaction(permission="identity:User.write", role_types=["DOMAIN_ADMIN"])
    @convert_model
    def disable(self, params: UserDisableRequest) -> Union[UserResponse, dict]:
        """Disable user
        Args:
            params (dict): {
                'user_id': 'str',       # required
                'domain_id': 'str'      # injected from auth (required)
            }

        Returns:
            UserResponse:
        """

        user_vo = self.user_mgr.get_user(params.user_id, params.domain_id)

        if user_vo.role_type == "DOMAIN_ADMIN" and user_vo.state == "ENABLED":
            self._check_last_admin_user(params.domain_id, user_vo)

        user_vo = self.user_mgr.update_user_by_vo({"state": "DISABLED"}, user_vo)
        return UserResponse(**user_vo.to_dict())

    @transaction(permission="identity:User.read", role_types=["DOMAIN_ADMIN"])
    @convert_model
    def get(self, params: UserGetRequest) -> Union[UserResponse, dict]:
        """Get user

        Args:
            params (dict): {
                'user_id': 'str',       # required
                'domain_id': 'str'      # injected from auth (required)
            }

        Returns:
            UserResponse:
        """

        user_vo = self.user_mgr.get_user(params.user_id, params.domain_id)
        return UserResponse(**user_vo.to_dict())

    @transaction(permission="identity:User.read", role_types=["DOMAIN_ADMIN"])
    @append_query_filter(
        ["user_id", "state", "auth_type", "role_type", "domain_id", "name", "email"]
    )
    @append_keyword_filter(["user_id", "name", "email"])
    @convert_model
    def list(self, params: UserSearchQueryRequest) -> Union[UsersResponse, dict]:
        """List users
        Args:
            params (UserSearchQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.Query)',
                'user_id': 'str',
                'name': 'str',
                'state': 'str',
                'email': 'str',
                'auth_type': 'str',
                'domain_id': 'str'      # injected from auth (required)
            }
        Returns:
            UsersResponse:
        """

        query = params.query or {}
        user_vos, total_count = self.user_mgr.list_users(query)

        users_info = [user_vo.to_dict() for user_vo in user_vos]
        return UsersResponse(results=users_info, total_count=total_count)

    @transaction(permission="identity:User.read", role_types=["DOMAIN_ADMIN"])
    @append_query_filter(["domain_id"])
    @append_keyword_filter(["user_id", "name", "email"])
    @convert_model
    def stat(self, params: UserStatQueryRequest) -> dict:
        """stat users

        Args:
            params (UserStatQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)', # required
                'domain_id': 'str',         # injected from auth (required)
            }

        Returns:
            dict: {
                'results': 'list',
                'total_count': 'int'
            }

        """

        query = params.query or {}
        return self.user_mgr.stat_users(query)

    def _get_domain_name(self, domain_id: str) -> str:
        domain_vo = self.domain_mgr.get_domain(domain_id)
        return domain_vo.name

    def _issue_temporary_token(
        self,
        user_id: str,
        domain_id: str,
        timeout: int = None,
        injected_params: dict = None,
    ) -> dict:
        if timeout is None:
            identity_conf = config.get_global("IDENTITY", {}) or {}
            token_conf = identity_conf.get("token", {})
            timeout = token_conf.get("temporary_token_timeout", 86400)

        private_jwk = self.domain_secret_mgr.get_domain_private_key(domain_id=domain_id)

        local_token_manager = LocalTokenManager()
        return local_token_manager.issue_temporary_token(
            user_id,
            domain_id,
            private_jwk,
            timeout=timeout,
            injected_params=injected_params,
        )

    @staticmethod
    def _get_console_sso_url(domain_name: str, token: str) -> str:
        console_domain = config.get_global("EMAIL_CONSOLE_DOMAIN")
        console_domain = console_domain.format(domain_name=domain_name)

        return f"{console_domain}?sso_access_token={token}"

    def _check_last_admin_user(self, domain_id: str, user_vo: User) -> None:
        user_vos = self.user_mgr.filter_users(
            domain_id=domain_id, state="ENABLED", role_type="DOMAIN_ADMIN"
        )

        if user_vos.count() == 1:
            raise ERROR_LAST_ADMIN_CANNOT_DISABLED_DELETED(user_id=user_vo.user_id)

    @staticmethod
    def _get_console_url(domain_name: str) -> str:
        console_domain = config.get_global("EMAIL_CONSOLE_DOMAIN")
        return console_domain.format(domain_name=domain_name)

    @staticmethod
    def _check_reset_password_eligibility(user_id: str, auth_type: str, email: str):
        if auth_type == "EXTERNAL":
            raise ERROR_UNABLE_TO_RESET_PASSWORD_IN_EXTERNAL_AUTH(user_id=user_id)
        elif not email:
            raise ERROR_UNABLE_TO_RESET_PASSWORD_WITHOUT_EMAIL(user_id=user_id)

    @staticmethod
    def _generate_temporary_password():
        while True:
            random_password = "".join(
                secrets.choice(
                    string.ascii_uppercase + string.ascii_lowercase + string.digits
                )
                for _ in range(12)
            )
            if (
                re.search("[a-z]", random_password)
                and re.search("[A-Z]", random_password)
                and re.search("[0-9]", random_password)
            ):
                return random_password

    @staticmethod
    def _check_invite_external_user_eligibility(user_id: str, email: str) -> bool:
        rule = r"[^@]+@[^@]+\.[^@]+"

        if email is None:
            _LOGGER.debug(
                f"[_check_invite_external_user_eligibility] email is None (user_id={user_id})"
            )
            return False

        if not re.match(rule, email):
            _LOGGER.debug(
                f"[_check_invite_external_user_eligibility] email format is incorrect (user_id={user_id}, email={email})"
            )
            return False

        return True

    @staticmethod
    def _get_external_auth_provider(domain_id: str) -> str:
        external_auth_mgr = ExternalAuthManager()
        external_auth_vo = external_auth_mgr.get_external_auth(domain_id)
        plugin_info_metadata = external_auth_vo.plugin_info.get("metadata", {})
        identity_provider = plugin_info_metadata.get("identity_provider", "EXTERNAL")
        return identity_provider

    @staticmethod
    def _get_domain_default_language(domain_id: str, language: str = None) -> str:
        if not language:
            config_mgr = ConfigManager()
            domain_config_data_info = config_mgr.get_auth_config(domain_id)
            settings = domain_config_data_info.get("settings", {})
            if settings:
                language = settings.get("language", "en")
            else:
                language = "en"
        return language

    @staticmethod
    def _get_domain_display_name(domain_id: str, domain_name: str) -> str:
        config_mgr = ConfigManager()
        domain_config_data_info = config_mgr.get_auth_config(domain_id)
        settings = domain_config_data_info.get("settings", {})
        domain_display_name = settings.get("display_name", "")

        if not domain_display_name:
            domain_display_name = domain_name

        return domain_display_name

    @staticmethod
    def _get_refresh_timeout_from_config(refresh_timeout: int) -> int:
        identity_conf = config.get_global("IDENTITY") or {}
        token_conf = identity_conf.get("token", {})
        config_refresh_timeout = token_conf.get("refresh_timeout")
        if refresh_timeout < config_refresh_timeout:
            raise ERROR_INVALID_PARAMETER(
                key="refresh_timeout",
                reason=f"Minimum value for refresh_timeout is {config_refresh_timeout}",
            )
        refresh_timeout = max(refresh_timeout, config_refresh_timeout)

        config_admin_refresh_max_timeout = token_conf.get(
            "admin_refresh_max_timeout", 2419200
        )
        refresh_timeout = min(refresh_timeout, config_admin_refresh_max_timeout)

        return refresh_timeout

    def __delete_otp_secret(self, user_vo: User, domain_id: str):
        user_vo_mfa = user_vo.mfa.to_dict() if user_vo.mfa else {}
        user_vo_mfa_options = user_vo_mfa.get("options", {})

        user_secret_id: Union[str, None] = user_vo_mfa_options.get(
            "user_secret_id", None
        )
        if user_secret_id is not None:
            secret_manager: SecretManager = self.locator.get_manager(SecretManager)
            secret_manager.delete_user_secret_with_system_token(
                domain_id, user_secret_id
            )
