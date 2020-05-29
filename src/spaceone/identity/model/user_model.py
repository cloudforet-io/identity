from mongoengine import *

from spaceone.core.error import *
from spaceone.core.model.mongo_model import MongoModel
from spaceone.identity.model.role_model import Role


class User(MongoModel):
    user_id = StringField(max_length=40, unique_with='domain_id', required=True)
    password = BinaryField()
    name = StringField(max_length=128)
    state = StringField(max_length=20, choices=('ENABLED', 'DISABLED', 'UNIDENTIFIED'))
    email = StringField(max_length=255, default=None, null=True)
    mobile = StringField(max_length=24, default=None, null=True)
    group = StringField(max_length=255, default=None, null=True)
    language = StringField(max_length=7, default='en')
    timezone = StringField(max_length=50, default='Etc/GMT')
    roles = ListField(ReferenceField('Role', reverse_delete_rule=DENY))
    tags = DictField()
    domain_id = StringField(max_length=40)
    last_accessed_at = DateTimeField(auto_now_add=True)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        'updatable_fields': [
            'password',
            'name',
            'state',
            'email',
            'mobile',
            'group',
            'language',
            'timezone',
            'roles',
            'tags'
        ],
        'exact_fields': [
            'user_id',
            'domain_id'
        ],
        'minimal_fields': [
            'user_id',
            'name',
            'state'
        ],
        'change_query_keys': {
            'role_id': 'roles.role_id'
        },
        'reference_query_keys': {
            'roles': Role
        },
        'ordering': ['name'],
        'indexes': [
            'user_id',
            'domain_id'
        ]
    }
