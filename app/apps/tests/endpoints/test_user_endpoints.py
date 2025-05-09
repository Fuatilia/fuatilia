import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db(databases=["default"])


@pytest.fixture
def create_app_user_fixt(
    api_client_fixt, superuser_token_api_client_fixt, client_app_group_fixt
):
    return api_client_fixt.post(
        "/api/users/v1/create/app",
        data={
            "username": "test_appuser",
            "email": "test_appuser@fuatilia.com",
            "password": "test_password",
            "phone_number": "254111111111",
            "user_type": "APP",
            "parent_organization": "fuatilia",
            "is_active": True,
        },
        headers={
            "Authorization": f"Bearer {superuser_token_api_client_fixt}",
        },
    )


def test_superuser_can_log_in(super_user_fixt, api_client_fixt):
    response = api_client_fixt.post(
        "/api/users/v1/login/user",
        {"username": super_user_fixt.username, "password": "test_password"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("access") is not None


def test_superuser_can_create_admin_user(
    api_client_fixt, superuser_token_api_client_fixt, fuatilia_verifier_group_fixt
):
    response = api_client_fixt.post(
        "/api/users/v1/create/user",
        {
            "first_name": "AdminFirstName",
            "last_name": "AdminLastName",
            "username": "test_adminuser",
            "email": "test_adminuser@fuatilia.com",
            "password": "test_password",
            "user_type": "USER",
            "parent_organization": "fuatilia",
            "is_active": True,
        },
        headers={
            "Authorization": f"Bearer {superuser_token_api_client_fixt}",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED


def test_admin_user_can_log_in(admin_user_fixt, api_client_fixt, client_app_group_fixt):
    response = api_client_fixt.post(
        "/api/users/v1/login/user",
        {"username": admin_user_fixt.username, "password": "test_password"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("access") is not None


def test_superuser_can_create_app_user(create_app_user_fixt):
    assert create_app_user_fixt.status_code == status.HTTP_201_CREATED


def test_app_user_can_log_in(create_app_user_fixt, api_client_fixt):
    response = api_client_fixt.post(
        "/api/users/v1/login/app",
        {
            "username": create_app_user_fixt.data.get("data").get("username"),
            "grant-type": "password",
            "client_id": create_app_user_fixt.data.get("data").get("client_id"),
            "client_secret": create_app_user_fixt.data.get("data").get("client_secret"),
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("access") is not None


def test_user_filter(api_client_fixt, superuser_token_api_client_fixt, super_user_fixt):
    token = superuser_token_api_client_fixt
    response = api_client_fixt.get(
        "/api/users/v1/filter?items_per_page=10&page=1",
        headers={
            "Authorization": f"Bearer {token}",
            "X-AUTHENTICATED-USERNAME": super_user_fixt.username,
        },
    )
    assert response.status_code == 200
    assert len(response.data.get("data")) > 0


def test_user_fetch(
    api_client_fixt, superuser_token_api_client_fixt, super_user_fixt, regular_user_fixt
):
    token = superuser_token_api_client_fixt
    response = api_client_fixt.get(
        f"/api/users/v1/{regular_user_fixt.id}",
        headers={
            "Authorization": f"Bearer {token}",
            "X-AUTHENTICATED-USERNAME": super_user_fixt.username,
        },
    )
    assert response.status_code == 200
    assert len(response.data.get("data")) > 0


def test_user_delete(
    api_client_fixt, superuser_token_api_client_fixt, super_user_fixt, regular_user_fixt
):
    token = superuser_token_api_client_fixt
    response = api_client_fixt.delete(
        f"/api/users/v1/{regular_user_fixt.id}",
        headers={
            "Authorization": f"Bearer {token}",
            "X-AUTHENTICATED-USERNAME": super_user_fixt.username,
        },
    )
    assert response.status_code == 204
