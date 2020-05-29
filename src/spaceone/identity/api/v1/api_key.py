from spaceone.api.identity.v1 import api_key_pb2, api_key_pb2_grpc
from spaceone.core.pygrpc import BaseAPI


class APIKey(BaseAPI, api_key_pb2_grpc.APIKeyServicer):

    pb2 = api_key_pb2
    pb2_grpc = api_key_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('APIKeyService', metadata) as api_key_svc:
            api_key_vo, api_key = api_key_svc.create_api_key(params)
            return self.locator.get_info('APIKeyInfo', api_key_vo, api_key=api_key)

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('APIKeyService', metadata) as api_key_svc:
            api_key_svc.delete_api_key(params)
            return self.locator.get_info('EmptyInfo')

    def enable(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('APIKeyService', metadata) as api_key_svc:
            data = api_key_svc.enable_api_key(params)
            return self.locator.get_info('APIKeyInfo', data)

    def disable(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('APIKeyService', metadata) as api_key_svc:
            data = api_key_svc.disable_api_key(params)
            return self.locator.get_info('APIKeyInfo', data)

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('APIKeyService', metadata) as api_key_svc:
            data = api_key_svc.get_api_key(params)
            return self.locator.get_info('APIKeyInfo', data)

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('APIKeyService', metadata) as api_key_svc:
            api_key_vos, total_count = api_key_svc.list_api_keys(params)
            return self.locator.get_info('APIKeysInfo', api_key_vos, total_count, minimal=self.get_minimal(params))

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('APIKeyService', metadata) as api_key_svc:
            return self.locator.get_info('StatisticsInfo', api_key_svc.stat(params))
