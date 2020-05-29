# from spaceone.core.actuator.health.grpc_health import HealthChecker
from spaceone.core.actuator.health import Health

__all__ = ['IdentityHealth']


class IdentityHealth(Health):

    def check(self):
        # TODO: what you want to check
        return Health.Status.SERVING

    def update_status(self, status: Health.Status):
        super().update_status(status)
