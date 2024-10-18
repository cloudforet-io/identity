import logging
import pyotp
from collections import OrderedDict

from spaceone.core import utils, cache

from spaceone.identity.manager import SecretManager
from spaceone.identity.manager.mfa_manager.base import MFAManager

from spaceone.identity.error.error_user import ERROR_INVALID_VERIFY_CODE

_LOGGER = logging.getLogger(__name__)


class OTPMFAManager(MFAManager):
    mfa_type = "OTP"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def enable_mfa(self, user_id: str, domain_id: str, user_mfa: dict, user_vo):
        credentials = {
            "user_id": user_id,
            "domain_id": domain_id
        }

        otp_secret_key = self._generate_otp_secret_key()
        otp_qrcode_uri = self._generate_otp_qrcode_uri(self._generate_otp(otp_secret_key), user_id)

        self.set_cache_otp_mfa_secret_key(otp_secret_key, user_id, domain_id, credentials, user_mfa)

        user_mfa["options"]["otp_qrcode_uri"] = otp_qrcode_uri

        return user_mfa

    def disable_mfa(self, user_id: str, domain_id: str, user_mfa: dict, user_vo):
        credentials = {
            "user_id": user_id,
            "domain_id": domain_id
        }

        secret_manager: SecretManager = self.locator.get_manager(SecretManager)
        user_secret_id = user_mfa["options"].get("user_secret_id")
        otp_secret_key = secret_manager.get_user_otp_secret_key(user_secret_id, domain_id)

        self.set_cache_otp_mfa_secret_key(otp_secret_key, user_id, domain_id, credentials)

    def confirm_mfa(self, credentials: dict, verify_code: str):

        confirm_result = self.check_otp_mfa_verify_code(credentials, verify_code)

        return confirm_result

    def set_mfa_options(self, user_mfa: dict, credentials: dict):
        mfa_state = user_mfa.get("state", "DISABLED")

        secret_manager: SecretManager = self.locator.get_manager(SecretManager)

        if mfa_state == "ENABLED":
            user_secret_id = user_mfa["options"]["user_secret_id"]
            secret_manager.delete_user_secret(user_secret_id)

        elif mfa_state == "DISABLED":
            otp_secret_key = self.get_cached_otp_secret_key(credentials)
            user_secret_params = {
                "name": f"{credentials['user_id']}_otp_secret_key",
                "data": {
                    "otp_secret_key": otp_secret_key
                }
            }
            user_secret_info = secret_manager.create_user_secret(user_secret_params)
            user_mfa["options"]["user_secret_id"] = user_secret_info.get("user_secret_id")

        return user_mfa

    def set_cache_otp_mfa_secret_key(self, otp_secret_key: str, user_id: str, domain_id: str, credentials: dict, user_mfa: dict = None):
        if cache.is_set():
            ordered_credentials = OrderedDict(sorted(credentials.items()))
            hashed_credentials = utils.dict_to_hash(ordered_credentials)
            cache.delete(f"identity:mfa:{hashed_credentials}")
            cache.set(
                f"identity:mfa:{hashed_credentials}",
                {
                    "otp_secret_key": otp_secret_key,
                    "user_id": user_id,
                    "domain_id": domain_id,
                    "user_mfa": user_mfa
                },
                expire=self.CONST_MFA_VERIFICATION_CODE_TIMEOUT,
            )

    def check_otp_mfa_verify_code(self, credentials: dict, verify_code: str) -> bool:
        if cache.is_set():
            ordered_credentials = OrderedDict(sorted(credentials.items()))
            hashed_credentials = utils.dict_to_hash(ordered_credentials)
            cached_mfa_info = cache.get(f"identity:mfa:{hashed_credentials}")
            otp = self._generate_otp(cached_mfa_info["otp_secret_key"])
            if otp.verify(verify_code):
                return True
            raise ERROR_INVALID_VERIFY_CODE(verify_code=verify_code)

    @staticmethod
    def get_cached_otp_secret_key(credentials: dict):
        if cache.is_set():
            ordered_credentials = OrderedDict(sorted(credentials.items()))
            hashed_credentials = utils.dict_to_hash(ordered_credentials)
            cached_mfa_info = cache.get(f"identity:mfa:{hashed_credentials}")
            cache.delete(f"identity:mfa:{hashed_credentials}")
            return cached_mfa_info["otp_secret_key"]

    @staticmethod
    def _generate_otp_secret_key() -> str:
        return pyotp.random_base32()

    def _generate_otp_qrcode_uri(self, otp, user_id: str) -> str:
        otp_qrcode_uri = otp.provisioning_uri(name=user_id, issuer_name=self.CONST_MFA_OTP_ISSUER_NAME)
        return otp_qrcode_uri

