from spaceone.core.pygrpc import BaseAPI
from spaceone.api.identity.v2 import app_pb2, app_pb2_grpc
from spaceone.identity.service.app_service import AppService


class App(BaseAPI, app_pb2_grpc.AppServicer):
    pb2 = app_pb2
    pb2_grpc = app_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)
        app_svc = AppService(metadata)
        response: dict = app_svc.create(params)
        return self.dict_to_message(response)

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)
        app_svc = AppService(metadata)
        response: dict = app_svc.update(params)
        return self.dict_to_message(response)

    def generate_client_secret(self, request, context):
        params, metadata = self.parse_request(request, context)
        app_svc = AppService(metadata)
        response: dict = app_svc.generate_client_secret(params)
        return self.dict_to_message(response)

    def enable(self, request, context):
        params, metadata = self.parse_request(request, context)
        app_svc = AppService(metadata)
        response: dict = app_svc.enable(params)
        return self.dict_to_message(response)

    def disable(self, request, context):
        params, metadata = self.parse_request(request, context)
        app_svc = AppService(metadata)
        response: dict = app_svc.disable(params)
        return self.dict_to_message(response)

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)
        app_svc = AppService(metadata)
        app_svc.delete(params)
        return self.empty()

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)
        app_svc = AppService(metadata)
        response: dict = app_svc.get(params)
        return self.dict_to_message(response)

    def check(self, request, context):
        params, metadata = self.parse_request(request, context)
        app_svc = AppService(metadata)
        response: dict = app_svc.check(params)
        return self.dict_to_message(response)

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)
        app_svc = AppService(metadata)
        response: dict = app_svc.list(params)
        return self.dict_to_message(response)

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)
        app_svc = AppService(metadata)
        response: dict = app_svc.stat(params)
        return self.dict_to_message(response)
