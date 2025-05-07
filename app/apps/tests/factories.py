import factory
from apps.votes.models import Vote
from apps.representatives.models import Representative
from apps.users.models import User
from apps.bills.models import Bill
from apps.props.models import Config, FAQ
from django.contrib.auth.models import Group, Permission


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


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group


class PermissionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Permission


class ConfigFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Config


class FAQFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FAQ
