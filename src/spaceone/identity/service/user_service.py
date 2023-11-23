import logging
import pytz
import random
import re
import string
from typing import Union, List

from spaceone.core.service import (
    BaseService,
    transaction,
    convert_model,
    append_query_filter,
    append_keyword_filter,
)
from spaceone.core import config

from spaceone.identity.error.error_mfa import *
from spaceone.identity.error.error_user import *
from spaceone.identity.manager.email_manager import EmailManager
from spaceone.identity.model.domain.database import Domain
from spaceone.identity.manager.domain_manager import DomainManager
from spaceone.identity.manager.domain_secret_manager import DomainSecretManager
from spaceone.identity.manager.mfa_manager import MFAManager
from spaceone.identity.manager.token_manager.local_token_manager import (
    LocalTokenManager,
)
from spaceone.identity.manager.user_manager import UserManager
from spaceone.identity.model.user.request import *
from spaceone.identity.model.user.response import *

_LOGGER = logging.getLogger(__name__)


class UserService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_mgr = UserManager()
        self.domain_mgr = DomainManager()
        self.domain_secret_mgr = DomainSecretManager()

    @transaction(append_meta={"authorization.scope": "DOMAIN_OR_WORKSPACE"})
    @convert_model
    def create(self, params: UserCreateRequest) -> Union[UserResponse, dict]:
        """Create user
        Args:
            params (dict): {
                'user_id': 'str', # required
                'password': 'str',
                'name': 'str',
                'email': 'str',
                'user_type': 'str', # required
                'auth_type': 'str',
                'language': 'str',
                'timezone': 'str',
                'tags': 'dict',
                'reset_password': 'bool',
                'role_binding': 'dict',
                'domain_id': 'str' # required
            }
        Returns:
            UserResponse:
        """

        user_id = params.user_id
        email = params.email
        params.user_type = params.user_type or "USER"
        params.auth_type = params.auth_type or "LOCAL"
        reset_password = params.reset_password or False
        domain_id = params.domain_id

        domain_vo = self.domain_mgr.get_domain(domain_id)

        default_language = self._get_default_config(domain_vo, "LANGUAGE")
        default_timezone = self._get_default_config(domain_vo, "TIMEZONE")

        self._check_user_type_and_auth_type(params.user_type, params.auth_type)

        if "language" not in params:
            params.language = default_language

        if "timezone" not in params:
            params.timezone = default_timezone

        if "timezone" in params:
            self._check_timezone(params.timezone)

        if reset_password:
            self._check_reset_password_eligibility(user_id, params.auth_type, email)

            email_manager = EmailManager()
            language = params.language
            required_actions = {"required_actions": ["UPDATE_PASSWORD"]}
            params.password = self._generate_temporary_password()

            reset_password_type = config.get_global("RESET_PASSWORD_TYPE")
            if reset_password_type == "ACCESS_TOKEN":
                token = self._issue_temporary_token(user_id, domain_id)
                reset_password_link = self._get_console_sso_url(
                    domain_id, token["access_token"]
                )

                params = params.dict()
                params.update(required_actions)

                user_vo = self.user_mgr.create_user(params, domain_vo)
                email_manager.send_reset_password_email_when_user_added(
                    user_id, email, reset_password_link, language
                )
            else:
                temp_password = params.password
                console_link = self._get_console_url(domain_id)

                user_vo = self.user_mgr.create_user(params.dict(), domain_vo)
                email_manager.send_temporary_password_email_when_user_added(
                    user_id, email, console_link, temp_password, language
                )
        else:
            user_vo = self.user_mgr.create_user(params.dict(), domain_vo)

        return UserResponse(**user_vo.to_dict())

    @transaction(append_meta={"authorization.scope": "DOMAIN_OR_USER"})
    @convert_model
    def update(self, params: UserUpdateRequest) -> Union[UserResponse, dict]:
        """
        Args:
            params (dict): {
                'user_id': 'str',
                'password': 'str',
                'name': 'str',
                'email': 'str',
                'language': 'str',
                'timezone': 'str',
                'tags': 'dict',
                'reset_password': 'bool',
                'domain_id': 'str'
            }
        Returns:
            UserResponse:

        """

        if "timezone" in params:
            self._check_timezone(params.timezone)

        user_vo = self.user_mgr.get_user(params.user_id, params.domain_id)

        if params.reset_password:
            domain_id = params.domain_id
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
            params.password = temp_password

            user_vo = self.user_mgr.update_user_by_vo(
                params.dict(exclude_unset=True), user_vo
            )
            user_vo = self.user_mgr.update_user_by_vo(
                {"required_actions": ["UPDATE_PASSWORD"]}, user_vo
            )

            if reset_password_type == "ACCESS_TOKEN":
                token = self._issue_temporary_token(user_id, domain_id)
                reset_password_link = self._get_console_sso_url(
                    domain_id, token["access_token"]
                )

                email_manager.send_reset_password_email(
                    user_id, email, reset_password_link, language
                )
            elif reset_password_type == "PASSWORD":
                console_link = self._get_console_url(domain_id)

                email_manager.send_temporary_password_email(
                    user_id, email, console_link, temp_password, language
                )
        else:
            user_vo = self.user_mgr.update_user_by_vo(
                params.dict(exclude_unset=True), user_vo
            )

        return UserResponse(**user_vo.to_dict())

    @transaction(append_meta={"authorization.scope": "DOMAIN_OR_USER"})
    @convert_model
    def verify_email(self, params: UserVerifyEmailRequest) -> None:
        """Verify email

        Args:
            params (dict): {
                'user_id': 'str',
                'email': 'str',
                'force': 'bool',
                'domain_id': 'str'
            }


        Returns:
            None
        """
        user_id = params.user_id
        domain_id = params.domain_id

        user_vo = self.user_mgr.get_user(user_id, domain_id)
        email = params.email or user_vo.email
        force = params.force or False

        params = params.dict(exclude_unset=True)
        if force:
            params.update({"email_verified": True})
            self.user_mgr.update_user_by_vo(params, user_vo)
        else:
            params.update({"email_verified": False})
            user_vo = self.user_mgr.update_user_by_vo(params, user_vo)

            token_manager = LocalTokenManager()
            verify_code = token_manager.create_verify_code(user_id, domain_id)

            email_manager = EmailManager()
            email_manager.send_verification_email(
                user_id, email, verify_code, user_vo.language
            )

    @transaction(append_meta={"authorization.scope": "DOMAIN_OR_USER"})
    @convert_model
    def confirm_email(
        self, params: UserConfirmEmailRequest
    ) -> Union[UserResponse, dict]:
        """Confirm email

        Args:
            params (dict): {
                'user_id': 'str',
                'verify_code': 'str',
                'domain_id': 'str'
            }


        Returns:
            UserResponse:
        """

        user_id = params.user_id
        domain_id = params.domain_id
        verify_code = params.verify_code

        token_manager = LocalTokenManager()
        if token_manager.check_verify_code(user_id, domain_id, verify_code):
            user_vo = self.user_mgr.get_user(user_id, domain_id)

            params = params.dict(exclude_unset=True)
            params["email_verified"] = True
            user_vo = self.user_mgr.update_user_by_vo(params, user_vo)
            return UserResponse(**user_vo.to_dict())
        else:
            raise ERROR_INVALID_VERIFY_CODE(verify_code=verify_code)

    @transaction
    @convert_model
    def reset_password(self, params: UserResetPasswordRequest) -> None:
        """Reset password

        Args:
            params (dict): {
                'user_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            None
        """

        user_id = params.user_id
        domain_id = params.domain_id

        user_vo = self.user_mgr.get_user(user_id, domain_id)
        auth_type = user_vo.auth_type
        email = user_vo.email
        language = user_vo.language

        self._check_reset_password_eligibility(user_id, auth_type, email)

        if user_vo.email_verified is False:
            raise ERROR_VERIFICATION_UNAVAILABLE(user_id=user_id)

        reset_password_type = config.get_global("RESET_PASSWORD_TYPE", "ACCESS_TOKEN")
        email_manager = EmailManager()
        if reset_password_type == "ACCESS_TOKEN":
            token = self._issue_temporary_token(user_id, domain_id)
            reset_password_link = self._get_console_sso_url(
                domain_id, token["access_token"]
            )
            email_manager.send_reset_password_email(
                user_id, email, reset_password_link, language
            )

        elif reset_password_type == "PASSWORD":
            temp_password = self._generate_temporary_password()
            self.user_mgr.update_user_by_vo({"password": temp_password}, user_vo)
            self.user_mgr.update_user_by_vo(
                {"required_actions": ["UPDATE_PASSWORD"]}, user_vo
            )
            console_link = self._get_console_url(domain_id)
            email_manager.send_temporary_password_email(
                user_id, email, console_link, temp_password, language
            )

    @transaction(append_meta={"authorization.scope": "DOMAIN"})
    @convert_model
    def set_required_actions(
        self, params: UserSetRequiredActionsRequest
    ) -> Union[UserResponse, dict]:
        return {}

    @transaction(append_meta={"authorization.scope": "USER"})
    @convert_model
    def enable_mfa(self, params: UserEnableMFARequest) -> Union[UserResponse, dict]:
        """Enable MFA

        Args:
            params (UserEnableMFARequest): {
                'user_id': 'str',
                'mfa_type': 'str',
                'options': 'dict',
                'domain_id': 'str'
            }
        Returns:
            UserResponse:
        """
        user_id = params.user_id
        mfa_type = params.mfa_type
        options = params.options
        domain_id = params.domain_id

        user_vo = self.user_mgr.get_user(user_id, domain_id)
        user_mfa = user_vo.mfa.to_dict() if user_vo.mfa else {}

        if not options:
            raise ERROR_REQUIRED_PARAMETER(key="options")

        if user_mfa.get("state", "DISABLED") == "ENABLED":
            raise ERROR_MFA_ALREADY_ENABLED(user_id=user_id)

        mfa_manager = MFAManager.get_manager_by_mfa_type(mfa_type)

        if mfa_type == "EMAIL":
            user_mfa["mfa_type"] = mfa_type
            user_mfa["options"] = options
            user_mfa["state"] = user_mfa.get("state", "DISABLED")
            mfa_manager.enable_mfa(user_id, domain_id, user_mfa, user_vo.language)
            user_vo = self.user_mgr.update_user_by_vo({"mfa": user_mfa}, user_vo)
        else:
            raise ERROR_NOT_SUPPORTED_MFA_TYPE(support_mfa_types=["EMAIL"])

        return UserResponse(**user_vo.to_dict())

    @transaction(append_meta={"authorization.scope": "DOMAIN_OR_USER"})
    @convert_model
    def disable_mfa(self, params: UserDisableMFARequest) -> Union[UserResponse, dict]:
        """Disable MFA

        Args:
            params (dict): {
                'user_id': 'str',
                'force': 'bool',
                'domain_id': 'str'
        Returns:
            Empty:
        """

        user_id = params.user_id
        domain_id = params.domain_id
        force = params.force or False

        user_vo = self.user_mgr.get_user(user_id, domain_id)
        user_mfa = user_vo.mfa.to_dict() if user_vo.mfa else {}
        mfa_type = user_mfa.get("mfa_type")

        if user_mfa.get("state", "DISABLED") == "DISABLED" or mfa_type is None:
            raise ERROR_MFA_ALREADY_DISABLED(user_id=user_id)

        mfa_manager = MFAManager.get_manager_by_mfa_type(mfa_type)

        if force:
            user_mfa = {"state": "DISABLED"}
            self.user_mgr.update_user_by_vo({"mfa": user_mfa}, user_vo)
        elif mfa_type == "EMAIL":
            mfa_manager.disable_mfa(user_id, domain_id, user_mfa, user_vo.language)

        return UserResponse(**user_vo.to_dict())

    @transaction(append_meta={"authorization.scope": "USER"})
    @convert_model
    def confirm_mfa(self, params: UserConfirmMFARequest) -> Union[UserResponse, dict]:
        """Confirm MFA
        Args:
            params (dict): {
                'user_id': 'str',
                'verify_code': 'str',
                'domain_id': 'str'
        Returns:
            Empty:
        """

        user_id = params.user_id
        domain_id = params.domain_id
        verify_code = params.verify_code

        user_vo = self.user_mgr.get_user(user_id, domain_id)
        mfa_type = user_vo.mfa.mfa_type

        if not mfa_type:
            raise ERROR_MFA_NOT_ENABLED(user_id=user_id)

        mfa_manager = MFAManager.get_manager_by_mfa_type(mfa_type)

        if mfa_type == "EMAIL":
            if mfa_manager.confirm_mfa(user_id, domain_id, verify_code):
                user_mfa = user_vo.mfa.to_dict() if user_vo.mfa else {}
                if user_mfa.get("state", "DISABLED") == "ENABLED":
                    user_mfa = {"state": "DISABLED"}
                elif user_mfa.get("state", "DISABLED") == "DISABLED":
                    user_mfa["state"] = "ENABLED"
                self.user_mgr.update_user_by_vo({"mfa": user_mfa}, user_vo)
            else:
                raise ERROR_INVALID_VERIFY_CODE(verify_code=verify_code)
        return UserResponse(**user_vo.to_dict())

    @transaction(append_meta={"authorization.scope": "DOMAIN"})
    @convert_model
    def delete(self, params: UserDeleteRequest) -> None:
        """Delete user

        Args:
            params (dict): {
                'user_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            None
        """
        user_vo = self.user_mgr.get_user(params.user_id, params.domain_id)
        # todo : check this user is last admin
        self.user_mgr.delete_user_by_vo(user_vo)

    @transaction(append_meta={"authorization.scope": "DOMAIN"})
    @convert_model
    def enable(self, params: UserEnableRequest) -> Union[UserResponse, dict]:
        """Enable user

        Args:
            params (dict): {
                'user_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            user_vo (object)
        """
        user_vo = self.user_mgr.get_user(params.user_id, params.domain_id)
        user_vo = self.user_mgr.enable_user(user_vo)
        return UserResponse(**user_vo.to_dict())

    @transaction(append_meta={"authorization.scope": "DOMAIN"})
    @convert_model
    def disable(self, params: UserDisableRequest) -> Union[UserResponse, dict]:
        """Disable user
        Args:
            params (dict): {
                'user_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            UserResponse:
        """

        user_vo = self.user_mgr.get_user(params.user_id, params.domain_id)
        user_vo = self.user_mgr.disable_user(user_vo)
        # todo : check this user is last admin
        return UserResponse(**user_vo.to_dict())

    @transaction(append_meta={"authorization.scope": "DOMAIN_READ"})
    @convert_model
    def get(self, params: UserGetRequest) -> Union[UserResponse, dict]:
        """Get user

        Args:
            params (dict): {
                'user_id': 'str', # required
                'domain_id': 'str' # required
            }

        Returns:
            user_vo (object)
        """
        user_vo = self.user_mgr.get_user(params.user_id, params.domain_id)
        return UserResponse(**user_vo.to_dict())

    @transaction(append_meta={"authorization.scope": "DOMAIN_READ"})
    @append_query_filter(
        [
            "user_id",
            "name",
            "state",
            "email",
            "user_type",
            "auth_type",
            "workspace_id",
            "domain_id",
        ]
    )
    @append_keyword_filter(["user_id", "name", "email"])
    @convert_model
    def list(self, params: UserSearchQueryRequest) -> Union[UsersResponse, dict]:
        """List users
        Args:
            params (dict): {
                'query': 'dict',
                'user_id': 'str',
                'name': 'str',
                'state': 'str',
                'email': 'str',
                'user_type': 'str',
                'auth_type': 'str',
                'workspace_id': 'str',
                'domain_id': 'str'
            }
        Returns:
            UsersResponse:
        """
        query = params.query or {}

        user_vos, total_count = self.user_mgr.list_users(query)
        users_info = [user_vo.to_dict() for user_vo in user_vos]
        return UsersResponse(results=users_info, total_count=total_count)

    @transaction(append_meta={"authorization.scope": "DOMAIN_READ"})
    @convert_model
    def stat(self, params: UserStatQueryRequest) -> dict:
        return {}

    def _get_domain_name(self, domain_id: str) -> str:
        domain_vo = self.domain_mgr.get_domain(domain_id)
        return domain_vo.name

    def _issue_temporary_token(self, user_id: str, domain_id: str) -> dict:
        identity_conf = config.get_global("identity") or {}
        timeout = identity_conf.get("temporary_token_timeout", 86400)

        private_jwk = self.domain_secret_mgr.get_domain_private_key(domain_id=domain_id)

        local_token_manager = LocalTokenManager()
        return local_token_manager.issue_temporary_token(
            user_id, domain_id, private_jwk=private_jwk, timeout=timeout
        )

    def _get_console_sso_url(self, domain_id: str, token: str) -> str:
        domain_name = self._get_domain_name(domain_id)

        console_domain = config.get_global("EMAIL_CONSOLE_DOMAIN")
        console_domain = console_domain.format(domain_name=domain_name)

        return f"{console_domain}?sso_access_token={token}"

    def _get_console_url(self, domain_id):
        domain_name = self._get_domain_name(domain_id)

        console_domain = config.get_global("EMAIL_CONSOLE_DOMAIN")
        return console_domain.format(domain_name=domain_name)

    @staticmethod
    def _get_default_config(vo: Domain, item: str) -> str:
        # todo : should be developed later
        DEFAULT = {"TIMEZONE": "UTC", "LANGUAGE": "en"}
        return DEFAULT.get(item)

    @staticmethod
    def _check_timezone(timezone):
        if timezone not in pytz.all_timezones:
            raise ERROR_INVALID_PARAMETER(key="timezone", reason="Timezone is invalid.")

    @staticmethod
    def _check_user_type_and_auth_type(user_type, auth_type):
        # Check User Type and Backend
        if user_type == "API_USER":
            if auth_type == "EXTERNAL":
                raise ERROR_EXTERNAL_USER_NOT_ALLOWED_API_USER()

        # Check External Authentication from Domain
        if auth_type == "EXTERNAL":
            # todo : should be developed later
            raise ERROR_NOT_ALLOWED_EXTERNAL_AUTHENTICATION()

    @staticmethod
    def _check_reset_password_eligibility(user_id, auth_type, email):
        if auth_type == "EXTERNAL":
            raise ERROR_UNABLE_TO_RESET_PASSWORD_IN_EXTERNAL_AUTH(user_id=user_id)
        elif email is None:
            raise ERROR_UNABLE_TO_RESET_PASSWORD_WITHOUT_EMAIL(user_id=user_id)

    @staticmethod
    def _generate_temporary_password():
        while True:
            random_password = "".join(
                random.choice(
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
