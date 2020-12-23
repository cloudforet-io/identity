import functools
from spaceone.api.core.v1 import tag_pb2
from spaceone.api.identity.v1 import user_pb2
from spaceone.core.pygrpc.message_type import *
from spaceone.identity.model.user_model import User

__all__ = ['UserInfo', 'UsersInfo']


def UserInfo(user_vo: User, minimal=False):
    info = {
        'user_id': user_vo.user_id,
        'name': user_vo.name,
        'state': user_vo.state,
        'user_type': user_vo.user_type
    }

    if not minimal:
        info.update({
            'email': user_vo.email,
            'backend': user_vo.backend,
            'language': user_vo.language,
            'timezone': user_vo.timezone,
            'tags': [tag_pb2.Tag(key=tag.key, value=tag.value) for tag in user_vo.tags],
            'domain_id': user_vo.domain_id,
            'last_accessed_at': change_timestamp_type(user_vo.last_accessed_at),
            'created_at': change_timestamp_type(user_vo.created_at)
        })

    return user_pb2.UserInfo(**info)


def UsersInfo(user_vos, total_count, **kwargs):
    results = list(map(functools.partial(UserInfo, **kwargs), user_vos))
    return user_pb2.UsersInfo(results=results, total_count=total_count)
