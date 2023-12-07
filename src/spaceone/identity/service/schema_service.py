import logging
from typing import Union

from spaceone.core.service import *
from spaceone.core.service.utils import *

from spaceone.identity.model.schema.request import *
from spaceone.identity.model.schema.response import *
from spaceone.identity.manager.schema_manager import SchemaManager

_LOGGER = logging.getLogger(__name__)


class SchemaService(BaseService):

    service = "identity"
    resource = "Schema"
    permission_group = "DOMAIN"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema_mgr = SchemaManager()

    @transaction(scope="domain_admin:write")
    @convert_model
    def create(self, params: SchemaCreateRequest) -> Union[SchemaResponse, dict]:
        """ create schema

        Args:
            params (SchemaCreateRequest): {
                'schema_id': 'str',         # required
                'name': 'str',              # required
                'schema_type': 'str',       # required
                'schema': 'dict',           # required
                'provider': 'str',          # required
                'related_schemas': 'list',
                'options': 'dict',
                'tags': 'dict',
                'domain_id': 'str'          # required
            }

        Returns:
            SchemaResponse:
        """

        schema_vo = self.schema_mgr.create_schema(params.dict())
        return SchemaResponse(**schema_vo.to_dict())

    @transaction(scope="domain_admin:write")
    @convert_model
    def update(self, params: SchemaUpdateRequest) -> Union[SchemaResponse, dict]:
        """ update schema

        Args:
            params (SchemaUpdateRequest): {
                'schema_id': 'str',       # required
                'name': 'str',
                'schema': 'dict',
                'related_schemas': 'list',
                'options': 'dict',
                'tags': 'dict',
                'domain_id': 'str'        # required
            }

        Returns:
            SchemaResponse:
        """

        schema_vo = self.schema_mgr.get_schema(params.schema_id, params.domain_id)

        schema_vo = self.schema_mgr.update_schema_by_vo(
            params.dict(exclude_unset=True), schema_vo
        )

        return SchemaResponse(**schema_vo.to_dict())

    @transaction(scope="domain_admin:write")
    @convert_model
    def delete(self, params: SchemaDeleteRequest) -> None:
        """ delete schema

        Args:
            params (SchemaDeleteRequest): {
                'schema_id': 'str',     # required
                'domain_id': 'str'      # required
            }

        Returns:
            None
        """

        schema_vo = self.schema_mgr.get_schema(params.schema_id, params.domain_id)
        self.schema_mgr.delete_schema_by_vo(schema_vo)

    @transaction(scope="workspace_member:read")
    @convert_model
    def get(self, params: SchemaGetRequest) -> Union[SchemaResponse, dict]:
        """ delete schema

        Args:
            params (SchemaGetRequest): {
                'schema_id': 'str',     # required
                'domain_id': 'str'      # required
            }

        Returns:
            SchemaResponse:
        """

        schema_vo = self.schema_mgr.get_schema(params.schema_id, params.domain_id)
        return SchemaResponse(**schema_vo.to_dict())

    @transaction(scope="workspace_member:read")
    @append_query_filter(
        ['schema_id', 'name', 'schema_type', 'provider', 'related_schema_id', 'is_managed', 'domain_id']
    )
    @append_keyword_filter(['schema_id', 'name'])
    @convert_model
    def list(self, params: SchemaSearchQueryRequest) -> Union[SchemasResponse, dict]:
        """ list schemas

        Args:
            params (SchemaSearchQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.Query)',
                'schema_id': 'str',
                'name': 'str',
                'schema_type': 'str',
                'provider': 'str',
                'related_schema_id': 'str',
                'is_managed': 'bool',
                'domain_id': 'str'              # required
            }

        Returns:
            SchemasResponse:
        """

        query = params.query or {}
        schema_vos, total_count = self.schema_mgr.list_schemas(query, params.domain_id)

        schemas_info = [schema_vo.to_dict() for schema_vo in schema_vos]
        return SchemasResponse(results=schemas_info, total_count=total_count)

    @transaction(scope="workspace_member:read")
    @append_query_filter(['domain_id'])
    @append_keyword_filter(['schema_id', 'name'])
    @convert_model
    def stat(self, params: SchemaStatQueryRequest) -> dict:
        """ stat schemas

        Args:
            params (SchemaStatQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)', # required
                'domain_id': 'str'    # required
            }

        Returns:
            dict: {
                'results': 'list',
                'total_count': 'int'
            }

        """

        query = params.query or {}
        return self.schema_mgr.stat_schemas(query)
