import os
import logging
from celery import shared_task
from utils.generics import add_string_data_to_span
from apps.props.models import Config
from utils.auth import get_tokens_for_user
from apps.users.models import User
from utils.notifications.email_utils import EmailGenerator, GCPEmailer, SendgridEmailer
from opentelemetry import trace

logger = logging.getLogger()
tracer = trace.get_tracer(__name__)


@shared_task(bind=True, max_retries=3)
def send_user_registration_verification_email(self, username):
    span = trace.get_current_span()
    add_string_data_to_span(
        span, f"Initiating user verification email for {username}", "celery.task"
    )

    logger.info(f"Initiating user verification email for {username}")
    user = User.objects.get(username=username)
    token = get_tokens_for_user(user, "email_verification")["access"]
    link = f"{os.environ.get('BASE_URL')}/api/users/v1/verify/{user.username}/{token}"
    email_body = EmailGenerator().generate_user_verification_email(
        user.first_name, link, user_role=user.role.lower()
    )

    email_client = Config.objects.filter(name="email_client").first()
    email = user.email
    subject = "Fuatilia User Signup"
    logger.info(
        f"Initiating {email_client or "GMAIL SMTP"} email to user {username} :: >> \n {email_body}"
    )
    if email_client == "sendgrid_api":
        SendgridEmailer().send_via_api([email], subject, email_body, "info")
    elif email_client == "sendgrid_smtp":
        SendgridEmailer().send_via_smtp([email], subject, email_body, "info")
    else:
        GCPEmailer().send_via_smtp([email], subject, email_body, "info")


@shared_task(bind=True, max_retries=3)
def send_app_registration_verification_email(self, username):
    logger.info(f"Initiating app verification email for {username}")
    user = User.objects.get(username=username)
    token = get_tokens_for_user(user, "email_verification")["access"]
    link = f"{os.environ.get('BASE_URL')}/api/users/v1/verify/{user.username}/{token}"
    email_body = EmailGenerator().generate_app_verification_email(user.username, link)

    email_client = Config.objects.filter(name="email_client").first()
    email = user.email
    subject = "Fuatilia App Signup"
    logger.info(
        f"Initiating {email_client or "gmail_smtp"} to app-user {username} :: >> \n {email_body}"
    )
    if email_client == "sendgrid_api":
        SendgridEmailer().send_via_api([email], subject, email_body, "info")
    elif email_client == "sendgrid_smtp":
        SendgridEmailer().send_via_smtp([email], subject, email_body, "info")
    else:
        GCPEmailer().send_via_smtp([email], subject, email_body, "info")


@shared_task(bind=True, max_retries=3)
def send_user_credential_reset_email(self, username):
    logger.info(f"Initiating app verification email for {username}")
    user = User.objects.get(username=username)
    token = get_tokens_for_user(user, "user_credential_reset")["access"]
    link = f"{os.environ.get('BASE_URL')}/api/users/v1/verify/{user.username}/{token}"
    email_body = EmailGenerator().generate_user_credential_reset_email(
        user.username, link
    )

    email_client = Config.objects.filter(name="email_client").first()
    email = user.email
    subject = "Fuatilia Credential Reset"
    logger.info(
        f"Initiating {email_client or "gmail_smtp"} to app-user {username} :: >> \n {email_body}"
    )
    if email_client == "sendgrid_api":
        SendgridEmailer().send_via_api([email], subject, email_body, "info")
    elif email_client == "sendgrid_smtp":
        SendgridEmailer().send_via_smtp([email], subject, email_body, "info")
    else:
        GCPEmailer().send_via_smtp([email], subject, email_body, "info")
