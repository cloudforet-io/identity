from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel
from spaceone.identity.model.role_model import Role


class UserTag(EmbeddedDocument):
    key = StringField(max_length=255)
    value = StringField(max_length=255)


class User(MongoModel):
    user_id = StringField(max_length=40, unique_with='domain_id', required=True)
    password = BinaryField(default=None)
    name = StringField(max_length=128)
    state = StringField(max_length=20, choices=('ENABLED', 'DISABLED', 'PENDING'))
    email = StringField(max_length=255, default=None, null=True)
    user_type = StringField(max_length=20, choices=('USER', 'API_USER'))
    backend = StringField(max_length=20, choices=('LOCAL', 'EXTERNAL'))
    language = StringField(max_length=7, default='en')
    timezone = StringField(max_length=50, default='UTC')
    roles = ListField(ReferenceField('Role', reverse_delete_rule=DENY))
    tags = ListField(EmbeddedDocumentField(UserTag))
    domain_id = StringField(max_length=40)
    last_accessed_at = DateTimeField(auto_now_add=True)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        'updatable_fields': [
            'password',
            'name',
            'state',
            'email',
            'language',
            'timezone',
            'roles',
            'tags'
        ],
        'exact_fields': [
            'user_id',
            'user_type',
            'backend',
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
            'state',
            'user_type',
            'backend',
            'roles',
            ('user_id', 'domain_id'),
            ('tags.key', 'tags.value')
        ]
    }
