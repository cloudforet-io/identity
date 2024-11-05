from google.protobuf.json_format import ParseDict
from spaceone.api.identity.v2 import user_pb2, user_profile_pb2, user_profile_pb2_grpc
from spaceone.core.pygrpc import BaseAPI

from spaceone.identity.service.user_profile_service import UserProfileService


class UserProfile(BaseAPI, user_profile_pb2_grpc.UserProfileServicer):
    pb2 = user_profile_pb2
    pb2_grpc = user_profile_pb2_grpc

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)
        user_profile_svc = UserProfileService(metadata)
        response: dict = user_profile_svc.update(params)
        return ParseDict(response, user_pb2.UserInfo())

    def verify_email(self, request, context):
        params, metadata = self.parse_request(request, context)
        user_profile_svc = UserProfileService(metadata)
        user_profile_svc.verify_email(params)
        return self.empty()

    def confirm_email(self, request, context):
        params, metadata = self.parse_request(request, context)
        user_profile_svc = UserProfileService(metadata)
        response: dict = user_profile_svc.confirm_email(params)
        return ParseDict(response, user_pb2.UserInfo())

    def reset_password(self, request, context):
        params, metadata = self.parse_request(request, context)
        user_profile_svc = UserProfileService(metadata)
        user_profile_svc.reset_password(params)
        return self.empty()

    def enable_mfa(self, request, context):
        params, metadata = self.parse_request(request, context)
        user_profile_svc = UserProfileService(metadata)
        response: dict = user_profile_svc.enable_mfa(params)
        return ParseDict(response, user_pb2.UserInfo())

    def disable_mfa(self, request, context):
        params, metadata = self.parse_request(request, context)
        user_profile_svc = UserProfileService(metadata)
        response: dict = user_profile_svc.disable_mfa(params)
        return ParseDict(response, user_pb2.UserInfo())

    def confirm_mfa(self, request, context):
        params, metadata = self.parse_request(request, context)
        user_profile_svc = UserProfileService(metadata)
        response: dict = user_profile_svc.confirm_mfa(params)
        return ParseDict(response, user_pb2.UserInfo())

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)
        user_profile_svc = UserProfileService(metadata)
        response: dict = user_profile_svc.get(params)
        return ParseDict(response, user_pb2.UserInfo())

    def get_workspaces(self, request, context):
        params, metadata = self.parse_request(request, context)
        user_profile_svc = UserProfileService(metadata)
        response: dict = user_profile_svc.get_workspaces(params)
        return self.dict_to_message(response)

    def get_workspace_groups(self, request, context):
        params, metadata = self.parse_request(request, context)
        user_profile_svc = UserProfileService(metadata)
        response: dict = user_profile_svc.get_workspace_groups(params)
        return self.dict_to_message(response)
