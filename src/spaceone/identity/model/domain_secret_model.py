from mongoengine import *

from spaceone.core.model.mongo_model import MongoModel
from spaceone.identity.model.domain_model import Domain


class DomainSecret(MongoModel):
    domain_key = StringField()
    pub_jwk = DictField(required=True)
    prv_jwk = DictField(required=True)
    refresh_pub_jwk = DictField(required=True)
    refresh_prv_jwk = DictField(required=True)
    domain_id = StringField(max_length=40, unique=True)
    domain = ReferenceField('Domain', reverse_delete_rule=CASCADE)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        'updatable_fields': [
            'refresh_pub_jwk',
            'refresh_prv_jwk',
            'domain'
        ],
        'ordering': ['domain_id'],
        'indexes': [
            'domain_id',
            'domain'
        ]
    }
