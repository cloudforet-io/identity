import logging
from typing import Tuple

from spaceone.core.cache import cacheable
from spaceone.core.manager import BaseManager
from spaceone.identity.lib.key_generator import KeyGenerator
from spaceone.identity.model.api_key.database import APIKey
from spaceone.identity.model.domain.database import DomainSecret
from spaceone.identity.model.user.database import User

_LOGGER = logging.getLogger(__name__)


class APIKeyManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key_model = APIKey
        self.domain_secret_model = DomainSecret

    def create_api_key(self, user_vo: User, params: dict) -> (APIKey, str):
        def _rollback(api_key_vo):
            _LOGGER.info(
                f"[create_api_key._rollback] Delete api_key : {api_key_vo.api_key_id}"
            )
            api_key_vo.delete()

        params["user"] = user_vo
        api_key_vo: APIKey = self.api_key_model.create(params)
        self.transaction.add_rollback(_rollback, api_key_vo)

        prv_jwk = self._query_domain_secret(params["domain_id"])

        key_gen = KeyGenerator(
            prv_jwk=prv_jwk, domain_id=params["domain_id"], audience=user_vo.user_id
        )

        api_key = key_gen.generate_api_key(api_key_vo.api_key_id)
        return api_key_vo, api_key

    def delete_api_key(self, api_key_id, domain_id):
        api_key_vo = self.get_api_key(api_key_id, domain_id)
        api_key_vo.delete()

    @staticmethod
    def delete_api_key_by_vo(api_key_vo: APIKey) -> None:
        api_key_vo.delete()

    def enable_api_key(self, api_key_id, domain_id):
        def _rollback(old_data):
            _LOGGER.info(f"[enable_api_key._rollback] Revert Data: {old_data}")
            api_key_vo.update(old_data)

        api_key_vo: APIKey = self.get_api_key(api_key_id, domain_id)
        if api_key_vo.state != "ENABLED":
            self.transaction.add_rollback(_rollback, api_key_vo.to_dict())
            api_key_vo.update({"state": "ENABLED"})

        return api_key_vo

    def disable_api_key(self, api_key_id, domain_id):
        def _rollback(old_data):
            _LOGGER.info(f"[disable_api_key._rollback] Revert Data: {old_data}")
            api_key_vo.update(old_data)

        api_key_vo: APIKey = self.get_api_key(api_key_id, domain_id)
        if api_key_vo.state != "DISABLED":
            self.transaction.add_rollback(_rollback, api_key_vo.to_dict())
            api_key_vo.update({"state": "DISABLED"})

        return api_key_vo

    def get_api_key(self, api_key_id: str, domain_id: str) -> APIKey:
        return self.api_key_model.get(api_key_id=api_key_id, domain_id=domain_id)

    def list_api_keys(self, query: dict) -> Tuple[list, int]:
        return self.api_key_model.query(**query)

    def stat_api_keys(self, query):
        return self.api_key_model.stat(**query)

    @cacheable(key="api-key:{domain_id}", expire=60)
    def _query_domain_secret(self, domain_id: str) -> DomainSecret:
        domain_secret = self.domain_secret_model.get(domain_id=domain_id)
        return domain_secret.prv_jwk
