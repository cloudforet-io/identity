from spaceone.core.error import *


class ERROR_RELATED_SERVICE_ACCOUNT_EXIST(ERROR_INVALID_ARGUMENT):
    _message = (
        "Related service account is exist. (service_account_id = {service_account_id})"
    )


class ERROR_NOT_ALLOWED_ADD_USER_TO_PUBLIC_PROJECT(ERROR_INVALID_ARGUMENT):
    _message = "Not allowed to add user to public project."
