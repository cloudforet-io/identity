from spaceone.api.core.v1 import handler_pb2

__all__ = ['AuthorizationResponse']


def AuthorizationResponse(auth_data):
    return handler_pb2.AuthorizationResponse(**auth_data)
