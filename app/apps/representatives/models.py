import uuid
from django.db import models
from utils.enum_utils import HouseChoices
from utils.enum_utils import PositionChoices, PositionClassChoices, GenderChoices


# Actual representative Model
class Representative(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=100, unique=True)
    position = models.CharField(max_length=10, choices=PositionChoices.choices)
    position_class = models.CharField(
        max_length=10, choices=PositionClassChoices.choices
    )
    house = models.CharField(max_length=10, choices=HouseChoices.choices)
    area_represented = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, null=True)
    image_url = models.CharField(max_length=250, null=True)
    gender = models.CharField(max_length=10, choices=GenderChoices.choices, null=True)
    current_parliamentary_roles = models.CharField(
        max_length=100, null=True
    )  # e.g chief whip , Majority leader, (Overwrites any previous role)
    representation_summary = models.JSONField(null=True)
    pending_update_json = models.JSONField(null=True)
    version = models.IntegerField(default=0)
    last_updated_by = models.CharField(max_length=40, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return self.__dict__

    class Meta:
        db_table = "representatives"
        ordering = ["-created_at"]
        verbose_name_plural = "representatives"
