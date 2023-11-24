from spaceone.core.error import *


class ERROR_PROJECT_GROUP_USED_IN_CHILD_PROJECT_GORUP(ERROR_BASE):
    _message = "Child project group is exist. project_group_id = {project_group_id}"


class ERROR_PROJECT_GROUP_USED_IN_PROJECT(ERROR_BASE):
    _message = "Project group is used in project. project_group_id = {project_group_id}"
