from spaceone.core.pygrpc.server import GRPCServer
from spaceone.core.plugin.server import PluginServer
from spaceone.identity.plugin.external_auth.interface.grpc import app
from spaceone.identity.plugin.external_auth.service.external_auth_service import (
    ExternalAuthService,
)

__all__ = ["ExternalAuthPluginServer"]


class ExternalAuthPluginServer(PluginServer):
    _grpc_app: GRPCServer = app
    _global_conf_path: str = (
        "spaceone.identity.plugin.external_auth.conf.global_conf:global_conf"
    )
    _plugin_methods = {
        "ExternalAuth": {
            "service": ExternalAuthService,
            "methods": ["init", "authorize"],
        }
    }
