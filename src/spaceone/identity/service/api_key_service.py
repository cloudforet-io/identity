import logging

from datetime import datetime, timedelta
from typing import Union
from spaceone.core.service import BaseService, transaction, convert_model

from spaceone.identity.error.error_api_key import *
from spaceone.identity.manager.api_key_manager import APIKeyManager
from spaceone.identity.manager.user_manager import UserManager
from spaceone.identity.model.api_key.request import *
from spaceone.identity.model.api_key.response import *

_LOGGER = logging.getLogger(__name__)


class APIKeyService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key_mgr = APIKeyManager()

    @transaction
    @convert_model
    def create(self, params: APIKeyCreateRequest) -> Union[APIKeyResponse, dict]:
        """Create API Key
        Args:
            params (dict): {
                'user_id': 'str', # required
                'name': 'str',
                'expired_at': 'datetime'
                'domain_id': 'str', # required
            }
        Return:
            APIKeyResponse:

        """
        expired_at = self._get_expired_at(params.expired_at)
        self._check_expired_at(expired_at)

        user_mgr = UserManager()
        user_vo = user_mgr.get_user(params.user_id, params.domain_id)
        api_key_vo, api_key = self.api_key_mgr.create_api_key(user_vo, params.dict())
        return APIKeyResponse(**api_key_vo.to_dict(), api_key=api_key)

    @transaction
    @convert_model
    def update(self, params: APIKeyUpdateRequest) -> Union[APIKeyResponse, dict]:
        return {}

    @transaction
    @convert_model
    def enable(self, params: APIKeyEnableRequest) -> Union[APIKeyResponse, dict]:
        return {}

    @transaction
    @convert_model
    def disable(self, params: APIKeyDisableRequest) -> Union[APIKeyResponse, dict]:
        return {}

    @transaction
    @convert_model
    def delete(self, params: APIKeyDeleteRequest) -> None:
        pass

    @transaction
    @convert_model
    def get(self, params: APIKeyGetRequest) -> Union[APIKeyResponse, dict]:
        return {}

    @transaction
    @convert_model
    def list(self, params: APIKeySearchQueryRequest) -> Union[APIKeysResponse, dict]:
        return {}

    @transaction
    @convert_model
    def stat(self, params: APIKeyStatQueryRequest) -> dict:
        return {}

    @staticmethod
    def _get_expired_at(expired_at: datetime) -> datetime:
        if expired_at:
            return expired_at.replace(hour=23, minute=59, second=59, microsecond=0)
        else:
            return datetime.now().replace(
                hour=23, minute=59, second=59, microsecond=0
            ) + timedelta(days=365)

    @staticmethod
    def _check_expired_at(expired_at):
        one_year_later = datetime.now().replace(
            hour=23, minute=59, second=59, microsecond=0
        ) + timedelta(days=365)

        if one_year_later < expired_at:
            raise ERROR_API_KEY_EXPIRED_LIMIT(
                expired_at=expired_at.strftime("%Y-%m-%dT%H:%M:%S")
            )
