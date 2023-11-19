from spaceone.core.error import *


class ERROR_DOMAIN_STATE(ERROR_BASE):
    _message = "Domain is disabled (domain_id = {domain_id})"


class ERROR_DOMAIN_AUTH_PLUGIN(ERROR_BASE):
    _message = "Failed to get endpoint of version = {version}, domain_id = {domain_id}"


class ERROR_EXTERNAL_USER_NOT_ALLOWED_API_USER(ERROR_INVALID_ARGUMENT):
    _message = "External user cannot be created with the API_USER type."


class ERROR_NOT_ALLOWED_ROLE_TYPE(ERROR_INVALID_ARGUMENT):
    _message = "Duplicate assignment of system roles and domain or project roles is not allowed."


class ERROR_NOT_ALLOWED_EXTERNAL_AUTHENTICATION(ERROR_INVALID_ARGUMENT):
    _message = "This domain does not allow external authentication."


class ERROR_PLUGIN_IS_NOT_SET(ERROR_BASE):
    _message = "External auth plugin is not set. First, execute the 'change_auth_plugin' API to set the plugin."
