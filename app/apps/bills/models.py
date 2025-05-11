import uuid
from django.db import models
from utils.enum_utils import HouseChoices


class BillStatus(models.TextChoices):
    FIRST_READING = "FIRST_READING"
    SECOND_READING = "SECOND_READING"
    THIRD_READING = "THIRD_READING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    IN_PROGRESS = "IN_PROGRESS"
    ASCENTED = "ASSENTED"


class Bill(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=150)
    status = models.CharField(
        max_length=20, choices=BillStatus.choices, default=BillStatus.IN_PROGRESS
    )
    sponsored_by = models.CharField(max_length=50)  # rep name/ID
    supported_by = models.CharField(max_length=50, null=True)
    house = models.CharField(max_length=20, choices=HouseChoices.choices)
    bill_no = models.CharField(
        max_length=20, null=True
    )  # e.g "10 of 2024", Tracks bills in the year
    gazette_no = models.CharField(max_length=5, null=True)
    date_introduced = models.DateField(null=True)
    summary = models.CharField(max_length=100, null=True)
    summary_created_by = models.CharField(
        max_length=100, null=True
    )  # Id of portal user)
    summary_upvoted_by = models.CharField(
        max_length=100, null=True
    )  # (expert names/ids)
    summary_downvoted_by = models.CharField(
        max_length=100, null=True
    )  # (expert names/ids)
    final_date_voted = models.DateField(
        null=True
    )  # (When the bill was passed or failed)
    topics_in_the_bill = models.CharField(
        max_length=200, null=True
    )  # (Will help in searches)
    metadata = models.JSONField(null=True)
    file_url = models.CharField(max_length=100, null=True)
    last_updated_by = models.CharField(max_length=20, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "bills"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["summary", "topics_in_the_bill"])]
