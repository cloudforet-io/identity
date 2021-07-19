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

        if 'plugin_info' in params:
            plugin_info = params['plugin_info']
            _LOGGER.debug(f'[create_domain] plugin_info: {plugin_info}')
            # plugin_connector: SpaceConnector = self.locator.get_connector('SpaceConnector', service='plugin')
            # response = plugin_connector.dispatch(
            #     'Plugin.get_plugin_endpoint',
            #     {
            #         'plugin_id': plugin_info['plugin_id'],
            #         'version': plugin_info['version'],
            #         'labels': {},
            #         'domain_id': params['domain_id']
            #     }
            # )
            # _LOGGER.debug(f'endpoint: {response["endpoint"]}')

        domain_vo: Domain = self.domain_model.create(params)

        self.transaction.add_rollback(_rollback, domain_vo)

        return domain_vo

    def update_domain(self, params):
        def _rollback(old_data):
            _LOGGER.info(f'[update_domain._rollback] Revert Data : {old_data["name"]} ({old_data["domain_id"]})')
            domain_vo.update(old_data)

        domain_vo: Domain = self.get_domain(params['domain_id'])
        domain_dict = domain_vo.to_dict()
        old_plugin_info = domain_dict.get('plugin_info', {})
        old_secret_id = old_plugin_info.get('secret_id', None)

        self.transaction.add_rollback(_rollback, domain_vo.to_dict())
        domain_id = params['domain_id']
        if 'plugin_info' in params:
            # TODO: Check Plugin
            plugin_info = params['plugin_info']
            _LOGGER.debug('[update_domain] plugin_info: %s' % plugin_info)
            secret_data = plugin_info.get('secret_data', None)
            if secret_data:
                if old_secret_id:
                    secret_id = self._update_secret_data(old_secret_id, secret_data, domain_id)
                else:
                    secret_id = self._create_secret(domain_id, secret_data)
                if secret_id:
                    plugin_info['secret_id'] = secret_id
                    del plugin_info['secret_data']

            endpoint = self._get_plugin_endpoint(domain_id, plugin_info)
            if endpoint:
                # grpc://dev-docker.pyengine.net:50060
                # verify plugin
                # plugin will return options
                # TODO: secret_id
                params['options'] = plugin_info['options']

                result = self._auth_init_and_verify(endpoint, params)
                _LOGGER.debug('[update_domain] endpoint: %s' % endpoint)
                _LOGGER.debug(f'[update_domain] PluginInfo: {result}')
                #plugin_info['options'] = result['options']
                plugin_info['metadata'] = result['metadata']
                params['plugin_info'] = plugin_info

        return domain_vo.update(params)

    def change_auth_plugin(self, params):
        def _rollback(old_data):
            _LOGGER.info(f'[update_domain._rollback] Revert Data : {old_data["name"]} ({old_data["domain_id"]})')
            domain_vo.update(old_data)

        domain_vo: Domain = self.get_domain(params['domain_id'])
        domain_dict = dict(domain_vo.to_dict())
        old_plugin_info = domain_dict.get('plugin_info', {})
        if old_plugin_info == None:
            old_secret_id = None
        else:
            old_secret_id = old_plugin_info.get('secret_id', None)

        self.transaction.add_rollback(_rollback, domain_vo.to_dict())
        domain_id = params['domain_id']
        if 'plugin_info' in params:
            # TODO: Check Plugin
            plugin_info = params['plugin_info']
            _LOGGER.debug('[update_domain] plugin_info: %s' % plugin_info)
            secret_data = plugin_info.get('secret_data', None)

            # Check endpoint first
            endpoint = self._get_plugin_endpoint(domain_id, plugin_info)
            if endpoint:
                # grpc://dev-docker.pyengine.net:50060
                # verify plugin
                # plugin will return options
                params['options'] = plugin_info['options']

                result = self._auth_init_and_verify(endpoint, params)
                _LOGGER.debug('[update_domain] endpoint: %s' % endpoint)
                _LOGGER.debug(f'[update_domain] PluginInfo: {result}')
                #plugin_info['options'] = result['options']
                plugin_info['metadata'] = result['metadata']

            if secret_data:
                # TODO: rollback secret_data
                if old_secret_id:
                    _LOGGER.debug(f'update secret_data of {old_secret_id}')
                    secret_id = self._update_secret_data(old_secret_id, secret_data, domain_id)
                else:
                    _LOGGER.debug(f'create new secret_id')
                    secret_id = self._create_secret(domain_id, secret_data)
                if secret_id:
                    plugin_info['secret_id'] = secret_id
                    del plugin_info['secret_data']

            params['plugin_info'] = plugin_info

        return domain_vo.update(params)


    def release_auth_plugin(self, domain_id):
        """ release plugin_info
        """
        def _rollback(old_data):
            _LOGGER.info(f'[update_domain._rollback] Revert Data : {old_data["name"]} ({old_data["domain_id"]})')
            domain_vo.update(old_data)

        domain_vo: Domain = self.get_domain(domain_id)
        self.transaction.add_rollback(_rollback, domain_vo.to_dict())
        # clean plugin_info
        # secret_id, if exist
        domain_dict = domain_vo.to_dict()
        plugin_info = domain_dict.get('plugin_info', {})
        if 'secret_id' in  plugin_info:
            self._delete_secret(plugin_info['secret_id'], domain_id)

        params = {'plugin_info': {}}
        return domain_vo.update(params)

    def update_domain_plugin(self, domain_id, version=None, options=None):
        """ Update plugin of domain
        If options exists, it should be complete content.
        """
        domain_vo: Domain = self.get_domain(domain_id)
        domain_dict = domain_vo.to_dict()
        current_plugin_info = domain_dict.get('plugin_info', {})
        new_plugin_info = current_plugin_info.copy()
        _LOGGER.debug(f'[update_domain_plugin] plugin_info: {new_plugin_info}')
        if version:
            new_plugin_info['version'] = version
        if options:
            new_plugin_info['options'] = options
        endpoint = self._get_plugin_endpoint(domain_id, new_plugin_info)
        if endpoint:
            # grpc://dev-docker.pyengine.net:50060
            # verify plugin
            # plugin will return options
            # TODO: secret_id
            # params = {
            #     'options': plugin_info['options'],
            #     'credentials': {}
            # }

            result = self._auth_init_and_verify(endpoint, new_plugin_info)
            _LOGGER.debug('[update_domain] endpoint: %s' % endpoint)
            _LOGGER.debug(f'[update_domain] PluginInfo: {result}')
            #plugin_info['options'] = result['options']
            new_plugin_info['metadata'] = result['metadata']
            _LOGGER.debug(f'[update_domain_plugin] new plugin_info: {new_plugin_info}')
            return domain_vo.update({'plugin_info': new_plugin_info})
        else:
            _LOGGER.error(f'[update_domain_plugin] fail to get endpoint: {endpoint}')
            raise ERROR_DOMAIN_PLUGIN(domain=domain_id, version = new_plugin_info['version'])

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

    def _get_plugin_endpoint(self, domain_id, plugin_info):
        plugin_connector: SpaceConnector = self.locator.get_connector('SpaceConnector', service='plugin')
        response = plugin_connector.dispatch(
            'Plugin.get_plugin_endpoint',
            {
                'plugin_id': plugin_info['plugin_id'],
                'version': plugin_info['version'],
                'labels': {},
                'domain_id': domain_id
            }
        )
        return response['endpoint']

    def _auth_init_and_verify(self, endpoint, params):
        auth: AuthPluginConnector = self.locator.get_connector('AuthPluginConnector')
        auth.initialize(endpoint)
        # update options based on return verify
        #result = auth.verify(params.get("options"), params.get("credentials"))
        result = auth.init(params.get("options"))
        return result

    def _create_secret(self, domain_id, secret_data):
        secret_connector: SpaceConnector = self.locator.get_connector('SpaceConnector',
                                                                                 service='secret')
        params = {
                'name': 'domain_auth_plugin_credential',
                'data': secret_data,
                'secret_type': 'CREDENTIALS',
                'domain_id': domain_id
                }
        resp = secret_connector.dispatch('Secret.create', params)
        _LOGGER.debug(f'[_create_secret] {resp}')
        return resp.get('secret_id', None)

    def _delete_secret(self, secret_id, domain_id):
        secret_connector: SpaceConnector = self.locator.get_connector('SpaceConnector',
                                                                                 service='secret')
        params = {
                'secret_id': secret_id,
                'domain_id': domain_id
                }
        resp = secret_connector.dispatch('Secret.delete', params)


    def _update_secret_data(self, secret_id, secret_data, domain_id):
        secret_connector: SpaceConnector = self.locator.get_connector('SpaceConnector',
                                                                                 service='secret')
        params = {
                'secret_id': secret_id,
                'data': secret_data,
                'domain_id': domain_id
                }
        resp = secret_connector.dispatch('Secret.update_data', params)
        _LOGGER.debug(f'[_update_secret_data] {resp}')
        return secret_id


    def _cleanup_plugin_info(self, plugin_info, domain_id):
        """ Clean up plugin_info
        secret_id
        """
        if 'secret_id' in plugin_info:
            # delete secret_id
            secret_connector: SpaceConnector = self.locator.get_connector('SpaceConnector',
                                                                                     service='secret')
            params = {
                    'secret_id': plugin_info['secret_id'],
                    'domain_id': domain_id
                    }
            resp = secret_connector.dispatch('Secret.delete', params)

