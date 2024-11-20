from spaceone.core.pygrpc.server import GRPCServer

from spaceone.identity.interface.grpc.agent import Agent
from spaceone.identity.interface.grpc.app import App
from spaceone.identity.interface.grpc.domain import Domain
from spaceone.identity.interface.grpc.endpoint import Endpoint
from spaceone.identity.interface.grpc.external_auth import ExternalAuth
from spaceone.identity.interface.grpc.job import Job
from spaceone.identity.interface.grpc.project import Project
from spaceone.identity.interface.grpc.project_group import ProjectGroup
from spaceone.identity.interface.grpc.provider import Provider
from spaceone.identity.interface.grpc.package import Package
from spaceone.identity.interface.grpc.role import Role
from spaceone.identity.interface.grpc.role_binding import RoleBinding
from spaceone.identity.interface.grpc.schema import Schema
from spaceone.identity.interface.grpc.service_account import ServiceAccount
from spaceone.identity.interface.grpc.system import System
from spaceone.identity.interface.grpc.token import Token
from spaceone.identity.interface.grpc.trusted_account import TrustedAccount
from spaceone.identity.interface.grpc.user import User
from spaceone.identity.interface.grpc.user_group import UserGroup
from spaceone.identity.interface.grpc.user_profile import UserProfile
from spaceone.identity.interface.grpc.workspace import Workspace
from spaceone.identity.interface.grpc.workspace_group import WorkspaceGroup
from spaceone.identity.interface.grpc.workspace_group_user import WorkspaceGroupUser
from spaceone.identity.interface.grpc.workspace_user import WorkspaceUser

_all_ = ["app"]

app = GRPCServer()
app.add_service(System)
app.add_service(Domain)
app.add_service(ExternalAuth)
app.add_service(Endpoint)
app.add_service(Workspace)
app.add_service(ProjectGroup)
app.add_service(Project)
app.add_service(Provider)
app.add_service(Package)
app.add_service(Schema)
app.add_service(TrustedAccount)
app.add_service(ServiceAccount)
app.add_service(Job)
app.add_service(Role)
app.add_service(RoleBinding)
app.add_service(UserProfile)
app.add_service(User)
app.add_service(WorkspaceUser)
app.add_service(UserGroup)
app.add_service(App)
app.add_service(Token)
app.add_service(Agent)
app.add_service(WorkspaceGroup)
app.add_service(WorkspaceGroupUser)
