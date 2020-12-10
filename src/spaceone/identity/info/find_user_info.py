import functools
from spaceone.api.core.v1 import tag_pb2
from spaceone.api.identity.v1 import user_pb2

__all__ = ['FindUserInfo', 'FindUsersInfo']


def FindUserInfo(user_data: dict, minimal=False):
    info = {
        'user_id': user_data.get('user_id'),
        'name': user_data.get('name'),
        'email': user_data.get('email')
    }
    if not minimal:
        info.update({
            'tags': [tag_pb2.Tag(key=tag['key'], value=tag['value']) for tag in user_data.get('tags', [])],
        })

    return user_pb2.FindUserInfo(**info)


def FindUsersInfo(find_users_vos, total_count, **kwargs):
    results = list(map(functools.partial(FindUserInfo, **kwargs), find_users_vos))
    return user_pb2.FindUsersInfo(results=results, total_count=total_count)
