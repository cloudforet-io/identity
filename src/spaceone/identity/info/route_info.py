# -*- coding: utf-8 -*-

from spaceone.core.pygrpc.message_type import *
from spaceone.api.identity.v1 import route_pb2

__all__ = ['RouteResponse']


def RouteResponse(data):
    return route_pb2.RouteResponse(name=data['name'])
