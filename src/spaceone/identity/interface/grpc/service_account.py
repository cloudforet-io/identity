from spaceone.core.pygrpc import BaseAPI
from spaceone.api.identity.v2 import service_account_pb2, service_account_pb2_grpc
from spaceone.identity.service.service_account_service import (
    ServiceAccountService,
)


class ServiceAccount(BaseAPI, service_account_pb2_grpc.ServiceAccountServicer):
    pb2 = service_account_pb2
    pb2_grpc = service_account_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)
        service_account_svc = ServiceAccountService(metadata)
        response: dict = service_account_svc.create(params)
        return self.dict_to_message(response)

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)
        service_account_svc = ServiceAccountService(metadata)
        response: dict = service_account_svc.update(params)
        return self.dict_to_message(response)

    def change_trusted_service_account(self, request, context):
        params, metadata = self.parse_request(request, context)
        service_account_svc = ServiceAccountService(metadata)
        response: dict = service_account_svc.change_trusted_service_account(params)
        return self.dict_to_message(response)

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)
        service_account_svc = ServiceAccountService(metadata)
        service_account_svc.delete(params)
        return self.empty()

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)
        service_account_svc = ServiceAccountService(metadata)
        response: dict = service_account_svc.get(params)
        return self.dict_to_message(response)

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)
        service_account_svc = ServiceAccountService(metadata)
        response: dict = service_account_svc.list(params)
        return self.dict_to_message(response)

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)
        service_account_svc = ServiceAccountService(metadata)
        response: dict = service_account_svc.stat(params)
        return self.dict_to_message(response)
