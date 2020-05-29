# -*- coding: utf-8 -*-

from spaceone.core.error import *


class ERROR_AUTHENTICATION_FAILURE(ERROR_AUTHENTICATE_FAILURE):
    _message = 'A user "{user_id}" is not exist or password is not correct.'


class ERROR_NOT_AUTHENTICATED(ERROR_AUTHENTICATE_FAILURE):
    _message = 'A user is not authenticated.'


class ERROR_AUTHENTICATED_WITHOUT_USER(ERROR_AUTHENTICATE_FAILURE):
    _message = 'Token is authenticated, however user is not exists.'


class ERROR_INVALID_CREDENTIALS(ERROR_AUTHENTICATE_FAILURE):
    _message = 'Invalid credentials provided.'


class ERROR_AUTHENTICATION_FAILURE_PLUGIN(ERROR_INTERNAL_API):
    _message = 'External plugin authentication exception. (reason={message})'


class ERROR_INVALID_REFRESH_TOKEN(ERROR_AUTHENTICATE_FAILURE):
    _message = 'Refresh token is invalid or expired.'


class ERROR_REFRESH_COUNT(ERROR_AUTHENTICATE_FAILURE):
    _message = 'The refresh count is exhausted.'


class ERROR_NOT_FOUND_PRIVATE_KEY(ERROR_AUTHENTICATE_FAILURE):
    _message = 'Private key not found.'
