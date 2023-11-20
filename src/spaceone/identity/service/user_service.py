import logging
from typing import Union

from spaceone.core.service import BaseService, transaction, convert_model

from spaceone.identity.error.error_mfa import *
from spaceone.identity.manager.user_manager import UserManager
from spaceone.identity.manager.mfa_manager import MFAManager
from spaceone.identity.model.user.request import *
from spaceone.identity.model.user.response import *

_LOGGER = logging.getLogger(__name__)


class UserService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_mgr = UserManager()

    @transaction
    @convert_model
    def create(self, params: UserCreateRequest) -> Union[UserResponse, dict]:
        return {}

    @transaction
    @convert_model
    def update(self, params: UserUpdateRequest) -> Union[UserResponse, dict]:
        return {}

    @transaction
    @convert_model
    def verify_email(self, params: UserVerifyEmailRequest) -> None:
        pass

    @transaction
    @convert_model
    def confirm_email(
        self, params: UserConfirmEmailRequest
    ) -> Union[UserResponse, dict]:
        return {}

    @transaction
    @convert_model
    def reset_password(self, params: UserResetPasswordRequest) -> None:
        pass

    @transaction
    @convert_model
    def set_required_actions(
        self, params: UserSetRequiredActionsRequest
    ) -> Union[UserResponse, dict]:
        return {}

    @transaction
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

    @transaction
    @convert_model
    def disable_mfa(self, params: UserDisableMFARequest) -> Union[UserResponse, dict]:
        return {}

    @transaction
    @convert_model
    def confirm_mfa(self, params: UserConfirmMFARequest) -> Union[UserResponse, dict]:
        return {}

    @transaction
    @convert_model
    def delete(self, params: UserDeleteRequest) -> None:
        pass

    @transaction
    @convert_model
    def enable(self, params: UserEnableRequest) -> Union[UserResponse, dict]:
        return {}

    @transaction
    @convert_model
    def disable(self, params: UserDisableRequest) -> Union[UserResponse, dict]:
        return {}

    @transaction
    @convert_model
    def get(self, params: UserGetRequest) -> Union[UserResponse, dict]:
        return {}

    @transaction
    @convert_model
    def list(self, params: UserSearchQueryRequest) -> Union[UsersResponse, dict]:
        return {}

    @transaction
    @convert_model
    def stat(self, params: UserStatQueryRequest) -> dict:
        return {}
