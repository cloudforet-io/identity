from spaceone.core.pygrpc import BaseAPI
from spaceone.api.core.v2 import handler_pb2
from google.protobuf.json_format import ParseDict
from spaceone.api.identity.v2 import domain_pb2, domain_pb2_grpc
from spaceone.identity.service.domain_service import DomainService


class Domain(BaseAPI, domain_pb2_grpc.DomainServicer):
    pb2 = domain_pb2
    pb2_grpc = domain_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)
        domain_svc = DomainService(metadata)
        response: dict = domain_svc.create(params)
        return self.dict_to_message(response)

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)
        domain_svc = DomainService(metadata)
        response: dict = domain_svc.update(params)
        return self.dict_to_message(response)

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)
        domain_svc = DomainService(metadata)
        domain_svc.delete(params)
        return self.empty()

    def enable(self, request, context):
        params, metadata = self.parse_request(request, context)
        domain_svc = DomainService(metadata)
        response: dict = domain_svc.enable(params)
        return self.dict_to_message(response)

    def disable(self, request, context):
        params, metadata = self.parse_request(request, context)
        domain_svc = DomainService(metadata)
        response: dict = domain_svc.disable(params)
        return self.dict_to_message(response)

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)
        domain_svc = DomainService(metadata)
        response: dict = domain_svc.get(params)
        return self.dict_to_message(response)

    def get_auth_info(self, request, context):
        params, metadata = self.parse_request(request, context)
        domain_svc = DomainService(metadata)
        response: dict = domain_svc.get_auth_info(params)
        return self.dict_to_message(response)

    def get_public_key(self, request, context):
        params, metadata = self.parse_request(request, context)
        domain_svc = DomainService(metadata)
        response: dict = domain_svc.get_public_key(params)
        return ParseDict(response, handler_pb2.AuthenticationResponse())

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)
        domain_svc = DomainService(metadata)
        response: dict = domain_svc.list(params)
        return self.dict_to_message(response)

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)
        domain_svc = DomainService(metadata)
        response: dict = domain_svc.stat(params)
        return self.dict_to_message(response)
