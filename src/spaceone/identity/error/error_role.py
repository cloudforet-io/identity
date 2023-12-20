from spaceone.core.error import *


class ERROR_ROLE_IN_USED(ERROR_INVALID_ARGUMENT):
    _message = (
        "Role is used. (role_binding_id = {role_binding_id}, user_id = {user_id})"
    )


class ERROR_NOT_ALLOWED_ROLE_TYPE(ERROR_INVALID_ARGUMENT):
    _message = (
        "Role type is not allowed. (request_role_id = {request_role_id}, "
        "request_role_type = {request_role_type}, supported_role_type = {supported_role_type})"
    )
