from spaceone.core.pygrpc import BaseAPI
from spaceone.api.identity.v2 import package_pb2, package_pb2_grpc
from spaceone.identity.service.package_service import PackageService


class Package(BaseAPI, package_pb2_grpc.PackageServicer):
    pb2 = package_pb2
    pb2_grpc = package_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)
        package_svc = PackageService(metadata)
        response: dict = package_svc.create(params)
        return self.dict_to_message(response)

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)
        package_svc = PackageService(metadata)
        response: dict = package_svc.update(params)
        return self.dict_to_message(response)

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)
        package_svc = PackageService(metadata)
        package_svc.delete(params)
        return self.empty()

    def set_default(self, request, context):
        params, metadata = self.parse_request(request, context)
        package_svc = PackageService(metadata)
        response: dict = package_svc.set_default(params)
        return self.dict_to_message(response)

    def change_order(self, request, context):
        params, metadata = self.parse_request(request, context)
        package_svc = PackageService(metadata)
        response: dict = package_svc.change_order(params)
        return self.dict_to_message(response)

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)
        package_svc = PackageService(metadata)
        response: dict = package_svc.get(params)
        return self.dict_to_message(response)

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)
        package_svc = PackageService(metadata)
        response: dict = package_svc.list(params)
        return self.dict_to_message(response)

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)
        package_svc = PackageService(metadata)
        response: dict = package_svc.stat(params)
        return self.dict_to_message(response)
