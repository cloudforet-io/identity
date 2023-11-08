from spaceone.core.error import *

class ERROR_NOT_SUPPORTED_MFA_TYPE(ERROR_INVALID_ARGUMENT):
    _message = 'Not supported MFA type. (mfa_type = {mfa_type})'


class ERROR_MFA_ALREADY_ENABLED(ERROR_UNKNOWN):
    _message = 'MFA already enabled. (user_id = {user_id})'


class ERROR_MFA_ALREADY_DISABLED(ERROR_UNKNOWN):
    _message = 'MFA already disabled. (user_id = {user_id})'