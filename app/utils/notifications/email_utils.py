import logging
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

logger = logging.getLogger("app_logger")


class SendgridEmailer:
    def __init__(self) -> None:
        self.info_email = os.environ.get("INFO_EMAIL")

    def SendViaApi(
        self, recipients: list[str], subject: str, message: str, message_type: str
    ):
        if message_type == "info":
            sending_email = self.info_email

        message = Mail(
            from_email=sending_email,
            to_emails=recipients,
            subject=subject,
            html_content=message,
        )

        try:
            sg = SendGridAPIClient(os.environ.get("SG_API_EMAIL_KEY"))
            response = sg.send(message)
            logger.info(response.status_code)
            logger.info(response.body)
            logger.info(response.headers)
        except Exception as e:
            logger.exception(e.message)
            raise InterruptedError({"message": e.message})


class GCPServiceAccountEmailer:
    def __init__(self) -> None:
        pass
