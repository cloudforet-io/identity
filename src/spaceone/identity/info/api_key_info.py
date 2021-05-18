import functools
from spaceone.api.identity.v1 import api_key_pb2
from spaceone.core import utils
from spaceone.identity.model.api_key_model import APIKey

__all__ = ['APIKeyInfo', 'APIKeysInfo']


def APIKeyInfo(api_key_vo: APIKey, minimal=False, api_key=None, **kwargs):
    info = {
        'api_key': api_key,
        'api_key_id': api_key_vo.api_key_id,
        'state': api_key_vo.state,
        'user_id': api_key_vo.user_id
    }

    if not minimal:
        info.update({
            'domain_id': api_key_vo.domain_id,
            'last_accessed_at': utils.datetime_to_iso8601(api_key_vo.last_accessed_at),
            'created_at': utils.datetime_to_iso8601(api_key_vo.created_at)
        })

    return api_key_pb2.APIKeyInfo(**info)


def APIKeysInfo(api_key_vos, total_count, **kwargs):
    results = list(map(functools.partial(APIKeyInfo, **kwargs), api_key_vos))
    return api_key_pb2.APIKeysInfo(results=results, total_count=total_count)
