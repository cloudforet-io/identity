from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class APIKey(MongoModel):
    api_key_id = StringField(max_length=40, generate_id='api-key', unique=True)
    api_key = StringField()
    state = StringField(max_length=20,
                        default='ENABLED',
                        choices=('ENABLED', 'DISABLED'))
    api_key_type = StringField(max_length=20,
                               choices=('USER', 'SYSTEM', 'DELEGATION', 'DOMAIN'))
    user_id = StringField(max_length=40)
    domain_id = StringField(max_length=40, required=True)
    last_accessed_at = DateTimeField(auto_now_add=True)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        'updatable_fields': [
            'roles',
            'allowed_hosts',
            'state'
        ],
        'exact_fields': [
            'api_key_id',
            'api_key,'
            'user_id',
            'domain_id',
            'state',
            'api_key_type'
        ],
        'minimal_fields': [
            'api_key_id',
            'state',
            'api_key_type'
        ],
        'ordering': ['api_key_id'],
        'indexes': [
            'api_key_id',
            'user_id',
            'domain_id'
        ]
    }

    @classmethod
    def create(cls, data):
        return super().create(data)
