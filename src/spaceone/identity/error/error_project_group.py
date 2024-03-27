from spaceone.core.error import *


class ERROR_RELATED_PROJECT_EXIST(ERROR_INVALID_ARGUMENT):
    _message = "Related project is exist. (project_id = {project_id})"


class ERROR_RELATED_PROJECT_GROUP_EXIST(ERROR_INVALID_ARGUMENT):
    _message = "Related project group is exist. (project_group_id = {project_group_id})"


class ERROR_NOT_ALLOWED_TO_CHANGE_PARENT_GROUP_TO_SUB_PROJECT_GROUP(
    ERROR_INVALID_ARGUMENT
):
    _message = "Not allowed to change parent group to sub project group. (project_group_id = {project_group_id})"


class ERROR_USER_NOT_IN_PROJECT_GROUP(ERROR_PERMISSION_DENIED):
    _message = "{user_id} is not in project group."
