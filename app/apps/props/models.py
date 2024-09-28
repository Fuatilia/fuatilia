import uuid
from django.db import models


# For stuff like switches etc
class Config(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=100)
    created_by = models.CharField(max_length=100)
    last_updated_by = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.name} --> {self.value}"

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "configs"


class FAQ(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    faq = models.CharField(max_length=100, unique=True)
    answer = models.CharField(max_length=100)
    created_by = models.CharField(max_length=100)
    last_updated_by = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.faq} --> {self.answer}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "faqs"
