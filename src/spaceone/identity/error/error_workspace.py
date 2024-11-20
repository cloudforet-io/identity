from spaceone.core.error import *


class ERROR_WORKSPACE_STATE(ERROR_INVALID_ARGUMENT):
    _message = "Workspace is disabled. (workspace_id = {workspace_id})"


class ERROR_DEFAULT_PACKAGE_NOT_ALLOWED(ERROR_INVALID_ARGUMENT):
    _message = (
        "Default package can not be added to workspace. (package_id = {package_id})"
    )
