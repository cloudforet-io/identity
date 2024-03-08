from spaceone.core.error import *


class ERROR_DUPLICATE_JOB(ERROR_UNKNOWN):
    _message = (
        "The same job is already running. (trusted_account_id = {trusted_account_id})"
    )
