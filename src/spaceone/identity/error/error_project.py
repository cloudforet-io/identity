from spaceone.core.error import *


class ERROR_EXIST_CHILD_PROJECT_GROUP(ERROR_BASE):
    _message = "Child project group is exist. project_group_id = {project_group_id}"


class ERROR_ALREADY_EXIST_USER_IN_PROJECT_GROUP(ERROR_BASE):
    _message = (
        'A user "{user_id}" is already exist in project group({project_group_id}).'
    )


class ERROR_ALREADY_EXIST_USER_IN_PROJECT(ERROR_BASE):
    _message = 'A user "{user_id}" is already exist in project({project_id}).'


class ERROR_NOT_FOUND_USER_IN_PROJECT_GROUP(ERROR_BASE):
    _message = 'A user "{user_id}" is not exist in project group({project_group_id}).'


class ERROR_NOT_FOUND_USER_IN_PROJECT(ERROR_BASE):
    _message = 'A user "{user_id}" is not exist in project({project_id}).'


class ERROR_ONLY_PROJECT_ROLE_TYPE_ALLOWED(ERROR_INVALID_ARGUMENT):
    _message = "Only project role type can be allowed."
