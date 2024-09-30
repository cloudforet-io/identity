import logging
import random
import re
import string
from typing import Dict, List, Union

from spaceone.core import config
from spaceone.core.service import *
from spaceone.core.service.utils import *

from spaceone.identity.error.error_mfa import *
from spaceone.identity.error.error_user import *
from spaceone.identity.manager.domain_manager import DomainManager
from spaceone.identity.manager.domain_secret_manager import DomainSecretManager
from spaceone.identity.manager.email_manager import EmailManager
from spaceone.identity.manager.mfa_manager.base import MFAManager
from spaceone.identity.manager.role_binding_manager import RoleBindingManager
from spaceone.identity.manager.role_manager import RoleManager
from spaceone.identity.manager.token_manager.local_token_manager import (
    LocalTokenManager,
)
from spaceone.identity.manager.user_manager import UserManager
from spaceone.identity.manager.workspace_group_manager import WorkspaceGroupManager
from spaceone.identity.manager.workspace_manager import WorkspaceManager
from spaceone.identity.model.user.database import User
from spaceone.identity.model.user.response import *
from spaceone.identity.model.user_profile.request import *
from spaceone.identity.model.user_profile.request import (
    UserProfileGetWorkspaceGroupsRequest,
)
from spaceone.identity.model.user_profile.response import (
    MyWorkspaceGroupsResponse,
    MyWorkspacesResponse,
)
from spaceone.identity.service.workspace_group_service import WorkspaceGroupService

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class UserProfileService(BaseService):
    resource = "UserProfile"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_mgr = UserManager()
        self.domain_mgr = DomainManager()
        self.domain_secret_mgr = DomainSecretManager()
        self.workspace_group_mgr = WorkspaceGroupManager()
        self.workspace_group_svc = WorkspaceGroupService()

    @transaction(permission="identity:UserProfile.write", role_types=["USER"])
    @convert_model
    def update(self, params: UserProfileUpdateRequest) -> Union[UserResponse, dict]:
        """
        Args:
            params (UserProfileUpdateRequest): {
                'password': 'str',
                'name': 'str',
                'email': 'str',
                'language': 'str',
                'timezone': 'str',
                'tags': 'dict',
                'user_id': 'str',           # injected from auth (required)
                'domain_id': 'str'          # injected from auth (required)
            }
        Returns:
            UserResponse:

        """

        user_vo = self.user_mgr.get_user(params.user_id, params.domain_id)

        user_vo = self.user_mgr.update_user_by_vo(
            params.dict(exclude_unset=True), user_vo
        )

        return UserResponse(**user_vo.to_dict())

    @transaction(permission="identity:UserProfile.write", role_types=["USER"])
    @convert_model
    def verify_email(self, params: UserProfileVerifyEmailRequest) -> None:
        """Verify email

        Args:
            params (UserProfileVerifyEmailRequest): {
                'email': 'str',
                'user_id': 'str',       # injected from auth (required)
                'domain_id': 'str'      # injected from auth (required)
            }


        Returns:
            None
        """
        user_id = params.user_id
        domain_id = params.domain_id

        user_vo = self.user_mgr.get_user(user_id, domain_id)
        email = params.email or user_vo.email

        params = params.dict(exclude_unset=True)
        params.update({"email_verified": False})
        user_vo = self.user_mgr.update_user_by_vo(params, user_vo)

        token_manager = LocalTokenManager()
        verify_code = token_manager.create_verify_code(user_id, domain_id)

        email_manager = EmailManager()
        email_manager.send_verification_email(
            user_id, email, verify_code, user_vo.language
        )

    @transaction(permission="identity:UserProfile.write", role_types=["USER"])
    @convert_model
    def confirm_email(
        self, params: UserProfileConfirmEmailRequest
    ) -> Union[UserResponse, dict]:
        """Confirm email

        Args:
            params (UserProfileConfirmEmailRequest): {
                'verify_code': 'str',       # required
                'user_id': 'str',           # injected from auth (required)
                'd  'domain_id': 'str'          # injected from auth (required)
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

    @transaction(exclude=["authentication", "authorization", "mutation"])
    @convert_model
    def reset_password(self, params: UserProfileResetPasswordRequest) -> None:
        """Reset password

        Args:
            params (UserResetPasswordRequest): {
                'user_id': 'str',       # required
                'domain_id': 'str'      # required
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

    @transaction(permission="identity:UserProfile.write", role_types=["USER"])
    @convert_model
    def enable_mfa(
        self, params: UserProfileEnableMFARequest
    ) -> Union[UserResponse, dict]:
        """Enable MFA

        Args:
            params (UserEnableMFARequest):
                'mfa_type': 'str',      # required
                'options': 'dict',      # required
                'user_id': 'str',       # injected from auth (required)
                'domain_id': 'str'      # injected from auth (required)
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

    @transaction(permission="identity:UserProfile.write", role_types=["USER"])
    @convert_model
    def disable_mfa(
        self, params: UserProfileDisableMFARequest
    ) -> Union[UserResponse, dict]:
        """Disable MFA

        Args:
            params (UserDisableMFARequest): {
                'user_id': 'str',       # injected from auth (required)
                'domain_id': 'str'      # injected from auth (required)
        Returns:
            UserResponse:
        """

        user_id = params.user_id
        domain_id = params.domain_id

        user_vo = self.user_mgr.get_user(user_id, domain_id)
        user_mfa = user_vo.mfa.to_dict() if user_vo.mfa else {}
        mfa_type = user_mfa.get("mfa_type")

        if user_mfa.get("state", "DISABLED") == "DISABLED" or mfa_type is None:
            raise ERROR_MFA_ALREADY_DISABLED(user_id=user_id)

        mfa_manager = MFAManager.get_manager_by_mfa_type(mfa_type)
        mfa_manager.disable_mfa(user_id, domain_id, user_mfa, user_vo.language)

        return UserResponse(**user_vo.to_dict())

    @transaction(permission="identity:UserProfile.write", role_types=["USER"])
    @convert_model
    def confirm_mfa(
        self, params: UserProfileConfirmMFARequest
    ) -> Union[UserResponse, dict]:
        """Confirm MFA
        Args:
            params (UserConfirmMFARequest): {
                'verify_code': 'str',       # required
                'user_id': 'str',           # injected from auth (required)
                'domain_id': 'str'          # injected from auth (required)
        Returns:
            UserResponse:
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
            credentials = {
                "user_id": user_id,
                "domain_id": domain_id,
            }
            if mfa_manager.confirm_mfa(credentials, verify_code):
                user_mfa = user_vo.mfa.to_dict() if user_vo.mfa else {}
                if user_mfa.get("state", "DISABLED") == "ENABLED":
                    user_mfa = {"state": "DISABLED"}
                elif user_mfa.get("state", "DISABLED") == "DISABLED":
                    user_mfa["state"] = "ENABLED"
                self.user_mgr.update_user_by_vo({"mfa": user_mfa}, user_vo)
            else:
                raise ERROR_INVALID_VERIFY_CODE(verify_code=verify_code)
        return UserResponse(**user_vo.to_dict())

    @transaction(permission="identity:UserProfile.read", role_types=["USER"])
    @convert_model
    def get(self, params: UserProfileGetRequest) -> Union[UserResponse, dict]:
        """Get user

        Args:
            params (dict): {
                'user_id': 'str',       # injected from auth (required)
                'domain_id': 'str'      # injected from auth (required)
            }

        Returns:
            UserResponse:
        """

        user_vo = self.user_mgr.get_user(params.user_id, params.domain_id)
        return UserResponse(**user_vo.to_dict())

    @transaction(permission="identity:UserProfile.read", role_types=["USER"])
    @convert_model
    def get_workspaces(
        self, params: UserProfileGetWorkspacesRequest
    ) -> Union[MyWorkspacesResponse, dict]:
        """Find user
        Args:
            params (UserWorkspacesRequest): {
                'workspace_group_id': 'str'
                'user_id': 'str',       # injected from auth (required)
                'domain_id': 'str'      # injected from auth (required)
            }
        Returns:
            MyWorkspaceResponse:
        """

        workspace_group_id = params.workspace_group_id
        user_id = params.user_id
        domain_id = params.domain_id

        role_mgr = RoleManager()
        rb_mgr = RoleBindingManager()
        workspace_mgr = WorkspaceManager()
        allow_all = False

        user_vo = self.user_mgr.get_user(user_id, domain_id)

        if user_vo.role_type == "DOMAIN_ADMIN":
            allow_all = True

        conditions = {
            "user_id": user_id,
            "domain_id": domain_id,
            "role_type": ["WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
        }

        if workspace_group_id:
            conditions["workspace_group_id"] = workspace_group_id

        rb_vos = rb_mgr.filter_role_bindings(**conditions)

        workspace_filter_conditions = {"domain_id": domain_id, "state": "ENABLED"}
        if allow_all:
            if workspace_group_id:
                workspace_filter_conditions["workspace_group_id"] = workspace_group_id

            workspace_vos = workspace_mgr.filter_workspaces(
                **workspace_filter_conditions
            )
        else:
            workspace_ids = list(set([rb.workspace_id for rb in rb_vos]))
            workspace_filter_conditions["workspace_id"] = workspace_ids
            workspace_vos = workspace_mgr.filter_workspaces(
                **workspace_filter_conditions
            )

        role_vos = role_mgr.filter_roles(
            domain_id=domain_id,
            role_type=["WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
        )

        role_name_map = {role_vo.role_id: role_vo.name for role_vo in role_vos}
        role_bindings_info_map = {rb.workspace_id: rb.to_dict() for rb in rb_vos}

        workspaces_info = [workspace_vo.to_dict() for workspace_vo in workspace_vos]
        my_workspaces_info = self._get_my_workspaces_info(
            workspaces_info, role_name_map, role_bindings_info_map
        )

        return MyWorkspacesResponse(
            results=my_workspaces_info, total_count=len(my_workspaces_info)
        )

    # my_workspaces_info = self._get_my_workspaces_info(workspaces_info, role_bindings_info_map)

    @transaction(permission="identity:UserProfile.read", role_types=["USER"])
    @convert_model
    def get_workspace_groups(
        self, params: UserProfileGetWorkspaceGroupsRequest
    ) -> Union[MyWorkspaceGroupsResponse, dict]:
        """Find user
        Args:
            params (UserWorkspacesRequest): {
                'user_id': 'str',       # injected from auth (required)
                'domain_id': 'str'      # injected from auth (required)
            }
        Returns:
            MyWorkspaceResponse:
        """
        rb_mgr = RoleBindingManager()
        allow_all = False

        user_vo = self.user_mgr.get_user(params.user_id, params.domain_id)

        if user_vo.role_type == "DOMAIN_ADMIN":
            allow_all = True

        if allow_all:
            workspace_group_vos = self.workspace_group_mgr.filter_workspace_groups(
                domain_id=params.domain_id
            )
            workspace_group_infos = [
                workspace_group_vo.to_dict()
                for workspace_group_vo in workspace_group_vos
            ]
        else:
            query_filter = {
                "filter": [
                    {"key": "users.user_id", "value": params.user_id, "operator": "eq"},
                    {"key": "domain_id", "value": params.domain_id, "operator": "eq"},
                ]
            }
            workspace_group_infos, _ = self.workspace_group_mgr.list_workspace_groups(
                query_filter
            )

        workspace_group_ids = [
            workspace_group_info["workspace_group_id"]
            for workspace_group_info in workspace_group_infos
        ]

        rb_vos = rb_mgr.filter_role_bindings(
            user_id=params.user_id,
            domain_id=params.domain_id,
            workspace_group_id=workspace_group_ids,
            role_type=["WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
        )
        role_bindings_info_map = {rb.workspace_group_id: rb.to_dict() for rb in rb_vos}

        workspace_group_user_ids = []
        for workspace_group_info in workspace_group_infos:
            if not isinstance(workspace_group_info, dict):
                workspace_group_info = workspace_group_info.to_dict()
            if users := workspace_group_info.get("users", []) or []:
                for user in users:
                    if isinstance(user, dict):
                        workspace_group_user_ids.append(user.get("user_id"))
                    elif hasattr(user, "user_id"):
                        workspace_group_user_ids.append(user.user_id)

        workspace_groups_info = []
        for workspace_group_info in workspace_group_infos:
            workspace_group_dict = (
                self.workspace_group_svc.add_user_name_and_state_to_users(
                    workspace_group_user_ids,
                    workspace_group_info,
                    params.domain_id,
                )
            )
            workspace_groups_info.append(workspace_group_dict)

        my_workspace_groups_info = self._get_my_workspace_groups_info(
            workspace_groups_info, role_bindings_info_map
        )

        return MyWorkspaceGroupsResponse(
            results=my_workspace_groups_info, total_count=len(my_workspace_groups_info)
        )

    def _get_domain_name(self, domain_id: str) -> str:
        domain_vo = self.domain_mgr.get_domain(domain_id)
        return domain_vo.name

    def _issue_temporary_token(self, user_id: str, domain_id: str) -> dict:
        identity_conf = config.get_global("IDENTITY") or {}
        token_conf = identity_conf.get("token", {})
        timeout = token_conf.get("temporary_token_timeout", 86400)

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

    def _check_last_admin(self, domain_id: str, user_vo: User) -> None:
        user_vos = self.user_mgr.filter_users(
            domain_id=domain_id, state="ENABLED", role_type=user_vo.role_type
        )

        if user_vos.count() == 1:
            if user_vos.first().user_id == user_vo.user_id:
                raise ERROR_LAST_ADMIN_CANNOT_DISABLED_DELETED(user_id=user_vo.user_id)

    def _get_console_url(self, domain_id):
        domain_name = self._get_domain_name(domain_id)

        console_domain = config.get_global("EMAIL_CONSOLE_DOMAIN")
        return console_domain.format(domain_name=domain_name)

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

    @staticmethod
    def _get_my_workspaces_info(
        workspaces_info: list, role_name_map: dict, role_bindings_info_map: dict
    ) -> list:
        my_workspaces_info = []

        for workspace_info in workspaces_info:
            if rb_info := role_bindings_info_map.get(workspace_info["workspace_id"]):
                workspace_info.update(
                    {
                        "role_id": rb_info.get("role_id"),
                        "role_type": rb_info.get("role_type"),
                        "role_name": role_name_map.get(rb_info.get("role_id")),
                    }
                )
            my_workspaces_info.append(workspace_info)
        return my_workspaces_info

    @staticmethod
    def _get_my_workspace_groups_info(
        workspace_groups_info: list, role_bindings_info_map: dict = None
    ) -> List[Dict[str, str]]:
        my_workspace_groups_info = []

        for workspace_group_info in workspace_groups_info:
            if rb_info := role_bindings_info_map.get(
                workspace_group_info["workspace_group_id"]
            ):
                workspace_group_info.update({"role_binding_info": rb_info})
            my_workspace_groups_info.append(workspace_group_info)

        return my_workspace_groups_info
