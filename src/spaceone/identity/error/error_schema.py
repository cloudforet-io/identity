from spaceone.core.error import *


class ERROR_SCHEMA_IS_NOT_DEFINED(ERROR_INVALID_ARGUMENT):
    _message = "Schema is not defined. (provider={provider}, schema_type={schema_type})"


class ERROR_SCHEMA_ID_IS_NOT_DEFINED(ERROR_INVALID_ARGUMENT):
    _message = (
        "Schema ID is not defined. (schema_id={schema_id}, schema_type={schema_type})"
    )
