import logging
from datetime import datetime
from typing import Tuple, Union

from mongoengine import QuerySet
from spaceone.core import queue, utils
from spaceone.core.error import *
from spaceone.core.manager import BaseManager

from spaceone.identity.model.job.database import Job

_LOGGER = logging.getLogger(__name__)


class JobManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.job_model = Job

    def create_job(
        self,
        resource_group: str,
        domain_id: str,
        workspace_id: str,
        trusted_account_id: str,
        plugin_id: str,
        options: dict,
    ) -> Job:
        data = {
            "resource_group": resource_group,
            "plugin_id": plugin_id,
            "trusted_account_id": trusted_account_id,
            "domain_id": domain_id,
            "workspace_id": workspace_id,
            "options": options,
        }
        job_vo = self.job_model.create(data)

        _LOGGER.debug(f"[create_job] create job: {job_vo.job_id}")
        return job_vo

    @staticmethod
    def delete_job_by_vo(job_vo: Job) -> None:
        _LOGGER.debug(f"[delete_job_by_vo] delete job: {job_vo.job_id}")
        job_vo.delete()

    def get_job(self, domain_id: str, job_id: str, workspace_id: str = None) -> Job:
        conditions = {"job_id": job_id, "domain_id": domain_id}

        if workspace_id:
            conditions["workspace_id"] = workspace_id

        return self.job_model.get(**conditions)

    def update_job_by_vo(self, params: dict, job_vo: Job) -> Job:
        def _rollback(old_data):
            _LOGGER.info(
                f'[update_project._rollback] Revert Data: {old_data["name"]} ({old_data["job_id"]})'
            )
            job_vo.update(old_data)

        self.transaction.add_rollback(_rollback, job_vo.to_dict())

        return job_vo.update(params)

    def filter_jobs(self, **conditions):
        return self.job_model.filter(**conditions)

    def list_jobs(self, query: dict) -> Tuple[QuerySet, int]:
        return self.job_model.query(**query)

    def stat_jobs(self, query: dict) -> dict:
        return self.job_model.stat(**query)

    def change_canceled_by_vo(self, job_vo: Job) -> None:
        _LOGGER.debug(f"[make_canceled_by_vo] cancel job: {job_vo.job_id}")
        self.update_job_by_vo(
            {"status": "CANCELED", "finished_at": datetime.utcnow()}, job_vo
        )

    def push_job(self, params: dict) -> None:
        token = self.transaction.meta.get("token")

        task = {
            "name": "sync_service_accounts",
            "version": "v1",
            "executionEngine": "BaseWorker",
            "stages": [
                {
                    "locator": "SERVICE",
                    "name": "JobService",
                    "metadata": {"token": token},
                    "method": "sync_service_accounts",
                    "params": {"params": params},
                }
            ],
        }
        _LOGGER.debug(
            f"[push_job] push job: {params['job_id']}, {params['domain_id'], params['trusted_account_id']}"
        )

        queue.put("identity_q", utils.dump_json(task))

    @staticmethod
    def change_in_progress_status(job_vo: Job) -> None:
        _LOGGER.debug(f"[change_in_progress_status] start job: {job_vo.job_id}")
        return job_vo.update({"status": "IN_PROGRESS", "started_at": datetime.utcnow()})

    @staticmethod
    def change_success_status(job_vo: Job) -> None:
        _LOGGER.debug(f"[change_success_status] success job: {job_vo.job_id}")
        job_vo.update(
            {
                "status": "SUCCESS",
                "finished_at": datetime.utcnow(),
            }
        )

    @staticmethod
    def change_canceled_status(job_vo: Job) -> None:
        _LOGGER.debug(f"[change_cancel_status] job canceled: {job_vo.job_id}")
        job_vo.update({"status": "CANCELED", "finished_at": datetime.utcnow()})

    @staticmethod
    def change_error_status(
        job_vo: Job, error: Union[ERROR_BASE, Exception] = None
    ) -> None:
        if not isinstance(error, ERROR_BASE):
            error = ERROR_UNKNOWN(message=str(error))
        _LOGGER.debug(
            f"[change_error_status] job error ({job_vo.job_id}): {error.message}"
        )

        job_vo.update(
            {
                "status": "FAILURE",
                "error_message": error.message,
                "finished_at": datetime.utcnow(),
            }
        )

    def push_dormancy_job(self, params: dict) -> None:
        token = self.transaction.meta.get("token")

        task = {
            "name": "check_dormancy_by_domain",
            "version": "v1",
            "executionEngine": "BaseWorker",
            "stages": [
                {
                    "locator": "SERVICE",
                    "name": "JobService",
                    "metadata": {"token": token},
                    "method": "check_dormancy_by_domain",
                    "params": {"params": params},
                }
            ],
        }
        _LOGGER.debug(f"[push_dormancy_job] {params['domain_id']}")

        queue.put("identity_q", utils.dump_json(task))
