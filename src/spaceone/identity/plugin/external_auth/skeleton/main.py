from spaceone.identity.plugin.external_auth.lib.server import ExternalAuthPluginServer

app = ExternalAuthPluginServer()


@app.route("ExternalAuth.init")
def external_auth_init(params: dict) -> dict:
    """init plugin by options

    Args:
        params (ExternalAuthInitRequest): {
            'options': 'dict',    # Required
            'domain_id': 'str'    # Required
        }

    Returns:
        PluginResponse: {
            'metadata': 'dict'
        }
    """
    pass


@app.route("ExternalAuth.authorize")
def external_auth_authorize(params: dict) -> dict:
    """ExternalAuth authorize

    Args:
        params (ExternalAuthAuthorizeRequest): {
            'options': 'dict',          # Required
            'schema_id': 'str',
            'secret_data': 'dict',      # Required
            'credentials': 'dict',      # Required
            'domain_id': 'str'          # Required
        }

    Returns:
        UserResponse: {
            'state': 'str',
            'user_id': 'str',
            'name': 'str',
            'email': 'str',
            'mobile': 'str',
            'group': 'str',
        }
    """
    pass
