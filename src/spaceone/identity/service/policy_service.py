import logging
from typing import Union
from spaceone.core.service import BaseService, transaction, convert_model
from spaceone.identity.model.policy.request import *
from spaceone.identity.model.policy.response import *

_LOGGER = logging.getLogger(__name__)


class PolicyService(BaseService):
    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @convert_model
    def create(self, params: PolicyCreateRequest) -> Union[PolicyResponse, dict]:
        """ create policy

         Args:
            params (PolicyCreateRequest): {
                'name': 'str',                      # required
                'permissions': 'list',              # required
                'tags': 'dict',
                'domain_id': 'str'                  # required
            }

        Returns:
            PolicyResponse:
        """
        return {}

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @convert_model
    def update(self, params: PolicyUpdateRequest) -> Union[PolicyResponse, dict]:
        """ update policy

         Args:
            params (PolicyUpdateRequest): {
                'policy_id': 'str',         # required
                'name': 'str',
                'permissions': 'list',
                'tags': 'dict',
                'domain_id': 'str',         # required
            }

        Returns:
            PolicyResponse:
        """

        return {}

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @convert_model
    def delete(self, params: PolicyDeleteRequest) -> None:
        """ delete policy

         Args:
            params (PolicyDeleteRequest): {
                'policy_id': 'str',             # required
                'domain_id': 'str',             # required
            }

        Returns:
            None
        """
        pass

    @transaction(append_meta={'authorization.scope': 'DOMAIN_READ'})
    @convert_model
    def get(self, params: PolicyGetRequest) -> Union[PolicyResponse, dict]:
        """ get policy

         Args:
            params (PolicyGetRequest): {
                'policy_id': 'str',             # required
                'domain_id': 'str',             # required
            }

        Returns:
             PolicyResponse:
        """
        return {}

    @transaction(append_meta={'authorization.scope': 'DOMAIN_READ'})
    @convert_model
    def list(self, params: PolicySearchQueryRequest) -> Union[PoliciesResponse, dict]:
        """ list policies

        Args:
            params (PolicySearchQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.Query)',
                'policy_id': 'str',
                'name': 'str',
                'domain_id': 'str',                     # required
            }

        Returns:
            PoliciesResponse:
        """
        return {}

    @transaction(append_meta={'authorization.scope': 'DOMAIN_READ'})
    @convert_model
    def stat(self, params: PolicyStatQueryRequest) -> dict:
        """ stat policies

        Args:
            params (PolicyStatQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)', # required
                'domain_id': 'str',         # required
            }

        Returns:
            dict: {
                'results': 'list',
                'total_count': 'int'
            }
        """
        return {}
