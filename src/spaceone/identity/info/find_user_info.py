# -*- coding: utf-8 -*-
import functools

from spaceone.api.identity.v1 import user_pb2

__all__ = ['FindUserInfo', 'FindUsersInfo']


def FindUserInfo(user_data: dict, minimal=False):
    info = {
        'user_id': user_data.get('user_id', None),
        'email': user_data.get('email', None),
        'state': user_data.get('state', None)
    }
    if not minimal:
        info.update({
            'name': user_data.get('name', None),
            'mobile': user_data.get('mobile', None),
            'group': user_data.get('group', None)
        })

    return user_pb2.FindUserInfo(**info)


def FindUsersInfo(find_users_vos, total_count, **kwargs):
    results = list(map(functools.partial(FindUserInfo, **kwargs), find_users_vos))
    return user_pb2.FindUsersInfo(results=results, total_count=total_count)
