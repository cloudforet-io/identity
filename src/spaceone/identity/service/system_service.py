import logging
from typing import Union

from spaceone.core.service import *
from spaceone.core.service.utils import *
from spaceone.core.auth.jwt import JWTAuthenticator

from spaceone.identity.manager.domain_manager import DomainManager
from spaceone.identity.manager.domain_secret_manager import DomainSecretManager
from spaceone.identity.manager.role_manager import RoleManager
from spaceone.identity.manager.role_binding_manager import RoleBindingManager
from spaceone.identity.manager.user_manager import UserManager
from spaceone.identity.manager.system_manager import SystemManager
from spaceone.identity.model.system.request import *
from spaceone.identity.model.system.response import *
from spaceone.identity.error.error_system import *
from spaceone.identity.error.error_domain import *

_LOGGER = logging.getLogger(__name__)


@event_handler
class SystemService(BaseService):
    resource = "System"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.domain_mgr = DomainManager()
        self.domain_secret_mgr = DomainSecretManager()
        self.user_mgr = UserManager()
        self.role_manager = RoleManager()

    @transaction()
    @convert_model
    def init(self, params: SystemInitRequest) -> Union[SystemResponse, dict]:
        """Init System
        Args:
            params (SystemInitRequest): {
                'admin': 'dict',    # required
                'force': 'bool'
            }
        Returns:
            SystemResponse:
        """

        system_mgr = SystemManager()

        root_domain_id = system_mgr.get_root_domain_id()
        root_domain_vos = self.domain_mgr.filter_domains(domain_id=root_domain_id)

        if root_domain_vos.count() == 0:
            _LOGGER.debug(f"[init] Create root domain: {root_domain_id}")
            root_domain_vo = self.domain_mgr.create_domain(
                {"domain_id": root_domain_id, "name": "root"}
            )

            self.domain_secret_mgr.delete_domain_secret(root_domain_vo.domain_id)
            self.domain_secret_mgr.create_domain_secret(root_domain_vo)

        else:
            if params.force is False:
                raise ERROR_SYSTEM_ALREADY_INITIALIZED()

            # Check System Token
            try:
                token = self.transaction.get_meta("token")
                root_pub_jwk = self.domain_secret_mgr.get_domain_public_key(
                    root_domain_id
                )
                JWTAuthenticator(root_pub_jwk).validate(token)
            except Exception as e:
                raise ERROR_UNKNOWN(message="Invalid System Token")

            root_domain_vo = root_domain_vos[0]

            _LOGGER.debug(
                f"[init] Reset root domain secret: {root_domain_vo.domain_id}"
            )
            self.domain_secret_mgr.delete_domain_secret(root_domain_vo.domain_id)
            self.domain_secret_mgr.create_domain_secret(root_domain_vo)

        if params.force:
            user_vos = self.user_mgr.filter_users(domain_id=root_domain_vo.domain_id)
            for user_vo in user_vos:
                _LOGGER.debug(
                    f"[init] Delete existing user in root domain: {user_vo.user_id}"
                )
                self.user_mgr.delete_user_by_vo(user_vo)

        # create admin user
        _LOGGER.debug(f"[init] Create admin user: {params.admin.user_id}")
        params_admin = params.admin.dict()
        params_admin["auth_type"] = "LOCAL"
        params_admin["domain_id"] = root_domain_vo.domain_id
        params_admin["role_type"] = "DOMAIN_ADMIN"
        params_admin["role_id"] = "managed-domain-admin"
        user_vo = self.user_mgr.create_user(params_admin)

        # create default role
        role_mgr = RoleManager()
        role_mgr.list_roles({}, root_domain_vo.domain_id)
        role_vos = self.role_manager.filter_roles(
            domain_id=root_domain_vo.domain_id, role_type="DOMAIN_ADMIN"
        )

        if len(role_vos) == 0:
            raise ERROR_DOMAIN_ADMIN_ROLE_IS_NOT_DEFINED()

        # create role binding
        _LOGGER.debug(
            f"[init] Create role binding: {user_vo.user_id} ({role_vos[0].role_id})"
        )
        role_binding_mgr = RoleBindingManager()
        params_rb = {
            "user_id": user_vo.user_id,
            "role_id": role_vos[0].role_id,
            "scope": "DOMAIN",
            "domain_id": user_vo.domain_id,
            "role_type": role_vos[0].role_type,
        }
        role_binding_mgr.create_role_binding(params_rb)

        system_token = system_mgr.create_system_token(
            root_domain_vo.domain_id, user_vo.user_id
        )

        response = {
            "domain_id": root_domain_vo.domain_id,
            "name": root_domain_vo.name,
            "system_token": system_token,
        }

        return SystemResponse(**response)
