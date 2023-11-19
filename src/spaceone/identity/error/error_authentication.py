from spaceone.core.error import *


class ERROR_AUTHENTICATION_FAILURE(ERROR_AUTHENTICATE_FAILURE):
    _message = 'A user "{user_id}" is not exist or password is not correct.'


class ERROR_NOT_AUTHENTICATED(ERROR_AUTHENTICATE_FAILURE):
    _message = "A user is not authenticated."


class ERROR_NOT_ALLOWED_ISSUE_TOKEN_API_USER(ERROR_AUTHENTICATE_FAILURE):
    _message = "API_USER are not allowed to issue tokens. (user_id = {user_id})"


class ERROR_INVALID_CREDENTIALS(ERROR_AUTHENTICATE_FAILURE):
    _message = "Invalid credentials provided."


class ERROR_AUTHENTICATION_FAILURE_PLUGIN(ERROR_INTERNAL_API):
    _message = "External plugin authentication exception. (reason = {message})"


class ERROR_INVALID_REFRESH_TOKEN(ERROR_AUTHENTICATE_FAILURE):
    _message = "Refresh token is invalid or expired."


class ERROR_REFRESH_COUNT(ERROR_AUTHENTICATE_FAILURE):
    _message = "The refresh count is exhausted."


class ERROR_NOT_FOUND_PRIVATE_KEY(ERROR_AUTHENTICATE_FAILURE):
    _message = "Private key not found. (purpose = {purpose})"


class ERROR_MAX_REFRESH_COUNT(ERROR_AUTHENTICATE_FAILURE):
    _message = "The maximum refresh count has been exceeded. (max_refresh_count = {max_refresh_count})"
