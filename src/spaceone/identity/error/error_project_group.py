from spaceone.core.error import *


class ERROR_RELATED_PROJECT_EXIST(ERROR_INVALID_ARGUMENT):
    _message = "Related project is exist. (project_id = {project_id})"


class ERROR_RELATED_PROJECT_GROUP_EXIST(ERROR_INVALID_ARGUMENT):
    _message = "Related project group is exist. (project_group_id = {project_group_id})"
