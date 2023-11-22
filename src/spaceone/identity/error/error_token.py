from spaceone.core.error import *


class ERROR_INVALID_AUTHENTICATION_TYPE(ERROR_INVALID_ARGUMENT):
    _message = "Invalid authentication type (LOCAL OR EXTERNAL). (authentication_type = {authentication_type})"
