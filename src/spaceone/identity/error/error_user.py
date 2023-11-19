from spaceone.core.error import *


class ERROR_USER_STATUS_CHECK_FAILURE(ERROR_BASE):
    _message = 'A user "{user_id}" status is not ENABLED.'


class ERROR_EXTERNAL_USER_NOT_ALLOWED_API_USER(ERROR_INVALID_ARGUMENT):
    _message = "External user cannot be created with the API_USER type."


class ERROR_NOT_ALLOWED_EXTERNAL_AUTHENTICATION(ERROR_INVALID_ARGUMENT):
    _message = "This domain does not allow external authentication."


class ERROR_TOO_MANY_USERS_IN_EXTERNAL_AUTH(ERROR_INVALID_ARGUMENT):
    _message = "There are two or more users in the external authentication system. (user_id = {user_id})"


class ERROR_NOT_FOUND_USER_IN_EXTERNAL_AUTH(ERROR_INVALID_ARGUMENT):
    _message = "The user could not be found in the external authentication system. (user_id = {user_id})"


class ERROR_INCORRECT_PASSWORD_FORMAT(ERROR_INVALID_ARGUMENT):
    _message = "The password format is incorrect. (rule = {rule})"


class ERROR_INCORRECT_USER_ID_FORMAT(ERROR_INVALID_ARGUMENT):
    _message = "The user id format is incorrect. (rule = {rule})"


class ERROR_NOT_ALLOWED_ACTIONS(ERROR_INVALID_ARGUMENT):
    _message = "External or API user are supported for actions. (action = {action})"


class ERROR_VERIFICATION_UNAVAILABLE(ERROR_INVALID_ARGUMENT):
    _message = "Email verification incomplete. (user_id = {user_id})"


class ERROR_INVALID_VERIFY_CODE(ERROR_VERIFICATION_UNAVAILABLE):
    _message = "Invalid verify code. (verify_code = {verify_code})"


class ERROR_UNABLE_TO_RESET_PASSWORD(ERROR_INVALID_ARGUMENT):
    _message = "Unable to reset password. (user_id = {user_id})"


class ERROR_PASSWORD_NOT_CHANGED(ERROR_UNABLE_TO_RESET_PASSWORD):
    _message = (
        "The password cannot be the same as the old password. (user_id = {user_id})"
    )


class ERROR_UNABLE_TO_RESET_PASSWORD_IN_EXTERNAL_AUTH(ERROR_UNABLE_TO_RESET_PASSWORD):
    _message = "Unable to reset password in external authentication system. (user_id = {user_id})"


class ERROR_UNABLE_TO_RESET_PASSWORD_WITHOUT_EMAIL(ERROR_UNABLE_TO_RESET_PASSWORD):
    _message = "Unable to reset password without email. (user_id = {user_id})"
