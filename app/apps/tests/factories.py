from apps.votes.models import Vote, VoteTypeChoices
from apps.representatives.models import (
    GenderChoices,
    PositionChoices,
    PositionTypeChoices,
)
from apps.users.models import User
from utils.enum_utils import HouseChoices
from apps.bills.models import Bill, BillStatus
import factory
from factory import fuzzy


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User


class RepresentativeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    full_name = factory.Faker("name")
    position = fuzzy.FuzzyChoice(PositionChoices.choices)
    position_type = fuzzy.FuzzyChoice(PositionTypeChoices.choices)
    house = fuzzy.FuzzyChoice(HouseChoices.choices)
    area_represented = factory.Faker("city")
    gender = fuzzy.FuzzyChoice(GenderChoices.choices)


class BillsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Bill

    title = factory.Faker("sentence", nb_words=4)
    status = fuzzy.FuzzyChoice(BillStatus.choices)
    sponsored_by = factory.SubFactory(RepresentativeFactory)
    house = fuzzy.FuzzyChoice(HouseChoices.choices)


class IndividualVoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Vote

    bill_id = factory.SubFactory(BillsFactory)
    representative_id = factory.SubFactory(RepresentativeFactory)
    vote_type = VoteTypeChoices.INDIVIDUAL
    house = fuzzy.FuzzyChoice(HouseChoices.choices)
    vote = fuzzy.FuzzyChoice(["YES", "NO"])


class ConsensusVoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Vote

    bill_id = factory.SubFactory(BillsFactory)
    representative_id = factory.SubFactory(RepresentativeFactory)
    vote_type = VoteTypeChoices.CONCENSUS
    vote_summary = ({"YES": 100, "NO": 20, "ABSENT": 30},)
    house = fuzzy.FuzzyChoice(HouseChoices.choices)
