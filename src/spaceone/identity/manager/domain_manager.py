import logging

from spaceone.core.manager import BaseManager

from spaceone.identity.connector import PluginServiceConnector, AuthPluginConnector
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

        if 'plugin_info' in params:
            plugin_info = params['plugin_info']
            _LOGGER.debug(f'[create_domain] plugin_info: {plugin_info}')
            plugin_svc_conn: PluginServiceConnector = self.locator.get_connector('PluginServiceConnector')
            plugin_id = plugin_info['plugin_id']
            version = plugin_info['version']
            _LOGGER.warning('[create_domain] Can not check plugin, since there is no token')
            # TODO: labels
            # TODO: no token
            #endpoint = plugin_svc_conn.get_plugin_endpoint(plugin_id, version)
            #_LOGGER.debug('endpoint: %s' % endpoint)

        domain_vo: Domain = self.domain_model.create(params)

        self.transaction.add_rollback(_rollback, domain_vo)

        return domain_vo

    def update_domain(self, params):
        def _rollback(old_data):
            _LOGGER.info(f'[update_domain._rollback] Revert Data : {old_data["name"]} ({old_data["domain_id"]})')
            domain_vo.update(old_data)

        domain_vo: Domain = self.get_domain(params['domain_id'])

        self.transaction.add_rollback(_rollback, domain_vo.to_dict())
        domain_id = params['domain_id']
        if 'plugin_info' in params:
            # TODO: Check Plugin
            plugin_info = params['plugin_info']
            _LOGGER.debug('[update_domain] plugin_info: %s' % plugin_info)
            endpoint = self._get_plugin_endpoint(domain_id, plugin_info)
            if endpoint:
                # grpc://dev-docker.pyengine.net:50060
                # verify plugin
                # plugin will return options
                # TODO: secret_id
                params['options'] = plugin_info['options']
                params['credentials'] = {}
                # params = {
                #     'options': plugin_info['options'],
                #     'credentials': {}
                # }

                result = self._auth_init_and_verify(endpoint, params)
                _LOGGER.debug('[update_domain] endpoint: %s' % endpoint)
                _LOGGER.debug('[update_domain] updated options: %s' % result)
                plugin_info['options'] = result['options']
                params['plugin_info'] = plugin_info

        return domain_vo.update(params)

    def delete_domain(self, domain_id):
        domain_vo: Domain = self.get_domain(domain_id)
        domain_vo.delete()

    def enable_domain(self, domain_id):
        def _rollback(old_data):
            _LOGGER.info(f'[enable_domain._rollback] Revert Data : {old_data["name"]} ({old_data["domain_id"]})')
            domain_vo.update(old_data)

        domain_vo: Domain = self.get_domain(domain_id)

        if domain_vo.state != 'ENABLED':
            self.transaction.add_rollback(_rollback, domain_vo.to_dict())
            domain_vo.update({'state': 'ENABLED'})

        return domain_vo

    def disable_domain(self, domain_id):
        def _rollback(old_data):
            _LOGGER.info(f'[disable_domain._rollback] Revert Data : {old_data["name"]} ({old_data["domain_id"]})')
            domain_vo.update(old_data)

        domain_vo: Domain = self.get_domain(domain_id)

        if domain_vo.state != 'DISABLED':
            self.transaction.add_rollback(_rollback, domain_vo.to_dict())
            domain_vo.update({'state': 'DISABLED'})

        return domain_vo

    def get_domain(self, domain_id, only=None):
        return self.domain_model.get(domain_id=domain_id, only=only)

    def list_domains(self, query):
        return self.domain_model.query(**query)

    def stat_domains(self, query):
        return self.domain_model.stat(**query)

    def _get_plugin_endpoint(self, domain_id, plugin_info):
        plugin_svc_conn: PluginServiceConnector = self.locator.get_connector('PluginServiceConnector')
        plugin_id = plugin_info['plugin_id']
        version = plugin_info['version']
        # TODO: label
        endpoint = plugin_svc_conn.get_plugin_endpoint(plugin_id, version, domain_id)
        return endpoint

    def _auth_init_and_verify(self, endpoint, params):
        auth: AuthPluginConnector = self.locator.get_connector('AuthPluginConnector')
        auth.initialize(endpoint)
        # update options based on return verify
        result = auth.verify(params.get("options"), params.get("credentials"))
        return result
