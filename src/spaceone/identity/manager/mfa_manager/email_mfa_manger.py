import logging
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape

from spaceone.core import config
from spaceone.identity.connector.smtp_connector import SMTPConnector
from spaceone.identity.manager.mfa_manager.base import MFAManager

_LOGGER = logging.getLogger(__name__)

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), f"../../template")
JINJA_ENV = Environment(
    loader=FileSystemLoader(searchpath=TEMPLATE_PATH), autoescape=select_autoescape()
)

LANGUAGE_MAPPER = {
    "default": {
        "verify_mfa_email": "Verify your MFA email",
        "authentication_mfa_email": "Your multi-factor authentication code.",
    },
    "ko": {
        "verify_mfa_email": "MFA 이메일 계정 인증 안내",
        "authentication_mfa_email": "MFA 인증 코드 발송",
    },
    "en": {
        "verify_mfa_email": "Verify your MFA email",
        "authentication_mfa_email": "Your multi-factor authentication code.",
    },
    "ja": {
        "verify_mfa_email": "MFAメールアカウント認証のご案内",
        "authentication_mfa_email": "MFA認証コード送信",
    },
}


class EmailMFAManager(MFAManager):
    mfa_type = "EMAIL"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.smtp_connector = SMTPConnector()

    def enable_mfa(self, user_id: str, domain_id: str, user_mfa: dict, user_vo):
        self.send_mfa_verify_email(
            user_id, domain_id, user_mfa["options"].get("email"), user_vo.language, user_mfa
        )
        return user_mfa

    def disable_mfa(self, user_id: str, domain_id: str, user_mfa: dict, user_vo):
        self.send_mfa_verify_email(
            user_id, domain_id, user_mfa["options"].get("email"), user_vo.language
        )

    def confirm_mfa(self, credentials: dict, verify_code: str):

        confirm_result = self.check_mfa_verify_code(credentials, verify_code)

        return confirm_result

    def set_mfa_options(self, user_mfa: dict, credentials: dict):
        return user_mfa

    def send_mfa_verify_email(self, user_id: str, domain_id: str, email: str, language: str, user_mfa: dict = None):
        service_name = self._get_service_name()
        language_map_info = LANGUAGE_MAPPER.get(language, "default")
        credentials = {"user_id": user_id, "domain_id": domain_id}
        verify_code = self.create_mfa_verify_code(user_id, domain_id, credentials, user_mfa)

        template = JINJA_ENV.get_template(f"verification_MFA_code_{language}.html")
        email_contents = template.render(
            user_name=user_id, verification_code=verify_code, service_name=service_name
        )
        subject = f'[{service_name}] {language_map_info["verify_mfa_email"]}'

        self.smtp_connector.send_email(email, subject, email_contents)

    def send_mfa_authentication_email(
        self, user_id: str, domain_id: str, email: str, language: str, credentials: dict
    ):
        service_name = self._get_service_name()
        language_map_info = LANGUAGE_MAPPER.get(language, "default")
        verify_code = self.create_mfa_verify_code(user_id, domain_id, credentials)

        template = JINJA_ENV.get_template(f"authentication_code_{language}.html")
        email_contents = template.render(
            user_name=user_id,
            authentication_code=verify_code,
            service_name=service_name,
        )
        subject = f'[{service_name}] {language_map_info["authentication_mfa_email"]}'

        self.smtp_connector.send_email(email, subject, email_contents)

    @staticmethod
    def _get_service_name():
        return config.get_global("EMAIL_SERVICE_NAME")
