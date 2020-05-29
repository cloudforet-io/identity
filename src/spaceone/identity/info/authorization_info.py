# -*- coding: utf-8 -*-

from spaceone.core.pygrpc.message_type import *

__all__ = ['AuthorizationResponse']


def AuthorizationResponse(auth_data):
    return change_handler_authorization_response(auth_data)
