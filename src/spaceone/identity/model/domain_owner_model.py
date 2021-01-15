from mongoengine import *

from spaceone.core.error import *
from spaceone.core.model.mongo_model import MongoModel


class DomainOwner(MongoModel):
    owner_id = StringField(max_length=40, unique_with='domain_id', required=True)
    password = BinaryField()
    name = StringField(max_length=128)
    email = StringField(max_length=255, default=None, null=True)
    language = StringField(max_length=7, default='en')
    timezone = StringField(max_length=50, default='UTC')
    domain_id = StringField(max_length=40)
    last_accessed_at = DateTimeField(default=None, null=True)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        'updatable_fields': [
            'password',
            'name',
            'email',
            'language',
            'timezone',
            'last_accessed_at'
        ],
        'minimal_fields': [
            'owner_id',
            'name'
        ],
        'ordering': ['name'],
        'indexes': [
            'owner_id',
            'email',
            'domain_id',
            'last_accessed_at'
        ]
    }

    @classmethod
    def create(cls, data):
        user_vos = cls.filter(domain_id=data['domain_id'])
        if user_vos.count() > 0:
            raise ERROR_NOT_UNIQUE(key='owner_id', value=data['owner_id'])
        return super().create(data)

    def update(self, data):
        return super().update(data)
