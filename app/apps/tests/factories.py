from apps.votes.models import Vote
from apps.representatives.models import Representative
from apps.users.models import User
from apps.bills.models import Bill
import factory


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User


class RepresentativeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Representative


class BillFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Bill


class IndividualVoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Vote


class ConsensusVoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Vote
