import logging
import os
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from typing import List
from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger("app_logger")


class SendgridEmailer:
    def __init__(self) -> None:
        self.info_email = os.environ.get("INFO_EMAIL")
        self.smtp_server = os.environ.get("SG_SMTP_SERVER")

    def send_via_api(
        self, recipients: List[str], subject: str, message: str, message_type: str
    ):
        if message_type == "info":
            sending_email = self.info_email
        else:
            raise NameError(f"No such message_type --> {message_type}")

        mail = Mail(
            Email(sending_email),
            To(recipients[0]),
            subject,
            Content("text/html", message),
        )

        try:
            sg = sendgrid.SendGridAPIClient(api_key=os.environ.get("SG_API_EMAIL_KEY"))
            mail_json = mail.get()
            response = sg.client.mail.send.post(request_body=mail_json)
            logger.info(
                f"=====Completed Sendgrid API email send\n==== status: {response.status_code}\n==== message-id: {response.headers['X-Message-Id']}"
            )
        except Exception as e:
            logger.exception(e)
            raise InterruptedError({"message": e})

    def send_via_smtp(
        self, recipients: List[str], subject: str, message: str, message_type: str
    ):
        server = SMTP(
            os.environ.get("SG_SMTP_SERVER"), int(os.environ.get("SG_SMTP_PORT"))
        )
        server.starttls()

        if message_type == "info":
            from_mail = self.info_email

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        part1 = MIMEText(message, "html")
        msg.attach(part1)

        server.login(
            os.environ.get("SG_SMTP_USERNAME"), os.environ.get("SG_SMTP_API_KEY")
        )
        response = server.sendmail(
            from_mail,
            recipients,
            msg.as_string(),
        )

        logger.info(
            f"=====Completed Sendgrid  SMTP email send\n==== response: {response}"
        )
        server.close()


class GCPEmailer:
    def __init__(self) -> None:
        self.info_email = os.environ.get("INFO_EMAIL")
        self.smtp_server = os.environ.get("SG_SMTP_SERVER")

    def send_via_smtp(
        self, recipients: List[str], subject: str, message: str, message_type: str
    ):
        server = SMTP("smtp.gmail.com", 587)
        server.starttls()

        if message_type == "info":
            from_mail = self.info_email

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        part1 = MIMEText(message, "html")
        msg.attach(part1)

        server.login(from_mail, os.environ.get("GCP_INFO_EMAIL_APP_PASSCODE"))
        response = server.sendmail(
            from_mail,
            recipients,
            msg.as_string(),
        )

        logger.info(f"=====Completed GCP SMTP email send\n==== response: {response}")
        server.close()


class EmailGenerator:
    def __init__(self):
        pass

    def generate_user_verification_email(self, name, link):
        return f"""
        Hello {name},
        <br><br>
        You registered an account on Fuatilia, before being able to use your account
        you need to verify that this is your email address by <a href={link}>clicking here</a>
        <br><br>
        If you did not intiate this email, you can safely ignore.
        <br><br>

        Kind Regards,<br>
        Fuatilia.Africa Team<br>
        """

    def generate_app_verification_email(self, name, link):
        return f""",
        Hello {name},
        <br><br>
        You registered an app on Fuatilia, before being able to use your app
        you need to verify that this is your email address by <a href={link}>clicking here</a>
        <br><br>
        If you did not intiate this email, you can safely ignore.
        <br><br>

        Kind Regards,<br>
        Fuatilia.Africa Team<br>
        """


class GCPServiceAccountEmailer:
    def __init__(self) -> None:
        pass
