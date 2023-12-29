from spaceone.core.error import *


class ERROR_APP_EXPIRED_LIMIT(ERROR_INVALID_ARGUMENT):
    _message = (
        "The maximum expiration limit for apps is 365 days. (expired_at = {expired_at})"
    )
