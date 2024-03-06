from spaceone.core.pygrpc.server import GRPCServer
from spaceone.core.plugin.server import PluginServer
from spaceone.identity.plugin.account_collector.interface.grpc import app
from spaceone.identity.plugin.account_collector.service.account_collector_service import (
    AccountCollectorService,
)

__all__ = ["AccountCollectorPluginServer"]


class AccountCollectorPluginServer(PluginServer):
    _grpc_app: GRPCServer = app
    _global_conf_path: str = (
        "spaceone.identity.plugin.account_collector.conf.global_conf:global_conf"
    )
    _plugin_methods = {
        "AccountCollector": {
            "service": AccountCollectorService,
            "methods": ["init", "sync"],
        }
    }
