# -*- coding: utf-8 -*-

from spaceone.api.identity.v1 import domain_owner_pb2

from spaceone.core.pygrpc.message_type import *
from spaceone.identity.model import DomainOwner

__all__ = ['DomainOwnerInfo']


def DomainOwnerInfo(owner_vo: DomainOwner, minimal=False):
    info = {
        'owner_id': owner_vo.owner_id,
        'name': owner_vo.name,
        'domain_id': owner_vo.domain_id
    }

    if not minimal:
        info.update({
            'email': owner_vo.email,
            'mobile': owner_vo.mobile,
            'language': owner_vo.language,
            'timezone': owner_vo.timezone,
            'last_accessed_at': change_timestamp_type(owner_vo.last_accessed_at),
            'created_at': change_timestamp_type(owner_vo.created_at)
        })

    return domain_owner_pb2.DomainOwnerInfo(**info)
