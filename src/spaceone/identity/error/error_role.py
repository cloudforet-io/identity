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


class ERROR_NOT_ALLOWED_USER_STATE(ERROR_INVALID_ARGUMENT):
    _message = "User state is not allowed. (user_id = {user_id}, state = {state})"


class ERROR_DUPLICATED_ROLE_BINDING(ERROR_INVALID_ARGUMENT):
    _message = (
        "Role type is duplicated. (role_type = {role_type}), "
        "Only one {role_type} is allowed per user in the domain."
    )


class ERROR_DUPLICATED_WORKSPACE_ROLE_BINDING(ERROR_INVALID_ARGUMENT):
    _message = "Only one role binding is allowed per user in then same workspace. (choices = {allowed_role_type})"


class ERROR_NOT_ALLOWED_TO_UPDATE_OR_DELETE_ROLE_BY_SELF(ERROR_INVALID_ARGUMENT):
    _message = "You are not allowed to update or delete your own role."


class ERROR_LAST_WORKSPACE_OWNER_CANNOT_DELETE(ERROR_INVALID_ARGUMENT):
    _message = "Last workspace owner cannot be deleted."


class ERROR_LAST_DOMAIN_ADMIN_CANNOT_DELETE(ERROR_INVALID_ARGUMENT):
    _message = "Last domain admin cannot be deleted."


class ERROR_NOT_ALLOWED_TO_UPDATE_ROLE_ASSIGNED_BY_WORKSPACE_GROUP(
    ERROR_INVALID_ARGUMENT
):
    _message = "Roles assigned by a Workspace Group cannot be updated from the User menu. (role_binding_id = {role_binding_id})"
