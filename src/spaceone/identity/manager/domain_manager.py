import logging

from spaceone.core import cache
from spaceone.core.manager import BaseManager
from spaceone.core.connector.space_connector import SpaceConnector
from spaceone.identity.connector import AuthPluginConnector
from spaceone.identity.model.domain_model import Domain

_LOGGER = logging.getLogger(__name__)


class DomainManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.domain_model: Domain = self.locator.get_model('Domain')

    def create_domain(self, params):
        def _rollback(vo):
            _LOGGER.info(f'[create_domain._rollback] Delete domain : {vo.name} ({vo.domain_id})')
            vo.delete()

        domain_vo: Domain = self.domain_model.create(params)
        self.transaction.add_rollback(_rollback, domain_vo)

        if 'plugin_info' in params:
            domain_id = domain_vo.domain_id
            plugin_info = params['plugin_info']
            options = plugin_info.get('options', {})
            endpoint, updated_version = self.get_auth_plugin_endpoint(domain_id, plugin_info)

            if updated_version:
                params['plugin_info']['version'] = updated_version

            response = self.init_auth_plugin(endpoint, options)
            params['plugin_info']['metadata'] = response['metadata']

            secret_data = plugin_info.get('secret_data')

            if secret_data:
                schema = plugin_info.get('schema')
                secret_id = self._create_secret(domain_id, secret_data, schema)

                if secret_id:
                    params['plugin_info']['secret_id'] = secret_id
                    del params['plugin_info']['secret_data']

                if schema:
                    del params['plugin_info']['schema']

            return domain_vo.update({
                'plugin_info': params['plugin_info']
            })
        else:
            return domain_vo

    def update_domain(self, params):
        def _rollback(old_data):
            _LOGGER.info(f'[update_domain._rollback] Revert Data : {old_data["name"]} ({old_data["domain_id"]})')
            domain_vo.update(old_data)

        domain_vo: Domain = self.get_domain(params['domain_id'])
        self.transaction.add_rollback(_rollback, domain_vo.to_dict())

        return domain_vo.update(params)

    def change_auth_plugin(self, domain_id, plugin_info):
        """"
        Case 1. No plugin_info -> New plugin_info
        Case 2. plugin_info(1) -> New plugin_info
        """
        domain_vo: Domain = self.get_domain(domain_id)

        try:
            old_secret_id = domain_vo.plugin_info.secret_id
        except Exception as e:
            # No plugin_info
            # plugin_info without secret_id
            old_secret_id = None

        options = plugin_info.get('options', {})
        endpoint, updated_version = self.get_auth_plugin_endpoint(domain_id, plugin_info)

        if updated_version:
            plugin_info['version'] = updated_version

        response = self.init_auth_plugin(endpoint, options)
        plugin_info['metadata'] = response['metadata']

        secret_data = plugin_info.get('secret_data')

        if secret_data:
            schema = plugin_info.get('schema')
            secret_id = self._create_secret(domain_id, secret_data, schema)

            if secret_id:
                plugin_info['secret_id'] = secret_id
                del plugin_info['secret_data']

            if schema:
                del plugin_info['schema']

        updated_domain_vo = domain_vo.update({'plugin_info': plugin_info})

        if old_secret_id:
            self._delete_secret(old_secret_id, domain_id)

        return updated_domain_vo

    def release_auth_plugin(self, domain_id):
        """ release plugin_info
        """
        domain_vo: Domain = self.get_domain(domain_id)

        # clean plugin_info
        # secret_id, if exist
        if domain_vo.plugin_info.secret_id:
            self._delete_secret(domain_vo.plugin_info.secret_id, domain_id)

        return domain_vo.update({'plugin_info': None})

    def update_domain_plugin(self, domain_id, version=None, options=None, upgrade_mode=None):
        """ Update plugin of domain
        If options exists, it should be complete content.
        """
        domain_vo: Domain = self.get_domain(domain_id)

        plugin_info = domain_vo.plugin_info.to_dict()

        if version:
            plugin_info['version'] = version

        if options:
            plugin_info['options'] = options

        if upgrade_mode:
            plugin_info['upgrade_mode'] = upgrade_mode

        endpoint, updated_version = self.get_auth_plugin_endpoint(domain_id, plugin_info)

        if updated_version:
            plugin_info['version'] = updated_version

        response = self.init_auth_plugin(endpoint, plugin_info.get('options', {}))
        plugin_info['metadata'] = response['metadata']

        return domain_vo.update({'plugin_info': plugin_info})

    def verify_auth_plugin(self, domain_id):
        domain_vo: Domain = self.get_domain(domain_id)
        endpoint = self.get_auth_plugin_endpoint_by_vo(domain_vo)
        plugin_info = domain_vo.plugin_info.to_dict()

        auth_conn: AuthPluginConnector = self.locator.get_connector('AuthPluginConnector')
        auth_conn.initialize(endpoint)

        return auth_conn.verify(plugin_info['options'])

    def delete_domain(self, domain_id):
        domain_vo: Domain = self.get_domain(domain_id)
        domain_vo.delete()

        cache.delete_pattern(f'domain-state:{domain_id}')

    def enable_domain(self, domain_id):
        def _rollback(old_data):
            _LOGGER.info(f'[enable_domain._rollback] Revert Data : {old_data["name"]} ({old_data["domain_id"]})')
            domain_vo.update(old_data)

        domain_vo: Domain = self.get_domain(domain_id)

        if domain_vo.state != 'ENABLED':
            self.transaction.add_rollback(_rollback, domain_vo.to_dict())
            domain_vo.update({'state': 'ENABLED'})

            cache.delete_pattern(f'domain-state:{domain_id}')

        return domain_vo

    def disable_domain(self, domain_id):
        def _rollback(old_data):
            _LOGGER.info(f'[disable_domain._rollback] Revert Data : {old_data["name"]} ({old_data["domain_id"]})')
            domain_vo.update(old_data)

        domain_vo: Domain = self.get_domain(domain_id)

        if domain_vo.state != 'DISABLED':
            self.transaction.add_rollback(_rollback, domain_vo.to_dict())
            domain_vo.update({'state': 'DISABLED'})

            cache.delete_pattern(f'domain-state:{domain_id}')

        return domain_vo

    def get_domain(self, domain_id, only=None):
        return self.domain_model.get(domain_id=domain_id, only=only)

    def list_domains(self, query):
        return self.domain_model.query(**query)

    def stat_domains(self, query):
        return self.domain_model.stat(**query)

    def get_auth_plugin_endpoint_by_vo(self, domain_vo: Domain):
        plugin_info = domain_vo.plugin_info.to_dict()
        endpoint, updated_version = self.get_auth_plugin_endpoint(domain_vo.domain_id, plugin_info)

        if updated_version:
            _LOGGER.debug(f'[get_auth_plugin_endpoint_by_vo] upgrade plugin version: {plugin_info["version"]} -> {updated_version}')
            self.upgrade_auth_plugin_version(domain_vo, endpoint, updated_version)

        return endpoint

    def get_auth_plugin_endpoint(self, domain_id, plugin_info):
        plugin_connector: SpaceConnector = self.locator.get_connector('SpaceConnector', service='plugin')
        response = plugin_connector.dispatch(
            'Plugin.get_plugin_endpoint',
            {
                'plugin_id': plugin_info['plugin_id'],
                'version': plugin_info.get('version'),
                'upgrade_mode': plugin_info.get('upgrade_mode', 'AUTO'),
                'domain_id': domain_id
            }
        )

        return response['endpoint'], response.get('updated_version')

    def upgrade_auth_plugin_version(self, domain_vo: Domain, endpoint, updated_version):
        plugin_info = domain_vo.plugin_info.to_dict()
        response = self.init_auth_plugin(endpoint, plugin_info.get('options', {}))
        plugin_info['version'] = updated_version
        plugin_info['metadata'] = response['metadata']
        domain_vo.update({'plugin_info': plugin_info})

    def init_auth_plugin(self, endpoint, options):
        auth_conn: AuthPluginConnector = self.locator.get_connector('AuthPluginConnector')
        auth_conn.initialize(endpoint)

        return auth_conn.init(options)

    def _create_secret(self, domain_id, secret_data, schema):
        secret_connector: SpaceConnector = self.locator.get_connector('SpaceConnector', service='secret')
        params = {
            'name': f'{domain_id}-auth-plugin-credentials',
            'data': secret_data,
            'secret_type': 'CREDENTIALS',
            'schema': schema,
            'domain_id': domain_id
        }

        resp = secret_connector.dispatch('Secret.create', params)
        _LOGGER.debug(f'[_create_secret] {resp}')
        return resp.get('secret_id')

    def _delete_secret(self, secret_id, domain_id):
        secret_connector: SpaceConnector = self.locator.get_connector('SpaceConnector', service='secret')
        params = {
            'secret_id': secret_id,
            'domain_id': domain_id
        }
        secret_connector.dispatch('Secret.delete', params)

    def _update_secret_data(self, secret_id, secret_data, domain_id):
        secret_connector: SpaceConnector = self.locator.get_connector('SpaceConnector', service='secret')
        params = {
            'secret_id': secret_id,
            'data': secret_data,
            'domain_id': domain_id
        }
        secret_connector.dispatch('Secret.update_data', params)
