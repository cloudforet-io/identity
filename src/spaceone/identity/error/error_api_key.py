from spaceone.core.error import *


class ERROR_API_KEY_EXPIRED_LIMIT(ERROR_INVALID_ARGUMENT):
    _message = "API Key expired limit is 365 days. (expired_at = {expired_at})"
