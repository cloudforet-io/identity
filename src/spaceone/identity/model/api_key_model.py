from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel
from spaceone.identity.model.user_model import User


class APIKey(MongoModel):
    api_key_id = StringField(max_length=40, generate_id='api-key', unique=True)
    state = StringField(max_length=20, default='ENABLED', choices=('ENABLED', 'DISABLED'))
    user_id = StringField(max_length=40, required=True)
    user = ReferenceField('User', null=True, default=None, reverse_delete_rule=CASCADE)
    domain_id = StringField(max_length=40, required=True)
    last_accessed_at = DateTimeField(default=None, null=True)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        'updatable_fields': [
            'state',
            'last_accessed_at'
        ],
        'minimal_fields': [
            'api_key_id',
            'state',
            'user_id'
        ],
        'ordering': ['api_key_id'],
        'indexes': [
            'state',
            'user_id',
            'domain_id',
            'last_accessed_at'
        ]
    }
