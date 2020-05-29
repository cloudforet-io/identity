# -*- coding: utf-8 -*-

import functools
from spaceone.api.identity.v1 import api_key_pb2
from spaceone.core.pygrpc.message_type import *
from spaceone.identity.model.api_key_model import APIKey
import logging


__all__ = ['APIKeyInfo', 'APIKeysInfo']

_LOGGER = logging.getLogger(__name__)


def APIKeyInfo(api_key_vo: APIKey, **kwargs):
    _LOGGER.debug(f'[APIKeyInfo] api_key_vo: {api_key_vo}')
    info = {}
    info['api_key'] = kwargs.get('api_key')
    info['api_key_id'] = api_key_vo.api_key_id
    info['state'] = api_key_vo.state
    # info['api_key_type'] = api_key_vo.api_key_type
    info['user_id'] = api_key_vo.user_id
    info['domain_id'] = api_key_vo.domain_id
    info['last_accessed_at'] = change_timestamp_type(api_key_vo.last_accessed_at)
    info['created_at'] = change_timestamp_type(api_key_vo.created_at)

    return api_key_pb2.APIKeyInfo(**info)


def APIKeysInfo(api_key_vos, total_count, **kwargs):
    results = list(map(functools.partial(APIKeyInfo, **kwargs), api_key_vos))
    return api_key_pb2.APIKeysInfo(results=results, total_count=total_count)
