from spaceone.core.error import *


class ERROR_DOMAIN_STATE(ERROR_INVALID_ARGUMENT):
    _message = "Domain is disabled. (domain_id = {domain_id})"


class ERROR_NOT_DEFINED_DOMAIN_ADMIN(ERROR_UNKNOWN):
    _message = "Domain admin role is not defined."
