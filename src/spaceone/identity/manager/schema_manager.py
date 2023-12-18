import logging
from typing import Tuple, List
from jsonschema import validate, exceptions

from spaceone.core import cache
from spaceone.core.manager import BaseManager
from spaceone.identity.error.error_schema import (
    ERROR_SCHEMA_IS_NOT_DEFINED,
    ERROR_SCHEMA_ID_IS_NOT_DEFINED,
    ERROR_INVALID_PARAMETER,
)
from spaceone.identity.model.schema.database import Schema
from spaceone.identity.manager.managed_resource_manager import ManagedResourceManager

_LOGGER = logging.getLogger(__name__)


class SchemaManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema_model = Schema

    def create_schema(self, params: dict) -> Schema:
        def _rollback(vo: Schema):
            _LOGGER.info(f"[create_schema._rollback] Delete schema : {vo.schema}")
            vo.delete()

        schema_vo = self.schema_model.create(params)
        self.transaction.add_rollback(_rollback, schema_vo)

        return schema_vo

    def update_schema_by_vo(self, params: dict, schema_vo: Schema) -> Schema:
        def _rollback(old_data):
            _LOGGER.info(
                f'[update_schema._rollback] Revert Data : {old_data["schema"]}'
            )
            schema_vo.update(old_data)

        self.transaction.add_rollback(_rollback, schema_vo.to_dict())

        return schema_vo.update(params)

    @staticmethod
    def delete_schema_by_vo(schema_vo: Schema) -> None:
        schema_vo.delete()

    def get_schema(self, schema_id: str, domain_id: str) -> Schema:
        return self.schema_model.get(schema_id=schema_id, domain_id=domain_id)

    def filter_schemas(self, **conditions) -> List[Schema]:
        return self.schema_model.filter(**conditions)

    def list_schemas(self, query: dict, domain_id: str) -> Tuple[list, int]:
        self._create_managed_schema(domain_id)
        return self.schema_model.query(**query)

    def stat_schemas(self, query: dict) -> dict:
        return self.schema_model.stat(**query)

    @cache.cacheable(key="identity:managed-schema:{domain_id}:sync", expire=300)
    def _create_managed_schema(self, domain_id: str) -> bool:
        managed_resource_mgr = ManagedResourceManager()

        schema_vos = self.filter_schemas(domain_id=domain_id, is_managed=True)

        installed_schema_version_map = {}
        for schema_vo in schema_vos:
            installed_schema_version_map[schema_vo.schema_id] = schema_vo.version

        managed_schema_map = managed_resource_mgr.get_managed_schemas()

        for managed_schema, managed_schema_info in managed_schema_map.items():
            managed_schema_info["domain_id"] = domain_id
            managed_schema_info["is_managed"] = True

            if schema_version := installed_schema_version_map.get(managed_schema):
                if schema_version != managed_schema_info["version"]:
                    _LOGGER.debug(
                        f"[_create_managed_schema] update managed schema: {managed_schema}"
                    )
                    schema_vo = self.get_schema(managed_schema, domain_id)
                    self.update_schema_by_vo(managed_schema_info, schema_vo)
            else:
                _LOGGER.debug(
                    f"[_create_managed_schema] create new managed schema: {managed_schema}"
                )
                self.create_schema(managed_schema_info)

        return True

    def validate_data_by_schema(
        self, provider: str, domain_id: str, schema_type: str, data: dict
    ) -> None:
        schema_vos = self.filter_schemas(
            provider=provider, domain_id=domain_id, schema_type=schema_type
        )

        if len(schema_vos) > 0:
            try:
                validate(instance=data, schema=schema_vos[0].schema)
            except exceptions.ValidationError as e:
                raise ERROR_INVALID_PARAMETER(key="data", reason=e.message)
        else:
            raise ERROR_SCHEMA_IS_NOT_DEFINED(
                provider=provider, schema_type=schema_type
            )

    def validate_secret_data_by_schema_id(
        self, schema_id: str, domain_id: str, data: dict, schema_type: str
    ) -> None:
        schema_vos = self.filter_schemas(
            schema_id=schema_id,
            domain_id=domain_id,
            schema_type=schema_type,
        )

        if len(schema_vos) > 0:
            try:
                validate(instance=data, schema=schema_vos[0].schema)
            except exceptions.ValidationError as e:
                raise ERROR_INVALID_PARAMETER(key="secret_data", reason=e.message)
        else:
            raise ERROR_SCHEMA_ID_IS_NOT_DEFINED(
                schema_id=schema_id, schema_type=schema_type
            )
