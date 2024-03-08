import logging
from datetime import datetime
from typing import Union

from spaceone.core.service import *
from spaceone.core.service.utils import *

from spaceone.identity.error.error_job import *
from spaceone.identity.manager.account_collector_plugin_manager import (
    AccountCollectorPluginManager,
)
from spaceone.identity.manager.job_manager import JobManager
from spaceone.identity.manager.provider_manager import ProviderManager
from spaceone.identity.manager.secret_manager import SecretManager
from spaceone.identity.manager.schema_manager import SchemaManager
from spaceone.identity.manager.trusted_account_manager import TrustedAccountManager
from spaceone.identity.model.trusted_account.database import TrustedAccount
from spaceone.identity.model.job.database import Job
from spaceone.identity.model.job.request import *
from spaceone.identity.model.job.response import *

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class JobService(BaseService):
    resource = "Job"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.job_mgr = JobManager()
        self.trusted_account_mgr = TrustedAccountManager()
        self.provider_mgr = ProviderManager()

    @transaction(exclude=["authentication", "authorization", "mutation"])
    def create_jobs_by_trusted_account(self, params):
        """Create jobs by trusted account
        Args:
            params (dict): {
                'params': dict
            }
        Returns:
            None:
        """

        for trusted_account_vo in self._get_all_schedule_enabled_trusted_accounts():
            try:
                self.created_service_account_job(trusted_account_vo, {})
            except Exception as e:
                _LOGGER.error(
                    f"[create_jobs_by_trusted_account] sync error: {e}", exc_info=True
                )

    @transaction(
        permission="identity:Job.write", role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER"]
    )
    @convert_model
    def delete(self, params: JobDeleteRequest) -> None:
        """Delete job
        Args:
            params (JobDeleteRequest): {
                'job_id': 'str',            # required
                'workspace_id': 'str',      # injected from auth (required)
                'domain_id': 'str'          # injected from auth (required)
            }
        Returns:
            None:
        """

        job_vo = self.job_mgr.get_job(
            params.job_id,
            params.domain_id,
            params.workspace_id,
        )

        self.job_mgr.delete_job_by_vo(job_vo)

    @transaction(
        permission="identity:Job.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER"],
    )
    def get(self, params: JobGetRequest) -> JobResponse:
        """Get job
        Args:
            params (JobGetRequest): {
                'job_id': 'str',            # required
                'workspace_id': 'str',      # injected from auth (required)
                'domain_id': 'str'          # injected from auth (required)
            }
        Returns:
            JobInfo:
        """

        job_id = params.job_id
        workspace_id = params.workspace_id
        domain_id = params.domain_id

        job_vo = self.job_mgr.get_job(job_id, domain_id, workspace_id)

        return JobResponse(**job_vo.to_dict())

    @transaction(
        permission="identity:Job.read", role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER"]
    )
    @append_query_filter(
        [
            "job_id",
            "status",
            "trusted_account_id",
            "plugin_id",
            "workspace_id",
            "domain_id",
        ]
    )
    @append_keyword_filter(["job_id", "status"])
    @convert_model
    def list(self, params: JobSearchQueryRequest) -> Union[JobsResponse, dict]:
        """List jobs
        Args:
            params (JobSearchQueryRequest): {
                'query': 'dict',
                'job_id': 'str',
                'status': 'str',
                'trusted_account_id': 'str',
                'plugin_id': 'str',
                'workspace_id': 'str',
                'domain_id': 'str'          # injected from auth (required)
            }
        Returns:
            JobsResponse:
        """

        query = params.query or {}

        job_vos, total_count = self.job_mgr.list_jobs(query)

        jobs_info = [job_vo.to_dict() for job_vo in job_vos]

        return JobsResponse(results=jobs_info, total_count=total_count)

    @transaction(
        permission="identity:Job.read", role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER"]
    )
    @append_query_filter(["workspace_id", "domain_id"])
    @append_keyword_filter(["job_id"])
    @convert_model
    def stat(self, params: JobStatQueryRequest) -> dict:
        """Stat jobs
        Args:
            params (JobStatQueryRequest): {
                'domain_id': 'str' # injected from auth (required)
            }
        Returns:
            dict:
        """

        query = params.query or {}

        return self.job_mgr.stat_jobs(query)

    @transaction(exclude=["authentication", "authorization", "mutation"])
    @check_required(["task_options", "job_task_id", "domain_id"])
    def sync_service_accounts(self, params: dict):
        """Sync account data
        Args:
            params (dict): {
                'job_task_id': 'str',
                'task_options': 'dict',
                'domain_id': 'str'
            }
        Returns:
            None:
        """

        trusted_secret_id = params["trusted_secret_id"]
        secret_data = params["secret_data"]
        trusted_account_id = params["trusted_account_id"]
        job_id = params["job_id"]
        domain_id = params["domain_id"]

        job_vo = self.job_mgr.get_job(job_id, domain_id)

        self._close_job(
            job_id,
            trusted_account_id,
            domain_id,
            job_vo.workspace_id,
        )

    def created_service_account_job(
        self, trusted_account_vo: TrustedAccount, job_options: dict
    ) -> Union[Job, dict]:
        resource_group = trusted_account_vo.resource_group
        provider = trusted_account_vo.provider
        sync_options = trusted_account_vo.sync_options
        trusted_account_id = trusted_account_vo.trusted_account_id
        workspace_id = trusted_account_vo.workspace_id
        domain_id = trusted_account_vo.domain_id

        provider_vo = self.provider_mgr.get_provider(provider, domain_id)
        ac_plugin_mgr = AccountCollectorPluginManager()
        endpoint = ac_plugin_mgr.get_account_collector_plugin_endpoint_by_vo(
            provider_vo
        )

        options = provider_vo.plugin_info.options
        schema_id = trusted_account_vo.secret_schema_id

        ac_plugin_mgr.initialize(endpoint)

        try:
            secret_data = self._get_secret_data(
                trusted_account_vo.trusted_secret_id, domain_id
            )
            schema_mgr = SchemaManager()
            # Check secret_data by schema
            schema_mgr.validate_secret_data_by_schema_id(
                schema_id, domain_id, secret_data, "SECRET"
            )
        except Exception as e:
            secret_data = {}
            _LOGGER.error(
                f"[created_trusted_account_job] get secret error: {e}", exc_info=True
            )

        # Add Job Options
        job_vo = self.job_mgr.create_job(
            resource_group, trusted_account_id, workspace_id, domain_id
        )

        if self._check_duplicate_job(domain_id, trusted_account_id, job_vo):
            self.job_mgr.change_error_status(
                job_vo, ERROR_DUPLICATE_JOB(trusted_account_id=trusted_account_id)
            )
        else:
            self.job_mgr.push_job(
                {
                    "job_id": job_vo.job_id,
                    "trusted_account_id": trusted_account_id,
                    "trusted_secret_id": trusted_account_vo.trusted_secret_id,
                    "secret_data": secret_data,
                    "workspace_id": trusted_account_vo.workspace_id,
                    "domain_id": domain_id,
                }
            )
            try:
                pass
            except Exception as e:
                self.job_mgr.change_error_status(job_vo, e)

        return job_vo

    def _get_all_schedule_enabled_trusted_accounts(self):
        return self.trusted_account_mgr.filter_trusted_accounts(
            state="ENABLED", data_source_type="EXTERNAL"
        )

    def _get_secret_data(self, secret_id: str, domain_id: str) -> dict:
        # todo: this method is internal method
        secret_mgr: SecretManager = self.locator.get_manager("SecretManager")
        if secret_id:
            secret_data = secret_mgr.get_secret_data(secret_id, domain_id)
        else:
            secret_data = {}

        return secret_data

    def _check_duplicate_job(
        self,
        domain_id: str,
        trusted_account_id: str,
        his_job_vo: Job,
    ) -> bool:
        query = {
            "filter": [
                {"k": "trusted_account_id", "v": trusted_account_id, "o": "eq"},
                {"k": "workspace_id", "v": his_job_vo.workspace_id, "o": "eq"},
                {"k": "domain_id", "v": domain_id, "o": "eq"},
                {"k": "status", "v": ["PENDING", "IN_PROGRESS"], "o": "in"},
                {"k": "job_id", "v": his_job_vo.job_id, "o": "not"},
            ]
        }

        job_vos, total_count = self.job_mgr.list_jobs(**query)

        if total_count == 0:
            return True
        else:
            for job_vo in job_vos:
                self.job_mgr.make_canceled_by_vo(job_vo)
        return False

    def _close_job(
        self,
        job_id: str,
        trusted_account_id: str,
        domain_id: str,
        workspace_id: str = None,
    ):
        job_vo: Job = self.job_mgr.get_job(job_id, domain_id, workspace_id)
        if job_vo.status == "IN_PROGRESS":
            self.job_mgr.change_success_status(job_vo)
        elif job_vo.status == "FAILURE":
            self.job_mgr.update_job_by_vo({"finished_at": datetime.utcnow()}, job_vo)
