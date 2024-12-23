import logging
import os
from typing import List

from spaceone.core import utils
from spaceone.core.manager import BaseManager

_LOGGER = logging.getLogger(__name__)
CURRENT_DIR = os.path.dirname(__file__)
_PROVIDER_DIR = os.path.join(CURRENT_DIR, "../managed_resource/provider/")
_SCHEMA_DIR = os.path.join(CURRENT_DIR, "../managed_resource/schema/")
_ROLE_DIR = os.path.join(CURRENT_DIR, "../managed_resource/role/")
_PACKAGE_DIR = os.path.join(CURRENT_DIR, "../managed_resource/package/")


class ManagedResourceManager(BaseManager):
    def get_managed_providers(self) -> dict:
        provider_map = {}
        for provider in self._load_managed_resources(_PROVIDER_DIR):
            provider_map[provider["provider"]] = provider

        return provider_map

    def get_managed_schemas(self) -> dict:
        schema_map = {}
        for schema in self._load_managed_resources(_SCHEMA_DIR):
            schema_map[schema["schema_id"]] = schema

        return schema_map

    def get_managed_roles(self) -> dict:
        role_map = {}
        for role in self._load_managed_resources(_ROLE_DIR):
            role_map[role["role_id"]] = role

        return role_map

    def get_managed_packages(self) -> dict:
        package_map = {}
        for package in self._load_managed_resources(_PACKAGE_DIR):
            package_map[package["name"]] = package

        return package_map

    @staticmethod
    def _load_managed_resources(dir_path: str) -> List[dict]:
        managed_resources = []
        for filename in os.listdir(dir_path):
            if filename.endswith(".yaml"):
                file_path = os.path.join(dir_path, filename)
                managed_resource_info = utils.load_yaml_from_file(file_path)
                managed_resources.append(managed_resource_info)
        return managed_resources
