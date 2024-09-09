import pytest
import factory
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_superuser_can_log_in(super_user_fixt, api_client_fixt):
    response = api_client_fixt.post(
        "/api/users/v1/login/user",
        {"username": super_user_fixt.username, "password": "test_password"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("access") is not None


def test_superuser_can_create_admin_user(
    super_user_fixt, api_client_fixt, superuser_token_api_client_fixt
):
    token = superuser_token_api_client_fixt
    response = api_client_fixt.post(
        "/api/users/v1/create/user",
        {
            "first_name": factory.Faker("name"),
            "last_name": factory.Faker("name"),
            "username": "test_adminuser",
            "email": "test_adminuser@fuatilia.com",
            "password": "test_password",
            "user_type": "USER",
            "parent_organization": "fuatilia",
            "is_active": True,
        },
        headers={
            "Authorization": f"Bearer {token}",
            "X-AUTHENTICATED-USERNAME": super_user_fixt.username,
        },
    )

    assert response.status_code == status.HTTP_201_CREATED


def test_admin_user_can_log_in(admin_user_fixt, api_client_fixt):
    response = api_client_fixt.post(
        "/api/users/v1/login/user",
        {"username": admin_user_fixt.username, "password": "test_password"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("access") is not None


def test_superuser_can_create_app_user(
    super_user_fixt, api_client_fixt, superuser_token_api_client_fixt
):
    token = superuser_token_api_client_fixt
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
            "Authorization": f"Bearer {token}",
            "X-AUTHENTICATED-USERNAME": super_user_fixt.username,
        },
    )

    assert response.status_code == status.HTTP_201_CREATED


def test_app_user_can_log_in(app_user_fixt, api_client_fixt):
    response = api_client_fixt.post(
        "/api/users/v1/login/app",
        {
            "username": app_user_fixt.get("data").get("username"),
            "grant-type": "password",
            "client_id": app_user_fixt.get("data").get("client_id"),
            "client_secret": app_user_fixt.get("data").get("client_secret"),
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("access") is not None
