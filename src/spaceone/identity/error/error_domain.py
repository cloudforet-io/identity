from spaceone.core.error import *


class ERROR_DOMAIN_STATE(ERROR_INVALID_ARGUMENT):
    _message = "Domain is disabled. (domain_id = {domain_id})"


class ERROR_DOMAIN_ADMIN_ROLE_IS_NOT_DEFINED(ERROR_UNKNOWN):
    _message = "Domain admin role is not defined."
