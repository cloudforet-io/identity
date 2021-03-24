from spaceone.core.error import *


class ERROR_NOT_ALLOWED_ROLE_TYPE(ERROR_INVALID_ARGUMENT):
    _message = 'Duplicate assignment of system role and domain or project role is not allowed.'


class ERROR_REQUIRED_PROJECT_OR_PROJECT_GROUP(ERROR_INVALID_ARGUMENT):
    _message = 'Project role require project_id or project_group_id.'


class ERROR_NOT_ALLOWED_PROJECT_ID(ERROR_INVALID_ARGUMENT):
    _message = 'Domain or system role dose not need project_id.'


class ERROR_NOT_ALLOWED_PROJECT_GROUP_ID(ERROR_INVALID_ARGUMENT):
    _message = 'Domain or system role dose not need project_group_id.'


class ERROR_DUPLICATE_ROLE_BOUND(ERROR_INVALID_ARGUMENT):
    _message = 'Duplicate role bound. (role_id = {role_id}, resource_id = {resource_id})'


class ERROR_DUPLICATE_RESOURCE_IN_PROJECT(ERROR_INVALID_ARGUMENT):
    _message = 'There are duplicate resource in the project. (project_id = {project_id}, resource_id = {resource_id})'


class ERROR_DUPLICATE_RESOURCE_IN_PROJECT_GROUP(ERROR_INVALID_ARGUMENT):
    _message = 'There are duplicate resource in the project_group. (project_group_id = {project_group_id}, resource_id = {resource_id})'


class ERROR_POLICY_IS_IN_USE(ERROR_INVALID_ARGUMENT):
    _message = 'The policy is in use by role. (policy_id = {policy_id}, role_id = {role_id})'
