import pytest

pytestmark = pytest.mark.django_db


@pytest.fixture
def create_representative(
    api_client_fixt, super_user_fixt, superuser_token_api_client_fixt
):
    token = superuser_token_api_client_fixt
    return api_client_fixt.post(
        "/api/representatives/v1/create",
        {
            "area_represented": "KENYA",
            "full_name": "Some random name",
            "house": "NATIONAL",
            "position": "MP",
            "position_type": "ELECTED",
            "gender": "M",
            "representation_summary": {},
        },
        format="json",
        headers={
            "Authorization": f"Bearer {token}",
            "X-AUTHENTICATED-USERNAME": super_user_fixt.username,
        },
    )


def test_create_representative(create_representative):
    assert create_representative.status_code == 201


def test_representative_filter(api_client_fixt, create_representative):
    response = api_client_fixt.get(
        "/api/representatives/v1/filter?items_per_page=10&page=1",
        headers={
            "Authorization": create_representative.request.get("HTTP_AUTHORIZATION"),
            "X-AUTHENTICATED-USERNAME": create_representative.request.get(
                "HTTP_X_AUTHENTICATED_USERNAME"
            ),
        },
    )

    assert response.status_code == 200
    assert len(response.data.get("data")) > 0


def test_representative_fetch(api_client_fixt, create_representative):
    response = api_client_fixt.get(
        f"/api/representatives/v1/{create_representative.data.get('data').get('id')}",
        headers={
            "Authorization": create_representative.request.get("HTTP_AUTHORIZATION"),
            "X-AUTHENTICATED-USERNAME": create_representative.request.get(
                "HTTP_X_AUTHENTICATED_USERNAME"
            ),
        },
    )

    assert response.status_code == 200
    assert len(response.data.get("data")) > 0


def test_representative_delete(api_client_fixt, create_representative):
    response = api_client_fixt.delete(
        f"/api/representatives/v1/{create_representative.data.get('data').get('id')}",
        headers={
            "Authorization": create_representative.request.get("HTTP_AUTHORIZATION"),
            "X-AUTHENTICATED-USERNAME": create_representative.request.get(
                "HTTP_X_AUTHENTICATED_USERNAME"
            ),
        },
    )

    assert response.status_code == 204
