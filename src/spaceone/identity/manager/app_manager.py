import logging
from typing import Tuple, Union

from mongoengine import QuerySet
from spaceone.core.manager import BaseManager

from spaceone.identity.model.app.database import App

_LOGGER = logging.getLogger(__name__)


class AppManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app_model = App

    def create_app(self, params: dict) -> App:
        def _rollback(vo: App):
            _LOGGER.info(f"[create_app._rollback] Delete app: {vo.name} ({vo.app_id})")
            vo.delete()

        app_vo = self.app_model.create(params)
        self.transaction.add_rollback(_rollback, app_vo)

        return app_vo

    def update_app_by_vo(self, params: dict, app_vo: App) -> App:
        def _rollback(old_data):
            _LOGGER.info(
                f'[update_app._rollback] Revert Data: {old_data["name"]} ({old_data["app_id"]})'
            )
            app_vo.update(old_data)

        self.transaction.add_rollback(_rollback, app_vo.to_dict())

        return app_vo.update(params)

    def enable_app(self, app_vo: App) -> App:
        self.update_app_by_vo({"state": "ENABLED"}, app_vo)

        return app_vo

    def disable_app(self, app_vo: App) -> App:
        self.update_app_by_vo({"state": "DISABLED"}, app_vo)

        return app_vo

    @staticmethod
    def delete_app_by_vo(app_vo: App) -> None:
        app_vo.delete()

    def get_app(
        self,
        app_id: str,
        domain_id: str,
        workspace_id: Union[str, None] = None,
    ) -> App:
        conditions = {
            "app_id": app_id,
            "domain_id": domain_id,
        }

        if workspace_id:
            conditions["workspace_id"] = workspace_id

        return self.app_model.get(**conditions)

    def filter_apps(self, **conditions) -> QuerySet:
        return self.app_model.filter(**conditions)

    def list_apps(self, query: dict) -> Tuple[list, int]:
        return self.app_model.query(**query)

    def stat_apps(self, query: dict) -> dict:
        return self.app_model.stat(**query)
