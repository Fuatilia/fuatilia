import pytest
import factory
from tests import factories
from rest_framework.test import APIClient
from pytest_factoryboy import register

register(factories.UserFactory)
register(factories.BillsFactory)
register(factories.ConsensusVoteFactory)
register(factories.IndividualVoteFactory)
register(factories.RepresentativeFactory)


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
def app_user_fixt(api_client_fixt, super_user_fixt, superuser_token_api_client_fixt):
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
