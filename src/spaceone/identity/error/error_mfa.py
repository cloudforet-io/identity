from spaceone.core.error import *


class ERROR_NOT_SUPPORTED_MFA_TYPE(ERROR_INVALID_ARGUMENT):
    _message = "Not supported MFA type. (support_mfa_types = {support_mfa_types})"


class ERROR_MFA_ALREADY_ENABLED(ERROR_UNKNOWN):
    _message = "MFA already enabled. (user_id = {user_id})"


class ERROR_MFA_ALREADY_DISABLED(ERROR_UNKNOWN):
    _message = "MFA already disabled. (user_id = {user_id})"


class ERROR_MFA_REQUIRED(ERROR_UNKNOWN):
    _message = "MFA is required. (user_id = {user_id}), (mfa_type = {mfa_type})"


class ERROR_MFA_NOT_ENABLED(ERROR_UNKNOWN):
    _message = "MFA is not enabled. (user_id = {user_id})"
