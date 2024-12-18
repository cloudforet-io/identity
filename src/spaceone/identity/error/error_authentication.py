from spaceone.core.error import *


class ERROR_AUTHENTICATION_FAILURE(ERROR_AUTHENTICATE_FAILURE):
    _message = 'A user "{user_id}" is not exist or password is not correct.'


class ERROR_NOT_AUTHENTICATED(ERROR_AUTHENTICATE_FAILURE):
    _message = "A user is not authenticated."


class ERROR_INVALID_CREDENTIALS(ERROR_AUTHENTICATE_FAILURE):
    _message = "Invalid credentials provided."


class ERROR_AUTHENTICATION_FAILURE_PLUGIN(ERROR_INTERNAL_API):
    _message = "External plugin authentication exception. (reason = {message})"


class ERROR_INVALID_GRANT_TYPE(ERROR_INVALID_ARGUMENT):
    _message = "Invalid grant type. (grant_type = {grant_type})"


class ERROR_UPDATE_PASSWORD_REQUIRED(ERROR_INVALID_ARGUMENT):
    _message = "Password reset is required.(user_id = {user_id})"


class ERROR_LOGIN_BLOCKED(ERROR_AUTHENTICATE_FAILURE):
    _message = "Login is blocked. Please try again later."
