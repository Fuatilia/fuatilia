import os
from apps.props.models import Config
from utils.auth import get_tokens_for_user
from apps.users.models import User
from utils.notifications.email_utils import EmailGenerator, GCPEmailer, SendgridEmailer


def send_user_registration_verification_email(username):
    user = User.objects.get(username=username)
    token = get_tokens_for_user(user, "email_verification")["access"]
    link = f"{os.environ.get("BASE_URL")}/api/users/v1/verify/{user.username}/{token}"
    email_body = EmailGenerator().generate_user_verification_email(
        user.first_name, link
    )

    email_client = Config.objects.filter(name="email_client").first()
    email = user["email"]
    subject = "Fuatilia user signup"
    if email_client == "sendgrid_api":
        SendgridEmailer().send_via_api([email], subject, email_body, "info")
    elif email_client == "sendgrid_smtp":
        SendgridEmailer().send_via_smtp([email], subject, email_body, "info")
    else:
        GCPEmailer().send_via_smtp([email], subject, email_body, "info")
