import logging
import pytest

pytestmark = pytest.mark.django_db

logging.disable(logging.CRITICAL)


@pytest.fixture
def create_permission_fixt(
    super_user_fixt, api_client_fixt, superuser_token_api_client_fixt
):
    return api_client_fixt.post(
        "/api/roles/v1/permission/create",
        data={"definition": "Can view s3bucket", "permission_name": "view_s3bucket"},
        headers={
            "Authorization": f"Bearer {superuser_token_api_client_fixt}",
            "X-AUTHENTICATED-USERNAME": super_user_fixt.username,
        },
    )


def test_permission_creation(create_permission_fixt):
    assert create_permission_fixt.status_code == 201
    assert create_permission_fixt.data.get("data").get("codename") == "view_s3bucket"


def test_permission_filter(api_client_fixt, create_permission_fixt):
    response = api_client_fixt.get(
        "/api/roles/v1/permission/filter?items_per_page=10&page=1&permission_name=s3bucket",
        headers={
            "Authorization": create_permission_fixt.request.get("HTTP_AUTHORIZATION"),
            "X-AUTHENTICATED-USERNAME": create_permission_fixt.request.get(
                "HTTP_X_AUTHENTICATED_USERNAME"
            ),
        },
    )

    assert response.status_code == 200
    assert "s3bucket" in response.data.get("data")[0]["codename"]


def test_permission_fetch(api_client_fixt, create_permission_fixt):
    permission_id = create_permission_fixt.data.get("data").get("pk")

    response = api_client_fixt.get(
        f"/api/roles/v1/permission/{permission_id}",
        headers={
            "Authorization": create_permission_fixt.request.get("HTTP_AUTHORIZATION"),
            "X-AUTHENTICATED-USERNAME": create_permission_fixt.request.get(
                "HTTP_X_AUTHENTICATED_USERNAME"
            ),
        },
    )
    assert response.status_code == 200
    assert "s3bucket" in response.data.get("data")["codename"]


def test_permission_delete(api_client_fixt, create_permission_fixt):
    permission_id = create_permission_fixt.data.get("data").get("pk")

    response = api_client_fixt.delete(
        f"/api/roles/v1/permission/{permission_id}",
        headers={
            "Authorization": create_permission_fixt.request.get("HTTP_AUTHORIZATION"),
            "X-AUTHENTICATED-USERNAME": create_permission_fixt.request.get(
                "HTTP_X_AUTHENTICATED_USERNAME"
            ),
        },
    )
    assert response.status_code == 204


@pytest.fixture
def create_role_fixt(super_user_fixt, superuser_token_api_client_fixt, api_client_fixt):
    return api_client_fixt.post(
        "/api/roles/v1/create",
        data={
            "permissions": ["view_vote", "view_bill", "view_representative"],
            "role_name": "client_api",
            "action": "add",
        },
        headers={
            "Authorization": f"Bearer {superuser_token_api_client_fixt}",
            "X-AUTHENTICATED-USERNAME": super_user_fixt.username,
        },
    )


def test_role_creation(create_role_fixt):
    assert create_role_fixt.status_code == 201


def test_role_filter(create_role_fixt, api_client_fixt):
    response = api_client_fixt.get(
        "/api/roles/v1/filter?items_per_page=10&page=1&role_name=client_api",
        headers={
            "Authorization": create_role_fixt.request.get("HTTP_AUTHORIZATION"),
            "X-AUTHENTICATED-USERNAME": create_role_fixt.request.get(
                "HTTP_X_AUTHENTICATED_USERNAME"
            ),
        },
    )
    assert response.status_code == 200
    assert response.data.get("data")[0]["name"] == "client_api"


def test_role_fetch(create_role_fixt, api_client_fixt):
    id = create_role_fixt.data.get("data").get("id")
    response = api_client_fixt.get(
        f"/api/roles/v1/{id}",
        headers={
            "Authorization": create_role_fixt.request.get("HTTP_AUTHORIZATION"),
            "X-AUTHENTICATED-USERNAME": create_role_fixt.request.get(
                "HTTP_X_AUTHENTICATED_USERNAME"
            ),
        },
    )

    assert response.status_code == 200
    assert response.data.get("data")["name"] == "client_api"


def test_role_delete(create_role_fixt, api_client_fixt):
    id = create_role_fixt.data.get("data").get("id")
    response = api_client_fixt.delete(
        f"/api/roles/v1/{id}",
        headers={
            "Authorization": create_role_fixt.request.get("HTTP_AUTHORIZATION"),
            "X-AUTHENTICATED-USERNAME": create_role_fixt.request.get(
                "HTTP_X_AUTHENTICATED_USERNAME"
            ),
        },
    )

    assert response.status_code == 204
