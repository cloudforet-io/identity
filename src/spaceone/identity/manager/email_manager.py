import logging
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape

from spaceone.core import config
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
        "invite_external_user": "You've been invited to join.",
        "app_expiration_email": "Your App is expiring",
    },
    "ko": {
        "reset_password": "비밀번호 재설정 안내",
        "temp_password": "임시 비밀번호 발급 안내",
        "verify_email": "알림전용 이메일 계정 인증 안내",
        "invite_external_user": "계정 초대 안내.",
        "app_expiration_email": "앱 만료 안내",
    },
    "en": {
        "reset_password": "Reset your password",
        "temp_password": "Your password has been changed",
        "verify_email": "Verify your notification email",
        "invite_external_user": "You've been invited to join.",
        "app_expiration_email": "Your App is expiring",
    },
    "ja": {
        "reset_password": "パスワードリセットのご案内",
        "temp_password": "仮パスワード発行のご案内",
        "verify_email": "通知メールアカウント認証のご案内",
        "invite_external_user": "参加するように招待されました",
        "app_expiration_email": "Your App is expiring",
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
        self, domain_display_name, user_id, email, reset_password_link, language
    ):
        service_name = self._get_service_name()
        language_map_info = LANGUAGE_MAPPER.get(language, "default")

        template = JINJA_ENV.get_template(
            f"reset_pwd_link_when_user_added_{language}.html"
        )
        email_contents = template.render(
            domain_display_name=domain_display_name,
            user_name=user_id,
            reset_password_link=reset_password_link,
            service_name=service_name,
        )
        subject = f'[{service_name}] {language_map_info["reset_password"]}'

        self.smtp_connector.send_email(email, subject, email_contents)

    def send_temporary_password_email_when_user_added(
        self, domain_display_name, user_id, email, console_link, temp_password, language
    ):
        service_name = self._get_service_name()
        language_map_info = LANGUAGE_MAPPER.get(language, "default")

        template = JINJA_ENV.get_template(f"temp_pwd_when_user_added_{language}.html")
        email_contents = template.render(
            domain_display_name=domain_display_name,
            user_name=user_id,
            temp_password=temp_password,
            service_name=service_name,
            login_link=console_link,
        )
        subject = f'[{service_name}] {language_map_info["temp_password"]}'

        self.smtp_connector.send_email(email, subject, email_contents)

    def send_invite_email_when_external_user_added(
        self,
        domain_display_name: str,
        user_id: str,
        email: str,
        console_link: str,
        language: str,
        external_auth_provider: str = "EXTERNAL",
    ):
        service_name = self._get_service_name()
        language_map_info = LANGUAGE_MAPPER.get(language, "default")

        template = JINJA_ENV.get_template(f"sso_invite_user_link_{language}.html")

        email_contents = template.render(
            domain_display_name=domain_display_name,
            user_name=user_id,
            auth_type=external_auth_provider,
            service_name=service_name,
            login_link=console_link,
        )

        subject = f'[{service_name}] {language_map_info["invite_external_user"]}'
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

    def send_domain_app_expiration_email(self, user_id: str, days_left: int, app_id: str, app_name: str, expired_at: str, console_link: str, email: str, language: str):
        service_name = config.get_global("EMAIL_SERVICE_NAME")
        language_map_info = LANGUAGE_MAPPER.get(language, "default")

        template = JINJA_ENV.get_template(f"domain_app_expiration_{language}.html")
        email_contents = template.render(
            user_name = user_id,
            days_left = days_left,
            app_id=app_id,
            app_name = app_name,
            expired_at = expired_at,
            console_link=console_link,
            service_name = service_name,
        )
        subject = f'[{service_name}] {language_map_info["app_expiration_email"]}'

        self.smtp_connector.send_email(email, subject, email_contents)

    def send_workspace_app_expiration_email(self, user_id: str, days_left: int, app_id: str, app_name: str, workspace_name: str,  expired_at: str, console_link: str, email: str, language: str):
        service_name = config.get_global("EMAIL_SERVICE_NAME")
        language_map_info = LANGUAGE_MAPPER.get(language, "default")

        template = JINJA_ENV.get_template(f"workspace_app_expiration_{language}.html")
        email_contents = template.render(
            user_name=user_id,
            days_left=days_left,
            app_id=app_id,
            app_name=app_name,
            workspace_name=workspace_name,
            expired_at=expired_at,
            console_link=console_link,
            service_name=service_name,
        )
        subject = f'[{service_name}] {language_map_info["app_expiration_email"]}'

        self.smtp_connector.send_email(email, subject, email_contents)



    @staticmethod
    def _get_service_name():
        return config.get_global("EMAIL_SERVICE_NAME")
