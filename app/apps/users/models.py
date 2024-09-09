import logging
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.contrib.auth.hashers import Argon2PasswordHasher

logger = logging.getLogger("app_logger")


class UserType(models.TextChoices):
    USER = "USER"
    APP = "APP"


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=40, null=True)
    last_name = models.CharField(max_length=40, null=True)
    client_id = models.CharField(max_length=40, null=True)
    client_secret = models.CharField(max_length=40, null=True)
    phone_number = models.CharField(max_length=40, null=True)
    username = models.CharField(
        max_length=100, unique=True
    )  # Allow users to define their usernames
    email = models.EmailField(max_length=30)
    password = models.CharField(max_length=255)
    user_type = models.CharField(
        choices=UserType.choices, max_length=10, default=UserType.USER
    )
    parent_organization = models.CharField(max_length=100)
    role = models.CharField(max_length=50, null=True)
    pending_update_json = models.JSONField(null=True)  # Incase of maker-cheker
    is_active = models.BooleanField(default=False)
    updated_by = models.CharField(max_length=30, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "username"

    def __repr__(self):
        return self.username

    class Meta:
        ordering = ["-created_at"]
        unique_together = [
            "email",
            "user_type",
        ]  # Allow people to use their emails for their apps
        db_table = "users"
        verbose_name_plural = "users"

    # For some reason DRF doesn't automatically hash passwords for AbstractUses
    # even with .set_password in the serializer
    # This helps with that
    def save(self, *args, **kwargs):
        self.set_password(self.password)
        super().save(*args, **kwargs)

    def verify_app_credentials(self, data):
        logger.info(
            f"Verifying app credentials for {self.id} ????? {data["client_secret"]}"
        )
        if self.client_id == data["client_id"]:
            if Argon2PasswordHasher().verify(data["client_secret"], self.client_secret):
                logger.info(f"Succesfully verified app credentials for {self.id}")
                return True
        return False
