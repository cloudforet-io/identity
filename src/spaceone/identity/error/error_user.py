# -*- coding: utf-8 -*-

from spaceone.core.error import *


class ERROR_USER_STATUS_CHECK_FAILURE(ERROR_BASE):
    _message = 'A user "{user_id}" status is not ENABLED.'


class ERROR_NOT_ALLOWED_ROLE_TYPE(ERROR_INVALID_ARGUMENT):
    _message = 'Duplicate assignment of system roles and domain or project roles is not allowed.'
