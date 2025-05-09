import uuid
from django.db import models
from utils.enum_utils import VoteTypeChoices, HouseChoices


# Create your models here.
class Vote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Probably have bill ID as a foreign key for fetching etc.
    bill_id = models.CharField(max_length=50)
    # Probably have represantative ID as a foreign key for fetching etc.
    # Pass 'ALL' for consensus/confidential votes
    representative_id = models.CharField(max_length=50)
    vote_type = models.CharField(
        max_length=15,
        choices=VoteTypeChoices.choices,
        default=VoteTypeChoices.INDIVIDUAL,
    )
    # Total counts etc --> Will help with the confidential ones
    # will be a json string of how voting panned out
    vote_summary = models.JSONField(null=True)

    # In the event a representative moves houses
    # i.e was an mp then senator, using rep ID might be confusing
    house = models.CharField(max_length=10, choices=HouseChoices.choices)
    vote = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return f"{self.vote_type} {self.house}  {self.vote} {self.vote_summary}"

    class Meta:
        indexes = [
            models.Index(fields=["bill_id", "representative_id", "vote_type", "house"]),
        ]
