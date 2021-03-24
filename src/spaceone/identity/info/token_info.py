from spaceone.api.identity.v1 import token_pb2

__all__ = ['TokenInfo']


def TokenInfo(token_data):
    info = {
        'access_token': token_data['access_token'],
        'refresh_token': token_data['refresh_token']
    }

    return token_pb2.TokenInfo(**info)