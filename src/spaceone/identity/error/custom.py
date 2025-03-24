from spaceone.core.error import *


class ERROR_GENERATE_KEY_FAILURE(ERROR_BASE):
    _message = "Error on generate key."


class ERROR_MANAGED_RESOURCE_CAN_NOT_BE_MODIFIED(ERROR_UNKNOWN):
    message = "Managed resource can not be deleted. please disable schedule first."


class ERROR_WORKSPACES_DO_NOT_EXIST(ERROR_UNKNOWN):
    _message = "Resource Not Found. (key = {key}, reason = {reason})"


class ERROR_ROLE_DOES_NOT_EXIST_OF_USER(ERROR_NOT_FOUND):
    _message = "Role does not exist in User. (role_id = {role_id}, user_id = {user_id})"


class ERROR_NOT_ALLOWED_TO_DELETE_ROLE_BINDING(ERROR_INVALID_ARGUMENT):
    _message = "Not allowed to delete role binding. (workspace_group_id = {workspace_group_id}, role_binding_id = {role_binding_id})"


class ERROR_ROLE_IN_USED_AT_ROLE_BINDING(ERROR_INVALID_ARGUMENT):
    _message = "Role is in used at RoleBinding. (role_id = {role_id})"


class ERROR_WORKSPACE_EXIST_IN_WORKSPACE_GROUP(ERROR_INVALID_ARGUMENT):
    _message = """Workspace exists in Workspace Group. (workspace_id = {workspace_id}, workspace_group_id = {workspace_group_id})
               Remove the workspace from the workspace group before deleting the workspace group."""


class ERROR_USER_EXIST_IN_WORKSPACE_GROUP(ERROR_INVALID_ARGUMENT):
    _message = """User exists in Workspace Group. (user_id = {user_id}, workspace_group_id = {workspace_group_id})
               Remove the user from the workspace group before deleting the workspace group."""


class ERROR_SERVICE_ACCOUNT_MANAGER_REGISTERED(ERROR_INVALID_ARGUMENT):
    _message = "Not allowed to delete because of registered service account manager. (service_account_id = {service_account_id})"


class ERROR_USER_EMAIL_NOT_VERIFIED(ERROR_INVALID_ARGUMENT):
    _message = "User email is not verified. (user_id = {user_id})"
