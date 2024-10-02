from celery import shared_task
from utils.auth import get_tokens_for_user
from apps.users.models import User
from utils.notifications.email_utils import EmailGenerator, GCPEmailer


# TODO Add config check for email client
@shared_task
def send_user_registration_verification_email(user: User):
    token = get_tokens_for_user(user, "email_verification")["access"]
    link = f"http://localhost:8000/api/users/v1/verify/{user.username}/{token}"
    email_body = EmailGenerator().generate_user_verification_email(
        user.first_name, link
    )
    # SendgridEmailer().send_via_api([email], "Fuatilia signup", email_body,"info")
    # SendgridEmailer().send_via_smtp([email], "Fuatilia signup", email_body,"info")
    GCPEmailer().send_via_smtp([user.email], "Fuatilia signup", email_body, "info")
