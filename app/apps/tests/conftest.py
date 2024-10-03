import pytest
import factory
from apps.bills.models import BillStatus
from apps.representatives.models import (
    GenderChoices,
    PositionChoices,
    PositionTypeChoices,
)
from apps.votes.models import VoteTypeChoices
from utils.enum_utils import HouseChoices
from tests import factories
from factory import fuzzy
from rest_framework.test import APIClient
from pytest_factoryboy import register

register(factories.UserFactory)
register(factories.BillFactory)
register(factories.ConsensusVoteFactory)
register(factories.IndividualVoteFactory)
register(factories.RepresentativeFactory)

pytestmark = pytest.mark.django_db


@pytest.fixture
def super_user_fixt():
    return factories.UserFactory.create(
        username="test_superuser",
        email="test_superuser@fuatilia.com",
        password="test_password",
        user_type="USER",
        parent_organization="fuatilia",
        is_active=True,
        is_superuser=True,
        is_staff=True,
    )


@pytest.fixture
def admin_user_fixt():
    return factories.UserFactory.create(
        first_name=factory.Faker("name"),
        last_name=factory.Faker("name"),
        username="test_adminuser",
        email="test_adminuser@fuatilia.com",
        password="test_password",
        user_type="USER",
        parent_organization="fuatilia",
        is_active=True,
    )


@pytest.fixture
def regular_user_fixt():
    return factories.UserFactory.create(
        first_name=factory.Faker("name"),
        last_name=factory.Faker("name"),
        username="test_regularuser",
        email="test_regularuser@fuatilia.com",
        password="test_password",
        user_type="USER",
        parent_organization="fuatilia",
        is_active=True,
    )


@pytest.fixture
def api_client_fixt():
    return APIClient()


@pytest.fixture
def superuser_token_api_client_fixt(super_user_fixt):
    response = APIClient().post(
        "/api/users/v1/login/user",
        {"username": super_user_fixt.username, "password": "test_password"},
    )

    return response.data.get("access")


@pytest.fixture
def adminuser_token_api_client_fixt(admin_user_fixt):
    client = APIClient().post(
        "/api/users/v1/login/user",
        {"username": admin_user_fixt.username, "password": "test_password"},
    )
    return client


@pytest.fixture
def app_user_fixt(super_user_fixt, api_client_fixt, superuser_token_api_client_fixt):
    response = api_client_fixt.post(
        "/api/users/v1/create/app",
        data={
            "username": "test_appuser",
            "email": "test_appuser@fuatilia.com",
            "password": "test_password",
            "phone_number": "254111111111",
            "parent_organization": "fuatilia",
            "is_active": True,
        },
        headers={
            "Authorization": f"Bearer {superuser_token_api_client_fixt}",
            "X-AUTHENTICATED-USERNAME": super_user_fixt.username,
        },
    )

    print("===>>>>>>>>>>>>>>>>>>======= ", super_user_fixt.is_active)
    print("===========================")
    print(response.data)
    print("===========================")

    return response.data


@pytest.fixture
def auth_appuser_api_client_fixt(app_user_fixt):
    client = APIClient().post(
        "/api/users/v1/login/app",
        {
            "username": app_user_fixt.get("data").get("username"),
            "grant_type": "password",
            "client_id": app_user_fixt.get("data").get("client_id"),
            "client_secret": app_user_fixt.get("data").get("client_secret"),
        },
    )
    return client


# REPRESENTATIVE
@pytest.fixture
def representative_fixt():
    return factories.RepresentativeFactory.create(
        full_name=factory.Faker("name"),
        position=fuzzy.FuzzyChoice(PositionChoices.choices),
        position_type=fuzzy.FuzzyChoice(PositionTypeChoices.choices),
        house=fuzzy.FuzzyChoice(HouseChoices.choices),
        area_represented=factory.Faker("city"),
        gender=fuzzy.FuzzyChoice(GenderChoices.choices),
    )


# BILLS
@pytest.fixture
def bill_fixt():
    return factories.BillFactory.create(
        title=factory.Faker("sentence", nb_words=4),
        status=fuzzy.FuzzyChoice(BillStatus.choices),
        sponsored_by=factory.SubFactory(factories.RepresentativeFactory),
        house=fuzzy.FuzzyChoice(HouseChoices.choices),
    )


# VOTES
@pytest.fixture
def individual_vote_fixt():
    return factories.IndividualVoteFactory.create(
        bill_id=factory.SubFactory(factories.BillFactory),
        representative_id=factory.SubFactory(factories.RepresentativeFactory),
        vote_type=VoteTypeChoices.INDIVIDUAL,
        house=fuzzy.FuzzyChoice(HouseChoices.choices),
        vote=fuzzy.FuzzyChoice(["YES", "NO"]),
    )


@pytest.fixture
def consensus_vote_fixt():
    return factories.ConsensusVoteFactory.create(
        bill_id=factory.SubFactory(factories.BillFactory),
        representative_id=factory.SubFactory(factories.RepresentativeFactory),
        vote_type=VoteTypeChoices.CONCENSUS,
        vote_summary={"YES": 100, "NO": 20, "ABSENT": 30},
        house=fuzzy.FuzzyChoice(HouseChoices.choices),
    )
