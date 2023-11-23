from spaceone.core.pygrpc import BaseAPI
from spaceone.api.identity.v2 import trusted_service_account_pb2, trusted_service_account_pb2_grpc
from spaceone.identity.service.trusted_service_account_service import (
    TrustedServiceAccountService,
)


class TrustedServiceAccount(
    BaseAPI, trusted_service_account_pb2_grpc.TrustedServiceAccountServicer
):
    pb2 = trusted_service_account_pb2
    pb2_grpc = trusted_service_account_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)
        trusted_service_account_svc = TrustedServiceAccountService(metadata)
        response: dict = trusted_service_account_svc.create(params)
        return self.dict_to_message(response)

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)
        trusted_service_account_svc = TrustedServiceAccountService(metadata)
        response: dict = trusted_service_account_svc.update(params)
        return self.dict_to_message(response)

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)
        trusted_service_account_svc = TrustedServiceAccountService(metadata)
        trusted_service_account_svc.delete(params)
        return self.empty()

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)
        trusted_service_account_svc = TrustedServiceAccountService(metadata)
        response: dict = trusted_service_account_svc.get(params)
        return self.dict_to_message(response)

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)
        trusted_service_account_svc = TrustedServiceAccountService(metadata)
        response: dict = trusted_service_account_svc.list(params)
        return self.dict_to_message(response)

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)
        trusted_service_account_svc = TrustedServiceAccountService(metadata)
        response: dict = trusted_service_account_svc.stat(params)
        return self.dict_to_message(response)
