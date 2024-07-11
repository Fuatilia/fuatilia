import logging
from datetime import datetime
import logging.config

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "when": "H",
            "interval": 3,
            "formatter": "verbose",
            "filename": f"logs/{datetime.now().strftime('%Y_%m_%d')} {datetime.now().hour//3}.log",
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "logging.handlers.SMTPHandler",
            "mailhost": "mailserver",
            "fromaddr": "noreply@example.com",
            "toaddrs": ["me@example.com"],
            "subject": "{message}",
            "credentials": ("user", "password"),
        },
    },
    "loggers": {
        "prod": {"handlers": ["console", "file", "mail_admins"], "level": "INFO"},
        "dev": {"handlers": ["console", "file"], "level": "DEBUG"},
    },
}

logging.config.dictConfig(logging_config)

logger = logging.getLogger("dev")
