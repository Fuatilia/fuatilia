import pytest
from datetime import datetime

pytestmark = pytest.mark.django_db


@pytest.fixture
def create_bill(
    representative_fixt,
    api_client_fixt,
    superuser_token_api_client_fixt,
):
    token = superuser_token_api_client_fixt
    return api_client_fixt.post(
        "/api/bills/v1/create",
        {
            "topics_in_the_bill": "financing agriculture,kengen tax",
            "title": "Finance Bill 2024",
            "gazette_no": "1",
            "bill_no": "1",
            "status": "IN_PROGRESS",
            "date_introduced": datetime.date(datetime.now()).isoformat(),
            "sponsored_by": representative_fixt.id,
            "house": "NATIONAL",
        },
        headers={"Authorization": f"Bearer {token}"},
    )


def test_create_bill(create_bill):
    assert create_bill.status_code == 201


def test_bill_filter(api_client_fixt, create_bill):
    response = api_client_fixt.get(
        "/api/bills/v1/filter?items_per_page=10&page=1",
        headers={"Authorization": create_bill.request.get("HTTP_AUTHORIZATION")},
    )

    assert response.status_code == 200
    assert len(response.data.get("data")) > 0


def test_bill_fetch(api_client_fixt, create_bill):
    response = api_client_fixt.get(
        f"/api/bills/v1/{create_bill.data.get('data').get('id')}",
        headers={
            "Authorization": create_bill.request.get("HTTP_AUTHORIZATION"),
            "X-AUTHENTICATED-USERNAME": create_bill.request.get(
                "HTTP_X_AUTHENTICATED_USERNAME"
            ),
        },
    )

    assert response.status_code == 200
    assert len(response.data.get("data")) > 0


def test_bill_delete(api_client_fixt, create_bill):
    response = api_client_fixt.delete(
        f"/api/bills/v1/{create_bill.data.get('data').get('id')}",
        headers={
            "Authorization": create_bill.request.get("HTTP_AUTHORIZATION"),
            "X-AUTHENTICATED-USERNAME": create_bill.request.get(
                "HTTP_X_AUTHENTICATED_USERNAME"
            ),
        },
    )

    assert response.status_code == 204
