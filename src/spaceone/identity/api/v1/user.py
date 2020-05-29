from spaceone.api.identity.v1 import user_pb2, user_pb2_grpc
from spaceone.core.pygrpc import BaseAPI


class User(BaseAPI, user_pb2_grpc.UserServicer):

    pb2 = user_pb2
    pb2_grpc = user_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('UserService', metadata) as user_svc:
            return self.locator.get_info('UserInfo', user_svc.create_user(params))

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('UserService', metadata) as user_svc:
            return self.locator.get_info('UserInfo', user_svc.update_user(params))

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('UserService', metadata) as user_svc:
            user_svc.delete_user(params)
            return self.locator.get_info('EmptyInfo')

    def enable(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('UserService', metadata) as user_svc:
            return self.locator.get_info('UserInfo', user_svc.enable_user(params))

    def disable(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('UserService', metadata) as user_svc:
            return self.locator.get_info('UserInfo', user_svc.disable_user(params))

    def update_role(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('UserService', metadata) as user_svc:
            return self.locator.get_info('UserInfo', user_svc.update_role(params))

    def find(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('UserService', metadata) as user_svc:
            users, total_count = user_svc.find_user(params)
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
            return self.locator.get_info('UserInfo', user_svc.get_user(params))

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('UserService', metadata) as user_svc:
            users, total_count = user_svc.list_users(params)
            return self.locator.get_info('UsersInfo', users, total_count,
                                         minimal=self.get_minimal(params))

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('UserService', metadata) as user_svc:
            return self.locator.get_info('StatisticsInfo', user_svc.stat(params))
