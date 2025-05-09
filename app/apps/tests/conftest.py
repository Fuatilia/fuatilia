import pytest
import factory
from apps.users.models import User
from apps.bills.models import BillStatus
from apps.representatives.models import (
    GenderChoices,
    PositionChoices,
    PositionClassChoices,
)
from apps.votes.models import VoteTypeChoices
from utils.enum_utils import HouseChoices
from tests import factories
from rest_framework.test import APIClient
from pytest_factoryboy import register
from django.contrib.contenttypes.models import ContentType

register(factories.UserFactory)
register(factories.BillFactory)
register(factories.ConsensusVoteFactory)
register(factories.IndividualVoteFactory)
register(factories.RepresentativeFactory)
register(factories.GroupFactory)
register(factories.PermissionFactory)
register(factories.ConfigFactory)
register(factories.FAQFactory)

pytestmark = pytest.mark.django_db(databases=["default"])


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
def app_user_fixt(
    client_app_group_fixt, api_client_fixt, superuser_token_api_client_fixt
):
    response = api_client_fixt.post(
        "/api/users/v1/create/app",
        data={
            "username": "test_appuser",
            "email": "test_appuser@fuatilia.com",
            "password": "test_password",
            "phone_number": "254111111111",
            "parent_organization": "fuatilia",
            "user_type": "APP",
        },
        headers={
            "Authorization": f"Bearer {superuser_token_api_client_fixt}",
        },
    )

    return response.data


@pytest.fixture
def auth_appuser_api_client_fixt(app_user_fixt):
    client = APIClient().post(
        "/api/users/v1/login/app",
        {
            "username": app_user_fixt.get("data").get("username"),
            "grant_type": "client_credentials",
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
        position=PositionChoices.MP,
        position_class=PositionClassChoices.ELECTED,
        house=HouseChoices.NATIONAL,
        area_represented=factory.Faker("city"),
        gender=GenderChoices.MALE,
    )


# BILLS
@pytest.fixture
def bill_fixt():
    return factories.BillFactory.create(
        title=factory.Faker("sentence", nb_words=4),
        status=BillStatus.IN_PROGRESS,
        sponsored_by=factories.RepresentativeFactory.create().__dict__["id"],
        house=HouseChoices.NATIONAL,
    )


# VOTES
@pytest.fixture
def individual_vote_fixt():
    return factories.IndividualVoteFactory.create(
        bill_id=factories.BillFactory.create().__dict__.get("id"),
        representative_id=factories.RepresentativeFactory.create().__dict__.get("id"),
        vote_type=VoteTypeChoices.INDIVIDUAL,
        house=HouseChoices.NATIONAL,
        vote="NO",
    )


@pytest.fixture
def consensus_vote_fixt():
    return factories.ConsensusVoteFactory.create(
        bill_id=factories.BillFactory.create().__dict__.get("id"),
        representative_id=factories.RepresentativeFactory.create().__dict__.get("id"),
        vote_type=VoteTypeChoices.CONCENSUS,
        vote_summary={"YES": 100, "NO": 20, "ABSENT": 30},
        house=HouseChoices.SENATE,
    )


# GROUPS
@pytest.fixture
def client_app_group_fixt(superuser_token_api_client_fixt, client_app_perm_fix):
    client = APIClient().post(
        "/api/roles/v1/create",
        data={
            "role_name": "client_app",
            "permissions": ["view_representatives"],
            "action": "add",
        },
        headers={
            "Authorization": f"Bearer {superuser_token_api_client_fixt}",
        },
    )
    return client


@pytest.fixture
def fuatilia_verifier_group_fixt(superuser_token_api_client_fixt, client_app_perm_fix):
    client = APIClient().post(
        "/api/roles/v1/create",
        data={
            "role_name": "fuatilia_verifier",
            "permissions": ["view_representatives"],
            "action": "add",
        },
        headers={
            "Authorization": f"Bearer {superuser_token_api_client_fixt}",
        },
    )
    return client


# PERMISSIONS
@pytest.fixture
def client_app_perm_fix():
    return factories.PermissionFactory.create(
        codename="view_representatives",
        name="view_representatives",
        content_type=ContentType.objects.get_for_model(User),
    )
