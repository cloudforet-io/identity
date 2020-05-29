from spaceone.api.identity.v1 import domain_owner_pb2, domain_owner_pb2_grpc
from spaceone.core.pygrpc import BaseAPI


class DomainOwner(BaseAPI, domain_owner_pb2_grpc.DomainOwnerServicer):

    pb2 = domain_owner_pb2
    pb2_grpc = domain_owner_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('DomainOwnerService', metadata) as domain_owner_svc:
            data = domain_owner_svc.create_owner(params)
            return self.locator.get_info('DomainOwnerInfo', data)

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('DomainOwnerService', metadata) as domain_owner_svc:
            data = domain_owner_svc.update_owner(params)
            return self.locator.get_info('DomainOwnerInfo', data)

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('DomainOwnerService', metadata) as domain_owner_svc:
            # TODO: block delete when users, projects, inventories are existing.
            data = domain_owner_svc.delete_owner(params)
            return self.locator.get_info('EmptyInfo')

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('DomainOwnerService', metadata) as domain_owner_svc:
            data = domain_owner_svc.get_owner(params)
            return self.locator.get_info('DomainOwnerInfo', data)
