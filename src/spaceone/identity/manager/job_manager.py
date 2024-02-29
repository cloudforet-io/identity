import logging
from typing import Tuple, List
from mongoengine import QuerySet

from spaceone.core.manager import BaseManager

from spaceone.identity.model.job.database import Job

_LOGGER = logging.getLogger(__name__)


class JobManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.job_model = Job
