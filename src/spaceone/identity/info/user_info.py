# -*- coding: utf-8 -*-

import functools
from spaceone.api.identity.v1 import user_pb2
from spaceone.core.pygrpc.message_type import *
from spaceone.identity.model.user_model import User
from spaceone.identity.info.role_info import RoleInfo

__all__ = ['UserInfo', 'UsersInfo']


def UserInfo(user_vo: User, minimal=False):
    info = {
        'user_id': user_vo.user_id,
        'name': user_vo.name,
        'state': user_vo.state,
        'domain_id': user_vo.domain_id
    }

    if not minimal:
        info.update({
            'email': user_vo.email,
            'mobile': user_vo.mobile,
            'group': user_vo.group,
            'language': user_vo.language,
            'timezone': user_vo.timezone,
            'roles': list(map(lambda role: RoleInfo(role, minimal=True), user_vo.roles)),
            'tags': change_struct_type(user_vo.tags),
            'last_accessed_at': change_timestamp_type(user_vo.last_accessed_at),
            'created_at': change_timestamp_type(user_vo.created_at)
        })

    return user_pb2.UserInfo(**info)


def UsersInfo(user_vos, total_count, **kwargs):
    results = list(map(functools.partial(UserInfo, **kwargs), user_vos))
    return user_pb2.UsersInfo(results=results, total_count=total_count)
