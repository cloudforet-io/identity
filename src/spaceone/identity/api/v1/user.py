from spaceone.api.identity.v1 import user_pb2, user_pb2_grpc
from spaceone.core.pygrpc import BaseAPI


class User(BaseAPI, user_pb2_grpc.UserServicer):

    pb2 = user_pb2
    pb2_grpc = user_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('UserService', metadata) as user_svc:
            return self.locator.get_info('UserInfo', user_svc.create(params))

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('UserService', metadata) as user_svc:
            return self.locator.get_info('UserInfo', user_svc.update(params))

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('UserService', metadata) as user_svc:
            user_svc.delete(params)
            return self.locator.get_info('EmptyInfo')

    def enable(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('UserService', metadata) as user_svc:
            return self.locator.get_info('UserInfo', user_svc.enable(params))

    def disable(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('UserService', metadata) as user_svc:
            return self.locator.get_info('UserInfo', user_svc.disable(params))

    def find(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('UserService', metadata) as user_svc:
            users, total_count = user_svc.find(params)
            return self.locator.get_info('FindUsersInfo', users, total_count)

    def sync(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('UserService', metadata) as user_svc:
            pass
            # data = user_service.find_user(params)
            # return self.locator.get_info('UserInfo', data)

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('UserService', metadata) as user_svc:
            return self.locator.get_info('UserInfo', user_svc.get(params))

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('UserService', metadata) as user_svc:
            users, total_count = user_svc.list(params)
            return self.locator.get_info('UsersInfo', users, total_count,
                                         minimal=self.get_minimal(params))

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('UserService', metadata) as user_svc:
            return self.locator.get_info('StatisticsInfo', user_svc.stat(params))
