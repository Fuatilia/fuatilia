import uuid
from django.db import models
from utils.enum_utils import HouseChoices


class BillStatus(models.TextChoices):
    FIRST_READING = "FIRST_READING"
    SECOND_READING = "SECOND_READING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    IN_PROGRESS = "IN_PROGRESS"
    ASCENTED = "ASCENTED"


class Bill(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20, choices=BillStatus, default=BillStatus.IN_PROGRESS
    )
    sponsored_by = models.CharField(max_length=100)  # rep name/ID
    supported_by = models.CharField(max_length=100, null=True)
    house = models.CharField(max_length=20, choices=HouseChoices.choices)
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
    final_date_voted = models.CharField(
        max_length=100, null=True
    )  # (When the bill was passed or failed)
    topics_in_the_bill = models.CharField(
        max_length=200, null=True
    )  # (Will help in searches)
    file_url = models.CharField(max_length=100, null=True)
    updated_by = models.CharField(max_length=20, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "bill"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["summary", "topics_in_the_bill"])]
