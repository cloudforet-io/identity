import logging
from typing import Union

from spaceone.core.service import *
from spaceone.core.service.utils import *
from spaceone.core.error import *

from spaceone.identity.model.provider.request import *
from spaceone.identity.model.provider.response import *
from spaceone.identity.manager.account_collector_plugin_manager import (
    AccountCollectorPluginManager,
)
from spaceone.identity.manager.provider_manager import ProviderManager

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class ProviderService(BaseService):
    resource = "Provider"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.provider_mgr = ProviderManager()
        self.ac_plugin_mgr = AccountCollectorPluginManager()

    @transaction(permission="identity:Provider.write", role_types=["DOMAIN_ADMIN"])
    @convert_model
    def create(self, params: ProviderCreateRequest) -> Union[ProviderResponse, dict]:
        """create provider

        Args:
            params (ProviderCreateRequest): {
                'provider': 'str',      # required
                'name': 'str',          # required
                'alias': 'str',
                'plugin_info: 'dict'
                'color': 'str',
                'icon': 'str',
                'order': 'int',
                'options': 'dict',
                'tags': 'dict',
                'domain_id': 'str'      # injected from auth (required)
            }

        Returns:
            ProviderResponse:
        """

        self._check_sync_option_with_plugin_info(params.options, params.plugin_info)

        provider_vo = self.provider_mgr.create_provider(params.dict())
        return ProviderResponse(**provider_vo.to_dict())

    @transaction(permission="identity:Provider.write", role_types=["DOMAIN_ADMIN"])
    @convert_model
    def update(self, params: ProviderUpdateRequest) -> Union[ProviderResponse, dict]:
        """update provider

        Args:
            params (ProviderUpdateRequest): {
                'provider': 'str',      # required
                'name': 'str',
                'alias': 'str',
                'color': 'str',
                'icon': 'str',
                'order': 'int',
                'options': 'dict',
                'tags': 'dict',
                'domain_id': 'str'      # injected from auth (required)
            }

        Returns:
            ProviderResponse:
        """

        provider_vo = self.provider_mgr.get_provider(params.provider, params.domain_id)
        if provider_vo.is_managed:
            raise ERROR_PERMISSION_DENIED()

        provider_vo = self.provider_mgr.update_provider_by_vo(
            params.dict(exclude_unset=True), provider_vo
        )

        return ProviderResponse(**provider_vo.to_dict())

    @transaction(
        permission="identity:TrustedAccount.write",
        role_types=["DOMAIN_ADMIN"],
    )
    @convert_model
    def update_plugin(
        self, params: ProviderUpdatePluginRequest
    ) -> Union[ProviderResponse, dict]:
        """update provider plugin info
        Args:
            params (ProviderUpdatePluginRequest): {
                'provider': 'str',      # required
                'version': 'str',
                'options': 'dict',
                'upgrade_mode': 'str',
                'domain_id': 'str'      # injected from auth
            }


        """

        provider = params.provider
        domain_id = params.domain_id
        version = params.version
        options = params.options or {}
        upgrade_mode = params.upgrade_mode

        provider = self.provider_mgr.get_provider(provider, domain_id)

        self.check_update_provider_plugin_info(provider.options)

        plugin_info = provider.plugin_info
        if version:
            plugin_info["version"] = version

        if options:
            plugin_info["options"] = options

        if upgrade_mode:
            plugin_info["upgrade_mode"] = upgrade_mode

        (
            endpoint,
            updated_version,
        ) = self.ac_plugin_mgr.get_account_collector_plugin_endpoint(
            plugin_info, domain_id
        )

        if updated_version:
            plugin_info["version"] = updated_version

        options = plugin_info.get("options", {})
        plugin_metadata = self._init_plugin(endpoint, options, domain_id)

        plugin_info["metadata"] = plugin_metadata
        _LOGGER.debug(f"[update_plugin] plugin_info: {plugin_info}")

        provider = self.provider_mgr.update_provider_by_vo(
            {"plugin_info": plugin_info}, provider
        )
        return ProviderResponse(**provider.to_dict())

    @transaction(permission="identity:Provider.write", role_types=["DOMAIN_ADMIN"])
    @convert_model
    def delete(self, params: ProviderDeleteRequest) -> None:
        """delete provider

        Args:
            params (ProviderDeleteRequest): {
                'provider': 'str',      # required
                'domain_id': 'str'      # injected from auth (required)
            }

        Returns:
            None
        """

        provider_vo = self.provider_mgr.get_provider(params.provider, params.domain_id)
        if provider_vo.is_managed:
            raise ERROR_PERMISSION_DENIED()

        self.provider_mgr.delete_provider_by_vo(provider_vo)

    @transaction(
        permission="identity:Provider.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @convert_model
    def get(self, params: ProviderGetRequest) -> Union[ProviderResponse, dict]:
        """delete provider

        Args:
            params (ProviderGetRequest): {
                'provider': 'str',      # required
                'domain_id': 'str'      # injected from auth (required)
            }

        Returns:
            ProviderResponse:
        """

        provider_vo = self.provider_mgr.get_provider(params.provider, params.domain_id)
        return ProviderResponse(**provider_vo.to_dict())

    @transaction(
        permission="identity:Provider.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @append_query_filter(["provider", "name", "alias", "is_managed", "domain_id"])
    @append_keyword_filter(["provider", "name"])
    @convert_model
    def list(
        self, params: ProviderSearchQueryRequest
    ) -> Union[ProvidersResponse, dict]:
        """list providers

        Args:
            params (ProviderSearchQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.Query)',
                'provider': 'str',
                'name': 'str',
                'alias': 'str',
                'is_managed': 'bool',
                'domain_id': 'str'      # injected from auth (required)
            }

        Returns:
            ProvidersResponse:
        """

        query = params.query or {}
        provider_vos, total_count = self.provider_mgr.list_providers(
            query, params.domain_id
        )

        providers_info = [provider_vo.to_dict() for provider_vo in provider_vos]
        return ProvidersResponse(results=providers_info, total_count=total_count)

    @transaction(
        permission="identity:Provider.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @append_query_filter(["domain_id"])
    @append_keyword_filter(["provider", "name"])
    @convert_model
    def stat(self, params: ProviderStatQueryRequest) -> dict:
        """stat providers

        Args:
            params (ProviderStatQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)', # required
                'domain_id': 'str'    # injected from auth (required)
            }

        Returns:
            dict: {
                'results': 'list',
                'total_count': 'int'
            }

        """

        query = params.query or {}
        return self.provider_mgr.stat_providers(query)

    def _init_plugin(self, endpoint: str, options: dict, domain_id: str) -> dict:
        self.ac_plugin_mgr.initialize(endpoint)
        return self.ac_plugin_mgr.init_plugin(domain_id, options)

    @staticmethod
    def _check_sync_option_with_plugin_info(
        provider_options: Union[dict, None],
        plugin_info: Union[Plugin, dict, None],
    ) -> None:
        if provider_options:
            if provider_options.get("support_auto_sync"):
                if not provider_options.get("support_trusted_account"):
                    raise ERROR_INVALID_PARAMETER(
                        key="options.support_trusted_account",
                        reason="Provider must support 'Trusted Account' to support 'Service Account' auto sync.",
                    )
                if not plugin_info:
                    raise ERROR_INVALID_PARAMETER(
                        key="plugin_info",
                        reason="Plugin info is required for 'Service Account' auto sync.",
                    )

            if plugin_info:
                if not (
                    provider_options.get("support_trusted_account")
                    or not provider_options.get("support_auto_sync")
                ):
                    raise ERROR_INVALID_PARAMETER(
                        key="options",
                        reason="Both support_trusted_account and support_auto_sync must be enabled.",
                    )

    @staticmethod
    def check_update_provider_plugin_info(provider_options: dict):
        if not provider_options.get("support_trusted_account"):
            raise ERROR_INVALID_PARAMETER(
                key="options",
                reason="Provider support_trusted_account option is disabled.",
            )
        if not provider_options["support_auto_sync"]:
            raise ERROR_INVALID_PARAMETER(
                key="options", reason="Provider support_auto_sync option is disabled."
            )
