from spaceone.core.error import *


class ERROR_UNDEFINED_SCHEMA(ERROR_INVALID_ARGUMENT):
    _message = 'Schema is not defined. (schema_type = {schema_type}, provider = {provider})'
