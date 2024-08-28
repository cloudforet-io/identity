from spaceone.core.error import *


class ERROR_GENERATE_KEY_FAILURE(ERROR_BASE):
    _message = "Error on generate key."


class ERROR_MANAGED_RESOURCE_CAN_NOT_BE_MODIFIED(ERROR_UNKNOWN):
    message = "Managed resource can not be deleted. please disable schedule first."


class ERROR_WORKSPACES_DO_NOT_EXIST(ERROR_UNKNOWN):
    _message = "Resource Not Found. (key = {key}, reason = {reason})"


class ERROR_ROLE_DOES_NOT_EXIST_OF_USER(ERROR_NOT_FOUND):
    _message = "Role does not exist of User. (role_id = {role_id}, user_id = {user_id})"
