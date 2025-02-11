import logging
from datetime import datetime

from spaceone.core.error import ERROR_CONFIGURATION
from spaceone.core import config
from spaceone.core import utils
from spaceone.core.locator import Locator
from spaceone.core.scheduler import HourlyScheduler

_LOGGER = logging.getLogger(__name__)


class ExpiringAppCheckScheduler(HourlyScheduler):
    def __init__(self, queue, interval, minute=":00"):
        super().__init__(queue, interval, minute)
        self.locator = Locator()
        self._init_config()

    def _init_config(self):
        self._token = config.get_global("TOKEN")
        if self._token is None:
            raise ERROR_CONFIGURATION(key="TOKEN")
        self._expiring_app_check_hour = config.get_global("EXPIRING_APP_CHECK_HOUR", 0)

    def create_task(self) -> list:
        tasks = []
        tasks.extend(self._create_expiring_app_check_task())
        return tasks

    def _create_expiring_app_check_task(self):
        current_hour = datetime.utcnow().hour
        if current_hour == self._expiring_app_check_hour:
            stp = {
                "name": "expiring_app_check_schedule",
                "version": "v1",
                "executionEngine": "BaseWorker",
                "stages": [
                    {
                        "locator": "SERVICE",
                        "name": "AppService",
                        "metadata": {"token": self._token},
                        "method": "check_expiring_apps",
                        "params": {"params": {}},
                    }
                ],
            }
            print(
                f"{utils.datetime_to_iso8601(datetime.utcnow())} [INFO] [create_task] check_expiring_apps => START"
            )
            return [stp]
        else:
            print(
                f"{utils.datetime_to_iso8601(datetime.utcnow())} [INFO] [create_task] check_expiring_apps => SKIP"
            )
            print(
                f"{utils.datetime_to_iso8601(datetime.utcnow())} [INFO] [create_task] check_expiring_apps_by: {self._expiring_app_check_hour} hour (UTC)"
            )
            return []