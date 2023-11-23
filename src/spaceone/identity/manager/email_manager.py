import logging
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape

from spaceone.core import config, utils
from spaceone.core.manager import BaseManager
from spaceone.identity.connector.smtp_connector import SMTPConnector

_LOGGER = logging.getLogger(__name__)

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), f"../template")
JINJA_ENV = Environment(
    loader=FileSystemLoader(searchpath=TEMPLATE_PATH), autoescape=select_autoescape()
)

LANGUAGE_MAPPER = {
    "default": {
        "reset_password": "Reset your password",
        "temp_password": "Your password has been changed",
        "verify_email": "Verify your notification email",
    },
    "ko": {
        "reset_password": "비밀번호 재설정 안내",
        "temp_password": "임시 비밀번호 발급 안내",
        "verify_email": "알림전용 이메일 계정 인증 안내",
    },
    "en": {
        "reset_password": "Reset your password",
        "temp_password": "Your password has been changed",
        "verify_email": "Verify your notification email",
    },
    "ja": {
        "reset_password": "パスワードリセットのご案内",
        "temp_password": "仮パスワード発行のご案内",
        "verify_email": "通知メールアカウント認証のご案内",
    },
}


class EmailManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.smtp_connector = SMTPConnector()

    def send_reset_password_email(self, user_id, email, reset_password_link, language):
        service_name = self._get_service_name()
        language_map_info = LANGUAGE_MAPPER.get(language, "default")

        template = JINJA_ENV.get_template(
            f"reset_pwd_link_when_pw_forgotten_{language}.html"
        )
        email_contents = template.render(
            user_name=user_id,
            reset_password_link=reset_password_link,
            service_name=service_name,
        )
        subject = f'[{service_name}] {language_map_info["reset_password"]}'

        self.smtp_connector.send_email(email, subject, email_contents)

    def send_temporary_password_email(
        self, user_id, email, console_link, temp_password, language
    ):
        service_name = self._get_service_name()
        language_map_info = LANGUAGE_MAPPER.get(language, "default")

        template = JINJA_ENV.get_template(f"temp_pwd_when_pw_forgotten_{language}.html")
        email_contents = template.render(
            user_name=user_id,
            temp_password=temp_password,
            service_name=service_name,
            login_link=console_link,
        )
        subject = f'[{service_name}] {language_map_info["temp_password"]}'

        self.smtp_connector.send_email(email, subject, email_contents)

    def send_reset_password_email_when_user_added(
        self, user_id, email, reset_password_link, language
    ):
        service_name = self._get_service_name()
        language_map_info = LANGUAGE_MAPPER.get(language, "default")

        template = JINJA_ENV.get_template(
            f"reset_pwd_link_when_user_added_{language}.html"
        )
        email_contents = template.render(
            user_name=user_id,
            reset_password_link=reset_password_link,
            service_name=service_name,
        )
        subject = f'[{service_name}] {language_map_info["reset_password"]}'

        self.smtp_connector.send_email(email, subject, email_contents)

    def send_temporary_password_email_when_user_added(
        self, user_id, email, console_link, temp_password, language
    ):
        service_name = self._get_service_name()
        language_map_info = LANGUAGE_MAPPER.get(language, "default")

        template = JINJA_ENV.get_template(f"temp_pwd_when_user_added_{language}.html")
        email_contents = template.render(
            user_name=user_id,
            temp_password=temp_password,
            service_name=service_name,
            login_link=console_link,
        )
        subject = f'[{service_name}] {language_map_info["temp_password"]}'

        self.smtp_connector.send_email(email, subject, email_contents)

    def send_verification_email(self, user_id, email, verification_code, language):
        service_name = self._get_service_name()
        language_map_info = LANGUAGE_MAPPER.get(language, "default")

        template = JINJA_ENV.get_template(f"verification_code_{language}.html")
        email_contents = template.render(
            user_name=user_id,
            verification_code=verification_code,
            service_name=service_name,
        )
        subject = f'[{service_name}] {language_map_info["verify_email"]}'

        self.smtp_connector.send_email(email, subject, email_contents)

    @staticmethod
    def _get_service_name():
        return config.get_global("EMAIL_SERVICE_NAME")
