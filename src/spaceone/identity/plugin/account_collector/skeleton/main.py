from spaceone.identity.plugin.account_collector.lib.server import (
    AccountCollectorPluginServer,
)

app = AccountCollectorPluginServer()


@app.route("AccountCollector.init")
def account_collector_init(params: dict) -> dict:
    """init plugin by options

    Args:
        params (CollectorInitRequest): {
            'options': 'dict',    # Required
            'domain_id': 'str'
        }

    Returns:
        PluginResponse: {
            'metadata': 'dict'
        }
    """
    pass


@app.route("AccountCollector.sync")
def account_collector_sync(params: dict) -> dict:
    """AccountCollector sync

    Args:
        params (AccountCollectorInit): {
            'options': 'dict',          # Required
            'schema_id': 'str',
            'secret_data': 'dict',      # Required
            'domain_id': 'str'          # Required
        }

    Returns:
        AccountsResponse:
        {
            'results': [
                {
                    name: 'str',
                    data: 'dict',
                    secret_schema_id: 'str',
                    secret_data: 'dict',
                    tags: 'dict',
                    location: [
                        {
                            'name': 'str',
                            'resource_id': 'str'
                        }
                    ]
                }
            ]
        }
    """
    pass
