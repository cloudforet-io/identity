from spaceone.core.error import *


class ERROR_SYSTEM_ALREADY_INITIALIZED(ERROR_INVALID_ARGUMENT):
    _message = "System is already initialized. You can force initialize with force=True option."
