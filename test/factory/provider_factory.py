import factory

from spaceone.core import utils
from spaceone.identity.model.provider_model import Provider


class ProviderFactory(factory.mongoengine.MongoEngineFactory):

    class Meta:
        model = Provider

    provider = factory.LazyAttribute(lambda o: utils.random_string())
    name = factory.LazyAttribute(lambda o: utils.random_string())
    template = {
        'service_account': {
            'schema': {
                'type': 'object',
                'properties': {
                    'account_id': {
                        'title': 'Account ID',
                        'type': 'string'
                    }
                },
                'required': ['account_id']
            }
        }
    }
    metadata = {
        'view': {
            'layouts': {
                'help:service_account:create': {
                    'name': 'Creation Help',
                    'type': 'markdown',
                    'options': {
                        'markdown': {
                            'en': (
                                '### Finding Your AWS Account ID\n'
                                'You can find your account ID in the AWS Management Console, or using the AWS CLI or AWS API.\n'
                                '#### Finding your account ID (Console)\n'
                                'In the navigation bar, choose **Support**, and then **Support Center**. '
                                'Your currently signed-in 12-digit account number (ID) appears in the **Support Center** title bar.\n'
                                '#### Finding your account ID (AWS CLI)\n'
                                'To view your user ID, account ID, and your user ARN:\n'
                                '- [aws sts get-caller-identity](https://docs.aws.amazon.com/IAM/latest/UserGuide/console_account-alias.html)\n'
                                '#### Finding your account ID (AWS API)\n'
                                'To view your user ID, account ID, and your user ARN:\n'
                                '- [GetCallerIdentity](https://docs.aws.amazon.com/STS/latest/APIReference/API_GetCallerIdentity.html)\n'
                                '#### References\n'
                                '- [AWS Guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/console_account-alias.html)\n'
                            )
                        }
                    }
                }
            }
        }
    }
    capability = {
        'supported_schema': ['schema-aaa', 'schema-bbb']
    }
    tags = [
        {
            'key': 'tag_key',
            'value': 'tag_value'
        }
    ]
    created_at = factory.Faker('date_time')
