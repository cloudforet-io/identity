import logging
from datetime import datetime

from spaceone.core.error import ERROR_CONFIGURATION
from spaceone.core import config
from spaceone.core import utils
from spaceone.core.locator import Locator
from spaceone.core.scheduler import HourlyScheduler

_LOGGER = logging.getLogger(__name__)


class DormancyScheduler(HourlyScheduler):
    def __init__(self, queue, interval, minute=":30"):
        super().__init__(queue, interval, minute)
        self.locator = Locator()
        self._init_config()

    def _init_config(self):
        self._token = config.get_global("TOKEN")
        if self._token is None:
            raise ERROR_CONFIGURATION(key="TOKEN")
        self._dormancy_check_hours = config.get_global("DORMANCY_CHECK_HOUR", 0)

    def create_task(self) -> list:
        tasks = []
        tasks.extend(self._create_dormancy_task())
        return tasks

    def _create_dormancy_task(self):
        current_hour = datetime.utcnow().hour
        if current_hour == self._dormancy_check_hours:
            stp = {
                "name": "dormancy_schedule",
                "version": "v1",
                "executionEngine": "BaseWorker",
                "stages": [
                    {
                        "locator": "SERVICE",
                        "name": "JobService",
                        "metadata": {"token": self._token},
                        "method": "check_dormancy",
                        "params": {"params": {}},
                    }
                ],
            }
            print(
                f"{utils.datetime_to_iso8601(datetime.utcnow())} [INFO] [create_task] check_dormancy_by_domains => START"
            )
            return [stp]
        else:
            print(
                f"{utils.datetime_to_iso8601(datetime.utcnow())} [INFO] [create_task] check_dormancy_by_domains => SKIP"
            )
            print(
                f"{utils.datetime_to_iso8601(datetime.utcnow())} [INFO] [create_task] check_dormancy_by_domains: {self._dormancy_check_hours} hour (UTC)"
            )
            return []
