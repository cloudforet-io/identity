from spaceone.core.pygrpc import BaseAPI
from spaceone.api.identity.v2 import schema_pb2, schema_pb2_grpc
from spaceone.identity.service.schema_service import SchemaService


class Schema(BaseAPI, schema_pb2_grpc.SchemaServicer):
    pb2 = schema_pb2
    pb2_grpc = schema_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)
        schema_svc = SchemaService(metadata)
        response: dict = schema_svc.create(params)
        return self.dict_to_message(response)

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)
        schema_svc = SchemaService(metadata)
        response: dict = schema_svc.update(params)
        return self.dict_to_message(response)

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)
        service_account_svc = SchemaService(metadata)
        service_account_svc.delete(params)
        return self.empty()

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)
        schema_svc = SchemaService(metadata)
        response: dict = schema_svc.get(params)
        return self.dict_to_message(response)

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)
        schema_svc = SchemaService(metadata)
        response: dict = schema_svc.list(params)
        return self.dict_to_message(response)

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)
        schema_svc = SchemaService(metadata)
        response: dict = schema_svc.stat(params)
        return self.dict_to_message(response)
