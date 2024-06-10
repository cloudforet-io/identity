from spaceone.core.error import ERROR_REQUIRED_PARAMETER


class ERROR_REQUIRED_FIELDS(ERROR_REQUIRED_PARAMETER):
    _message = "Required fields. (key = {key})"
