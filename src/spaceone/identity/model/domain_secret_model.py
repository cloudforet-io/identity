from mongoengine import *

from spaceone.core.model.mongo_model import MongoModel


class DomainSecret(MongoModel):
    domain_id = StringField(max_length=40, unique=True)
    created_at = DateTimeField(auto_now_add=True)
    pub_jwk = DictField(required=True)
    prv_jwk = DictField(required=True)
    domain_key = StringField()

    meta = {
        'updatable_fields': [
        ],
        'exact_fields': [
            'domain_id',
            'pub_jwk',
            'prv_jwk'
        ],
        'ordering': ['domain_id'],
        'indexes': [
            'domain_id'
        ]
    }

    @classmethod
    def create(cls, data):
        return super().create(data)
