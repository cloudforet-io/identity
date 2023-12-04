import logging

from datetime import datetime, timedelta
from typing import Union
from spaceone.core.service import (
    BaseService,
    transaction,
    convert_model,
    append_query_filter,
    append_keyword_filter,
)

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
        """Delete API Key
        Args:
            params (dict): {
                'api_key_id': 'str', # required
                'domain_id': 'str' # required
            }
        Returns:
            None
        """
        api_key_vo = self.api_key_mgr.get_api_key(params.api_key_id, params.domain_id)
        self.api_key_mgr.delete_api_key_by_vo(api_key_vo)

    @transaction
    @convert_model
    def get(self, params: APIKeyGetRequest) -> Union[APIKeyResponse, dict]:
        """Get API Key
        Args:
            params (dict): {
                'api_key_id': 'str', # required
                'domain_id': 'str' # required
            }
        Returns:
            APIKeyResponse:
        """
        api_key_vo = self.api_key_mgr.get_api_key(params.api_key_id, params.domain_id)
        return APIKeyResponse(**api_key_vo.to_dict())

    @transaction
    @append_query_filter(["api_key_id", "user_id", "state", "domain_id"])
    @append_keyword_filter(["api_key_id", "user_id"])
    @convert_model
    def list(self, params: APIKeySearchQueryRequest) -> Union[APIKeysResponse, dict]:
        """List API Keys
        Args:
            params (dict): {
                'query': 'dict',
                'api_key_id': 'str',
                'user_id': 'str',
                'state': 'str',
                'domain_id': 'str'
            }
            Returns:
                APIKeysResponse:
        """
        query = params.query or {}
        api_key_vos, total_count = self.api_key_mgr.list_api_keys(query)
        api_keys_info = [api_key_vo.to_dict() for api_key_vo in api_key_vos]
        return APIKeysResponse(results=api_keys_info, total_count=total_count)

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
