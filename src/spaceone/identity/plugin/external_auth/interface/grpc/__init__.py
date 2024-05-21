from spaceone.core.pygrpc.server import GRPCServer
from spaceone.identity.plugin.external_auth.interface.grpc.external_auth import (
    ExternalAuth,
)

_all_ = ["app"]

app = GRPCServer()
app.add_service(ExternalAuth)
