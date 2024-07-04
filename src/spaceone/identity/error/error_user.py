from spaceone.core.error import *


class ERROR_USER_STATE_DISABLED(ERROR_INVALID_ARGUMENT):
    _message = 'A user "{user_id}" state is DISABLED.'


class ERROR_APP_STATE_DISABLED(ERROR_INVALID_ARGUMENT):
    _message = 'App "{app_id}" state is DISABLED.'


class ERROR_INCORRECT_PASSWORD_FORMAT(ERROR_INVALID_ARGUMENT):
    _message = "The password format is incorrect. (rule = {rule})"


class ERROR_INCORRECT_USER_ID_FORMAT(ERROR_INVALID_ARGUMENT):
    _message = "The user id format is incorrect. (rule = {rule})"


class ERROR_INCORRECT_EMAIL_FORMAT(ERROR_INVALID_ARGUMENT):
    _message = "The email format is incorrect. (rule = {rule})"


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


class ERROR_LAST_ADMIN_CANNOT_DISABLED_DELETED(ERROR_INVALID_ARGUMENT):
    _message = "The last Domain Admin or System Admin cannot be disabled or deleted. (user_id = {user_id})"
