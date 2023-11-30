import logging
import os
from typing import List

from spaceone.core import utils
from spaceone.core.manager import BaseManager

_LOGGER = logging.getLogger(__name__)
CURRENT_DIR = os.path.dirname(__file__)
_PROVIDER_DIR = os.path.join(CURRENT_DIR, '../managed_resource/provider/')
_SCHEMA_DIR = os.path.join(CURRENT_DIR, '../managed_resource/schema/')
_ROLE_DIR = os.path.join(CURRENT_DIR, '../managed_resource/role/')


class ManagedResourceManager(BaseManager):

    def list_managed_providers(self):
        return self._load_managed_resources(_PROVIDER_DIR)

    def list_managed_schemas(self):
        return self._load_managed_resources(_SCHEMA_DIR)

    def list_managed_roles(self):
        return self._load_managed_resources(_ROLE_DIR)

    @staticmethod
    def _load_managed_resources(dir_path: str) -> List[dict]:
        managed_resources = []
        for filename in os.listdir(dir_path):
            if filename.endswith('.yaml'):
                file_path = os.path.join(dir_path, filename)
                managed_resource_info = utils.load_yaml_from_file(file_path)
                managed_resources.append(managed_resource_info)
        return managed_resources
