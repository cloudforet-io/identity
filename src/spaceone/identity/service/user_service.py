import logging
from typing import Union
from spaceone.core.service import BaseService, transaction, convert_model
from spaceone.identity.model.user_request import *
from spaceone.identity.model.user_response import *

_LOGGER = logging.getLogger(__name__)


class UserService(BaseService):
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
        return {}

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
