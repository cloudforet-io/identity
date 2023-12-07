from spaceone.core.error import *


class ERROR_SCHEMA_IN_NOT_DEFINED(ERROR_INVALID_ARGUMENT):
    _message = 'Schema is not defined. (schema_type = {schema_type}, provider = {provider})'
