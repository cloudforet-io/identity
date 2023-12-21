from spaceone.core.error import *


class ERROR_WORKSPACE_STATE(ERROR_INVALID_ARGUMENT):
    _message = "Workspace is disabled. (workspace_id = {workspace_id})"
