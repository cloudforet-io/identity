from spaceone.core.pygrpc.server import GRPCServer
from spaceone.identity.interface.grpc.api_key import APIKey
from spaceone.identity.interface.grpc.authorization import Authorization
from spaceone.identity.interface.grpc.domain import Domain
from spaceone.identity.interface.grpc.domain_owner import DomainOwner
from spaceone.identity.interface.grpc.endpoint import Endpoint
from spaceone.identity.interface.grpc.policy import Policy
from spaceone.identity.interface.grpc.project import Project
from spaceone.identity.interface.grpc.project_group import ProjectGroup
from spaceone.identity.interface.grpc.provider import Provider
from spaceone.identity.interface.grpc.role import Role
from spaceone.identity.interface.grpc.role_binding import RoleBinding
from spaceone.identity.interface.grpc.service_account import ServiceAccount
from spaceone.identity.interface.grpc.token import Token
from spaceone.identity.interface.grpc.user import User

_all_ = ['app']


app = GRPCServer()
app.add_service(APIKey)
app.add_service(Authorization)
app.add_service(Domain)
app.add_service(DomainOwner)
app.add_service(Endpoint)
app.add_service(Policy)
app.add_service(Project)
app.add_service(ProjectGroup)
app.add_service(Provider)
app.add_service(Role)
app.add_service(RoleBinding)
app.add_service(ServiceAccount)
app.add_service(Token)
app.add_service(User)