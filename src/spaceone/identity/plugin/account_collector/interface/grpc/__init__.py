from spaceone.core.pygrpc.server import GRPCServer
from spaceone.identity.plugin.account_collector.interface.grpc.account_collector import (
    AccountCollector,
)

_all_ = ["app"]

app = GRPCServer()
app.add_service(AccountCollector)
