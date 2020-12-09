from spaceone.api.identity.v1 import domain_pb2, domain_pb2_grpc
from spaceone.core.pygrpc import BaseAPI


class Domain(BaseAPI, domain_pb2_grpc.DomainServicer):

    pb2 = domain_pb2
    pb2_grpc = domain_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('DomainService', metadata) as domain_svc:
            data = domain_svc.create(params)
            return self.locator.get_info('DomainInfo', data)

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('DomainService', metadata) as domain_svc:
            data = domain_svc.update(params)
            return self.locator.get_info('DomainInfo', data)

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('DomainService', metadata) as domain_svc:
            domain_svc.delete(params)
            return self.locator.get_info('EmptyInfo')

    def enable(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('DomainService', metadata) as domain_svc:
            data = domain_svc.enable(params)
            return self.locator.get_info('DomainInfo', data)

    def disable(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('DomainService', metadata) as domain_svc:
            data = domain_svc.disable(params)
            return self.locator.get_info('DomainInfo', data)

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('DomainService', metadata) as domain_svc:
            data = domain_svc.get(params)
            return self.locator.get_info('DomainInfo', data)

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('DomainService', metadata) as domain_svc:
            data, total_count = domain_svc.list(params)
            return self.locator.get_info('DomainsInfo', data, total_count, minimal=self.get_minimal(params))

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('DomainService', metadata) as domain_svc:
            return self.locator.get_info('StatisticsInfo', domain_svc.stat(params))

    def get_public_key(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('DomainService', metadata) as domain_svc:
            data = domain_svc.get_public_key(params)
            return self.locator.get_info('DomainPublicKeyInfo', data['pub_jwk'], data['domain_id'])
