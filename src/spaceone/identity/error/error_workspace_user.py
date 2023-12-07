from spaceone.core.error import *


class ERROR_USER_NOT_EXIST_IN_WORKSPACE(ERROR_INVALID_ARGUMENT):
    _message = "User does not exist in workspace. (user_id = {user_id}, workspace_id = {workspace_id})"
