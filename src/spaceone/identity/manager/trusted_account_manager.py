import logging
from typing import Tuple, List, Union

from spaceone.core.manager import BaseManager
from spaceone.identity.model.trusted_account.database import TrustedAccount

_LOGGER = logging.getLogger(__name__)


class TrustedAccountManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trusted_account_model = TrustedAccount

    def create_trusted_account(self, params: dict) -> TrustedAccount:
        def _rollback(vo: TrustedAccount):
            _LOGGER.info(
                f"[create_trusted_account._rollback] "
                f"Delete trusted service account: {vo.name} ({vo.trusted_account_id})"
            )
            vo.delete()

        trusted_account_vo = self.trusted_account_model.create(params)
        self.transaction.add_rollback(_rollback, trusted_account_vo)

        return trusted_account_vo

    def update_trusted_account_by_vo(
        self, params: dict, trusted_account_vo: TrustedAccount
    ) -> TrustedAccount:
        def _rollback(old_data: dict):
            _LOGGER.info(
                f"[update_trusted_account_by_vo._rollback] Revert Data : "
                f'{old_data["trusted_account_id"]}'
            )
            trusted_account_vo.update(old_data)

        self.transaction.add_rollback(_rollback, trusted_account_vo.to_dict())

        return trusted_account_vo.update(params)

    @staticmethod
    def delete_trusted_account_by_vo(trusted_account_vo: TrustedAccount) -> None:
        trusted_account_vo.delete()

    def get_trusted_account(
        self,
        trusted_account_id: str,
        domain_id: str,
        workspace_id: Union[str, list] = None,
    ) -> TrustedAccount:
        conditions = {
            "trusted_account_id": trusted_account_id,
            "domain_id": domain_id,
        }

        if workspace_id:
            conditions["workspace_id"] = workspace_id

        return self.trusted_account_model.get(**conditions)

    def filter_trusted_accounts(self, **conditions) -> List[TrustedAccount]:
        return self.trusted_account_model.filter(**conditions)

    def list_trusted_accounts(self, query: dict) -> Tuple[list, int]:
        return self.trusted_account_model.query(**query)

    def stat_trusted_accounts(self, query: dict) -> dict:
        return self.trusted_account_model.stat(**query)
