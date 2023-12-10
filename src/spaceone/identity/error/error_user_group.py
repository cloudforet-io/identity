from spaceone.core.error import *


class ERROR_USERS_NOT_FOUND(ERROR_INVALID_ARGUMENT):
    _message = "Users not found. (users = {users})"
