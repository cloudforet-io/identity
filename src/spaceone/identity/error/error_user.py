from spaceone.core.error import *


class ERROR_USER_STATUS_CHECK_FAILURE(ERROR_BASE):
    _message = 'A user "{user_id}" status is not ENABLED.'


class ERROR_EXTERNAL_USER_NOT_ALLOWED_API_USER(ERROR_INVALID_ARGUMENT):
    _message = 'External user cannot be created with the API_USER type.'


class ERROR_NOT_ALLOWED_EXTERNAL_AUTHENTICATION(ERROR_INVALID_ARGUMENT):
    _message = 'This domain does not allow external authentication.'


class ERROR_TOO_MANY_USERS_IN_EXTERNAL_AUTH(ERROR_INVALID_ARGUMENT):
    _message = 'There are two or more users in the external authentication system. (user_id = {user_id})'


class ERROR_NOT_FOUND_USER_IN_EXTERNAL_AUTH(ERROR_INVALID_ARGUMENT):
    _message = 'The user could not be found in the external authentication system. (user_id = {user_id})'


class ERROR_INCORRECT_PASSWORD_FORMAT(ERROR_INVALID_ARGUMENT):
    _message = 'The password format is incorrect. (rule = {rule})'


class ERROR_INCORRECT_USER_ID_FORMAT(ERROR_INVALID_ARGUMENT):
    _message = 'The user id format is incorrect. (rule = {rule})'
