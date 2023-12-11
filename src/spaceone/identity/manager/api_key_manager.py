import logging
from typing import Tuple

from mongoengine import QuerySet
from spaceone.core.manager import BaseManager
from spaceone.core import utils

from spaceone.identity.lib.key_generator import KeyGenerator
from spaceone.identity.model.app.database import App
from spaceone.identity.model.api_key.database import APIKey
from spaceone.identity.model.user.database import User
from spaceone.identity.manager.domain_secret_manager import DomainSecretManager

_LOGGER = logging.getLogger(__name__)


class APIKeyManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key_model = APIKey

    def create_api_key(self, params: dict) -> Tuple[APIKey, str]:
        def _rollback(vo):
            _LOGGER.info(f"[create_api_key._rollback] Delete api key: {vo.api_key_id}")
            vo.delete()

        if params["owner_type"] == "USER":
            audience = params["user_id"]
        else:
            audience = params["app_id"]

        api_key_vo = self.api_key_model.create(params)
        self.transaction.add_rollback(_rollback, api_key_vo)

        domain_secret_mgr = DomainSecretManager()
        prv_jwk = domain_secret_mgr.get_domain_private_key(params["domain_id"])
        params["expired_at"] = utils.iso8601_to_datetime(
            params["expired_at"]
        ).timestamp()

        key_gen = KeyGenerator(
            api_key_id=api_key_vo.api_key_id,
            prv_jwk=prv_jwk,
            domain_id=params["domain_id"],
            audience=audience,
        )

        api_key = key_gen.generate_api_key(params["expired_at"])

        return api_key_vo, api_key

    def create_api_key_by_user_vo(
        self, user_vo: User, params: dict
    ) -> Tuple[APIKey, str]:
        params["user"] = user_vo
        params["owner_type"] = "USER"
        return self.create_api_key(params)

    def create_api_key_by_app_vo(self, app_vo: App, params: dict) -> Tuple[APIKey, str]:
        params["app"] = app_vo
        params["app_id"] = app_vo.app_id
        params["owner_type"] = "APP"
        return self.create_api_key(params)

    def update_api_key_by_vo(self, params: dict, api_key_vo: APIKey) -> APIKey:
        def _rollback(old_data):
            _LOGGER.info(
                f"[update_api_key_by_vo._rollback] Revert Data : {old_data['api_key_id']}"
            )
            api_key_vo.update(old_data)

        self.transaction.add_rollback(_rollback, api_key_vo.to_dict())

        return api_key_vo.update(params)

    @staticmethod
    def delete_api_key_by_vo(api_key_vo: APIKey) -> None:
        api_key_vo.delete()

    def enable_api_key(self, api_key_vo: APIKey) -> APIKey:
        return self.update_api_key_by_vo({"state": "ENABLED"}, api_key_vo)

    def disable_api_key(self, api_key_vo: APIKey) -> APIKey:
        return self.update_api_key_by_vo({"state": "DISABLED"}, api_key_vo)

    def get_api_key(
        self,
        api_key_id: str,
        domain_id: str,
        owner_type: str,
        user_id: str = None,
        app_id: str = None,
    ) -> APIKey:
        conditions = {
            "api_key_id": api_key_id,
            "domain_id": domain_id,
            "owner_type": owner_type,
        }

        if user_id:
            conditions["user_id"] = user_id

        if app_id:
            conditions["app_id"] = app_id

        return self.api_key_model.get(**conditions)

    def filter_api_keys(self, **conditions) -> QuerySet:
        return self.api_key_model.filter(**conditions)

    def list_api_keys(self, query: dict) -> Tuple[list, int]:
        return self.api_key_model.query(**query)

    def stat_api_keys(self, query: dict) -> dict:
        return self.api_key_model.stat(**query)
