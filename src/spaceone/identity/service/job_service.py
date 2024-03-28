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
from spaceone.identity.manager.project_manager import ProjectManager
from spaceone.identity.manager.project_group_manager import ProjectGroupManager
from spaceone.identity.manager.provider_manager import ProviderManager
from spaceone.identity.manager.schema_manager import SchemaManager
from spaceone.identity.manager.service_account_manager import ServiceAccountManager
from spaceone.identity.manager.secret_manager import SecretManager
from spaceone.identity.manager.trusted_account_manager import TrustedAccountManager
from spaceone.identity.manager.workspace_manager import WorkspaceManager
from spaceone.identity.model.project.database import Project
from spaceone.identity.model.project_group.database import ProjectGroup
from spaceone.identity.model.provider.database import Provider
from spaceone.identity.model.service_account.database import ServiceAccount
from spaceone.identity.model.trusted_account.database import TrustedAccount
from spaceone.identity.model.job.database import Job
from spaceone.identity.model.job.request import *
from spaceone.identity.model.job.response import *
from spaceone.identity.model.workspace.database import Workspace
from spaceone.identity.service.service_account_service import ServiceAccountService

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
        self.account_collector_plugin_mgr = AccountCollectorPluginManager()
        self.workspace_mgr = WorkspaceManager()
        self.service_account_mgr = ServiceAccountManager()
        self.project_mgr = ProjectManager()
        self.project_group_mgr = ProjectGroupManager()

    @transaction(exclude=["authentication", "authorization", "mutation"])
    def create_jobs_by_trusted_account(self, params):
        """Create jobs by trusted account
        Args:
            params (dict): {
                'params':
            }
        Returns:
            None:
        """

        current_hour = params.get("current_hour", datetime.utcnow().hour)

        # todo check provider sync condition
        for trusted_account_vo in self._get_all_schedule_enabled_trusted_accounts(
                current_hour
        ):
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
            params.domain_id,
            params.job_id,
            params.workspace_id,
        )

        self.job_mgr.delete_job_by_vo(job_vo)

    @transaction(
        permission="identity:Job.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER"],
    )
    @convert_model
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

        job_vo = self.job_mgr.get_job(domain_id, job_id, workspace_id)

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
    def sync_service_accounts(self, params: dict) -> None:
        """Sync account data
        Args:
            params (dict): {
                    'job_id': 'str',
                    'trusted_account_id': 'str',
                    'trusted_secret_id': 'str',
                    'secret_data': 'dict',
                    'workspace_id': 'str',
                    'domain_id': 'str'
            }
        Returns:
            None:
        """

        trusted_secret_id = params["trusted_secret_id"]
        secret_data = params["secret_data"]
        trusted_account_id = params["trusted_account_id"]
        job_id = params["job_id"]
        workspace_id = params.get("workspace_id")
        domain_id = params["domain_id"]

        schema_mgr = SchemaManager()

        trusted_account_vo: TrustedAccount = (
            self.trusted_account_mgr.get_trusted_account(
                trusted_account_id, domain_id, workspace_id
            )
        )
        job_vo: Job = self.job_mgr.get_job(domain_id, job_id, workspace_id)
        schema_vo = schema_mgr.get_schema(trusted_account_vo.secret_schema_id, domain_id)
        provider_vo: Provider = self.provider_mgr.get_provider(trusted_account_vo.provider, domain_id)
        plugin_info = provider_vo.plugin_info.to_dict()

        provider = provider_vo.provider
        sync_options = trusted_account_vo.sync_options or {}
        related_schemas = schema_vo.related_schemas or []

        if self._is_job_failed(job_id, domain_id, job_vo.workspace_id):
            self.job_mgr.change_canceled_status(job_vo)
        else:
            self.job_mgr.change_in_progress_status(job_vo)
            synced_projects = []
            synced_service_accounts = []

            try:
                options = plugin_info.get("options", {})
                schema_id = plugin_info.get("schema_id")

                (
                    endpoint,
                    updated_version,
                ) = self.account_collector_plugin_mgr.get_account_collector_plugin_endpoint(
                    plugin_info, domain_id
                )

                self.account_collector_plugin_mgr.initialize(endpoint)
                start_dt = datetime.utcnow()

                is_canceled = False

                response = self.account_collector_plugin_mgr.sync(
                    endpoint, options, secret_data, domain_id, schema_id
                )

                for result in response.get("results", []):
                    location = self._get_location(result, trusted_account_vo.resource_group, sync_options)

                    if trusted_account_vo.resource_group == "DOMAIN":
                        if not sync_options.get("single_workspace_id"):
                            workspace_vo = self._create_workspace(domain_id, location.pop(0))
                        else:
                            workspace_vo = self.workspace_mgr.get_workspace(domain_id,
                                                                            sync_options.get("single_workspace_id"))
                        sync_workspace_id = workspace_vo.workspace_id

                    else:
                        sync_workspace_id = workspace_id

                    parent_group_id = None
                    for loc in location:
                        project_group_vo = self._create_project_group(domain_id, sync_workspace_id, loc,
                                                                      parent_group_id)
                        parent_group_id = project_group_vo.project_group_id

                    project_vo = self._create_project(domain_id, sync_workspace_id, result["name"], parent_group_id,
                                                      sync_options)
                    synced_projects.append(project_vo)
                    service_account_vo = self._create_service_account(result, project_vo, trusted_account_id,
                                                                      trusted_secret_id,
                                                                      provider, result["name"], related_schemas,
                                                                      sync_options)
                    synced_service_accounts.append(service_account_vo)

                if self._is_job_failed(job_id, domain_id, job_vo.workspace_id):
                    self.job_mgr.change_canceled_status(job_vo)
                    is_canceled = True

                if not is_canceled:
                    end_dt = datetime.utcnow()
                    _LOGGER.debug(
                        f"[sync_service_accounts] end job ({job_vo.job_id}): {end_dt}"
                    )
                    _LOGGER.debug(
                        f"[sync_service_accounts] total job time ({job_vo.job_id}): {end_dt - start_dt}"
                    )
                    self.job_mgr.change_success_status(job_vo)

            except Exception as e:
                # self._delete_synced_resources(synced_projects, synced_service_accounts)
                self.job_mgr.change_error_status(job_vo, e)
                _LOGGER.error(f"[sync_service_accounts] sync error: {e}", exc_info=True)

        self._close_job(
            job_id,
            domain_id,
            job_vo.workspace_id,
        )

    def created_service_account_job(
            self, trusted_account_vo: TrustedAccount, job_options: dict
    ) -> Union[Job, dict]:
        resource_group = trusted_account_vo.resource_group
        provider = trusted_account_vo.provider
        trusted_account_id = trusted_account_vo.trusted_account_id
        workspace_id = trusted_account_vo.workspace_id
        domain_id = trusted_account_vo.domain_id

        provider_vo = self.provider_mgr.get_provider(provider, domain_id)
        plugin_id = provider_vo.plugin_info["plugin_id"]
        ac_plugin_mgr = AccountCollectorPluginManager()
        endpoint = ac_plugin_mgr.get_account_collector_plugin_endpoint_by_vo(
            provider_vo
        )

        options = provider_vo.plugin_info.get("options")
        schema_id = trusted_account_vo.secret_schema_id

        ac_plugin_mgr.initialize(endpoint)

        try:
            trusted_secret_data = self._get_trusted_secret_data(
                trusted_account_vo.trusted_secret_id, domain_id
            )

            if trusted_secret_data:
                schema_mgr = SchemaManager()
                # Check secret_data by schema
                schema_mgr.validate_secret_data_by_schema_id(
                    schema_id, domain_id, trusted_secret_data, "TRUSTED_ACCOUNT"
                )
        except Exception as e:
            trusted_secret_data = {}
            _LOGGER.error(
                f"[created_trusted_account_job] get trusted secret error: {e}",
                exc_info=True,
            )

        # Add Job Options
        job_vo = self.job_mgr.create_job(
            resource_group,
            domain_id,
            workspace_id,
            trusted_account_id,
            plugin_id,
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
                    "secret_data": trusted_secret_data,
                    "workspace_id": trusted_account_vo.workspace_id,
                    "domain_id": domain_id,
                }
            )
            try:
                pass
            except Exception as e:
                self.job_mgr.change_error_status(job_vo, e)

        return job_vo

    def _get_all_schedule_enabled_trusted_accounts(self, current_hour: int) -> list:
        query = {
            "filter": [
                {"k": "schedule.state", "v": "ENABLED", "o": "eq"},
                {"k": "schedule.hours", "v": [current_hour], "o": "in"},
            ]
        }
        (
            trusted_account_vos,
            total_count,
        ) = self.trusted_account_mgr.list_trusted_accounts(query)
        _LOGGER.debug(
            f"[_get_all_schedule_enabled_trusted_accounts] scheduled trusted accounts count (UTC {current_hour}: {total_count}"
        )
        return trusted_account_vos

    def _get_trusted_secret_data(self, trusted_secret_id: str, domain_id: str) -> dict:
        # todo: this method is internal method
        secret_mgr: SecretManager = self.locator.get_manager("SecretManager")
        if trusted_secret_id:
            secret_data = secret_mgr.get_trusted_secret_data(
                trusted_secret_id, domain_id
            )
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

        job_vos, total_count = self.job_mgr.list_jobs(query)

        if total_count == 0:
            return True
        else:
            for job_vo in job_vos:
                self.job_mgr.make_canceled_by_vo(job_vo)
        return False

    def _is_job_failed(
            self, job_id: str, domain_id: str, workspace_id: str = None
    ) -> bool:
        job_vo: Job = self.job_mgr.get_job(domain_id, job_id, workspace_id)

        if job_vo.status in ["CANCELED", "FAILURE"]:
            return True
        else:
            return False

    def _close_job(
            self,
            job_id: str,
            domain_id: str,
            workspace_id: str = None,
    ):
        job_vo: Job = self.job_mgr.get_job(domain_id, job_id, workspace_id)
        if job_vo.status == "IN_PROGRESS":
            self.job_mgr.change_success_status(job_vo)
        elif job_vo.status == "FAILURE":
            self.job_mgr.update_job_by_vo({"finished_at": datetime.utcnow()}, job_vo)

    def _create_workspace(self, domain_id: str, name: str) -> Workspace:
        workspace_vos = self.workspace_mgr.filter_workspaces(domain_id=domain_id, name=name)
        if workspace_vos:
            workspace_vo = workspace_vos[0]
        else:
            workspace_vo = self.workspace_mgr.create_workspace(
                {
                    "domain_id": domain_id,
                    "name": name,
                }
            )
        return workspace_vo

    def _create_project_group(self, domain_id: str, workspace_id: str, name: str,
                              parent_group_id: str = None) -> ProjectGroup:
        query_filter = {
            "filter": [{"k": "domain_id", "v": domain_id, "o": "eq"},
                       {"k": "workspace_id", "v": workspace_id, "o": "eq"}, {"k": "name", "v": name, "o": "eq"}]
        }
        if parent_group_id:
            query_filter["filter"].append({"k": "parent_group_id", "v": parent_group_id, "o": "eq"})

        project_group_vos, _ = self.project_group_mgr.list_project_groups(query_filter)

        if project_group_vos:
            project_group_vo = project_group_vos[0]
        else:
            params = {
                "name": name,
                "domain_id": domain_id,
                "workspace_id": workspace_id,
            }
            if parent_group_id:
                params["parent_group_id"] = parent_group_id
            project_group_vo = self.project_group_mgr.create_project_group(params)

        return project_group_vo

    def _create_project(
            self,
            domain_id: str,
            workspace_id: str,
            name: str,
            parent_group_id: str = None,
            sync_options: dict = None,
            project_type: str = "PRIVATE",
    ) -> Project:
        params = {
            "name": name,
            "domain_id": domain_id,
            "workspace_id": workspace_id,
            "project_type": project_type,
        }

        if parent_group_id:
            params["parent_group_id"] = parent_group_id

        project_vos = self.project_mgr.filter_projects(**params)

        if project_vos:
            project_vo = project_vos[0]
            self.project_mgr.update_project_by_vo(params, project_vo)
        else:
            project_vo = self.project_mgr.create_project(params)
        return project_vo

    def _create_service_account(
            self,
            result: dict,
            project_vo: Project,
            trusted_account_id: str,
            trusted_secret_id: str,
            provider: str,
            name: str,
            related_schemas: list = None,
            sync_options: dict = None,
    ) -> ServiceAccount:
        secret_data = result.get("secret_data", {})
        data = result.get("data", {})
        secret_schema_id = result.get("secret_schema_id")
        tags = result.get("tags", {})

        if secret_data and secret_schema_id is None:
            raise ERROR_INVALID_PARAMETER(key="secret_schema_id")

        if secret_schema_id not in related_schemas:
            raise ERROR_INVALID_PARAMETER(key="secret_schema_id", reason=f"schema_id is not in {related_schemas}")

        service_account_vos = self.service_account_mgr.filter_service_accounts(
            domain_id=project_vo.domain_id, workspace_id=project_vo.workspace_id, project_id=project_vo.project_id,
            data=data
        )

        if service_account_vos:
            service_account_vo = service_account_vos[0]
            if service_account_vo.name != result["name"]:
                service_account_vo = self.service_account_mgr.update_service_account_by_vo(
                    {"name": name}, service_account_vo
                )
        else:
            params = {
                "name": name,
                "provider": provider,
                "data": data,
                "trusted_account_id": trusted_account_id,
                "project_id": project_vo.project_id,
                "workspace_id": project_vo.workspace_id,
                "domain_id": project_vo.domain_id,
                "tags": tags,
            }
            if secret_schema_id:
                params["schema_id"] = secret_schema_id

            service_account_vo = self.service_account_mgr.create_service_account(params)

        if secret_data:
            # Check secret_data by schema
            schema_mgr = SchemaManager()
            schema_mgr.validate_secret_data_by_schema_id(
                secret_schema_id,
                service_account_vo.domain_id,
                secret_data,
                "TRUSTING_SECRET",
            )

            secret_mgr = SecretManager()
            create_secret_params = {
                "name": f"{service_account_vo.service_account_id}-secret",
                "data": secret_data,
                "schema_id": secret_schema_id,
                "trusted_secret_id": trusted_secret_id,
                "resource_group": "PROJECT",
            }
            secret_info = secret_mgr.create_secret(create_secret_params)
            # Update secret_id in service_account_vo
            service_account_vo = self.service_account_mgr.update_service_account_by_vo(
                {"secret_id": secret_info["secret_id"]}, service_account_vo
            )
        return service_account_vo

    # todo: change
    def _delete_synced_resources(
            self, synced_projects: list, synced_service_accounts: list, synced_projects_groups: list = None
    ) -> None:
        for service_account_vo in synced_projects:
            self.service_account_mgr.delete_service_account_by_vo(service_account_vo)

        for project_vo in synced_service_accounts:
            self.project_mgr.delete_project_by_vo(project_vo)

    @staticmethod
    def _get_location(result: dict, resource_group: str, sync_options: dict) -> list:
        location = []
        if not sync_options.get("skip_project_group", False):
            location = result.get("location", [])
            if resource_group == "DOMAIN" and not location:
                raise ERROR_REQUIRED_PARAMETER(key="location", reason="location is required")

        return location
