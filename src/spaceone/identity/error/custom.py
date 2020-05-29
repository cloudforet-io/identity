# -*- coding: utf-8 -*-

from spaceone.core.error import *


class ERROR_GENERATE_KEY_FAILURE(ERROR_BASE):
    _message = 'Error on generate key.'


class ERROR_UNSUPPORTED_API(ERROR_BASE):
    _message = 'Unsupported api. (reason={reason})'
