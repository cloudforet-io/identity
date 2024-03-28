from spaceone.core.pygrpc import BaseAPI
from google.protobuf.json_format import ParseDict
from spaceone.api.identity.v2 import trusted_account_pb2, trusted_account_pb2_grpc
from spaceone.api.identity.v2 import job_pb2
from spaceone.identity.service.trusted_account_service import TrustedAccountService


class TrustedAccount(BaseAPI, trusted_account_pb2_grpc.TrustedAccountServicer):
    pb2 = trusted_account_pb2
    pb2_grpc = trusted_account_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)
        trusted_account_svc = TrustedAccountService(metadata)
        response: dict = trusted_account_svc.create(params)
        return self.dict_to_message(response)

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)
        trusted_account_svc = TrustedAccountService(metadata)
        response: dict = trusted_account_svc.update(params)
        return self.dict_to_message(response)

    def update_secret_data(self, request, context):
        params, metadata = self.parse_request(request, context)
        trusted_account_svc = TrustedAccountService(metadata)
        response: dict = trusted_account_svc.update_secret_data(params)
        return self.dict_to_message(response)

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)
        trusted_account_svc = TrustedAccountService(metadata)
        trusted_account_svc.delete(params)
        return self.empty()

    def sync(self, request, context):
        params, metadata = self.parse_request(request, context)
        trusted_account_svc = TrustedAccountService(metadata)
        response: dict = trusted_account_svc.sync(params)
        return ParseDict(response, job_pb2.JobInfo())

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)
        trusted_account_svc = TrustedAccountService(metadata)
        response: dict = trusted_account_svc.get(params)
        return self.dict_to_message(response)

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)
        trusted_account_svc = TrustedAccountService(metadata)
        response: dict = trusted_account_svc.list(params)
        return self.dict_to_message(response)

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)
        trusted_account_svc = TrustedAccountService(metadata)
        response: dict = trusted_account_svc.stat(params)
        return self.dict_to_message(response)
