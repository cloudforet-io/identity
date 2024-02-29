import logging
from typing import Union

from spaceone.core.service import *
from spaceone.core.service.utils import *

from spaceone.identity.manager.job_manager import JobManager
from spaceone.identity.model.job.request import *
from spaceone.identity.model.job.response import *
from spaceone.identity.error.error_project import *

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

        self.job_vo.delete_job_by_vo(job_vo)
