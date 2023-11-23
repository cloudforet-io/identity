import logging
from typing import Union
from spaceone.core.service import BaseService, transaction, convert_model, append_query_filter, append_keyword_filter
from spaceone.identity.model.policy.request import *
from spaceone.identity.model.policy.response import *
from spaceone.identity.manager.policy_manager import PolicyManager

_LOGGER = logging.getLogger(__name__)


class PolicyService(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.policy_mgr = PolicyManager()

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

        policy_vo = self.policy_mgr.create_policy(params.dict())
        return PolicyResponse(**policy_vo.to_dict())

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

        policy_vo = self.policy_mgr.get_policy(params.policy_id, params.domain_id)

        policy_vo = self.policy_mgr.update_policy_by_vo(
            params.dict(exclude_unset=True), policy_vo
        )

        return PolicyResponse(**policy_vo.to_dict())

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

        policy_vo = self.policy_mgr.get_policy(params.policy_id, params.domain_id)
        self.policy_mgr.delete_policy_by_vo(policy_vo)

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

        policy_vo = self.policy_mgr.get_policy(params.policy_id, params.domain_id)
        return PolicyResponse(**policy_vo.to_dict())

    @transaction(append_meta={'authorization.scope': 'DOMAIN_READ'})
    @append_query_filter(['policy_id', 'name', 'domain_id'])
    @append_keyword_filter(['policy_id', 'name'])
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

        query = params.query or {}
        policy_vos, total_count = self.policy_mgr.list_policies(query)

        policies_info = [policy_vo.to_dict() for policy_vo in policy_vos]
        return PoliciesResponse(results=policies_info, total_count=total_count)

    @transaction(append_meta={'authorization.scope': 'DOMAIN_READ'})
    @append_query_filter(['domain_id'])
    @append_keyword_filter(['policy_id', 'name'])
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

        query = params.query or {}
        return self.policy_mgr.stat_policies(query)
