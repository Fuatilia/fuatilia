import pytest

pytestmark = pytest.mark.django_db


@pytest.fixture
def create_individual_vote(
    representative_fixt,
    bill_fixt,
    api_client_fixt,
    superuser_token_api_client_fixt,
):
    token = superuser_token_api_client_fixt
    return api_client_fixt.post(
        "/api/votes/v1/create",
        data={
            "vote": "YES",
            "bill_id": bill_fixt.id,
            "representative_id": representative_fixt.id,
            "vote_type": "INDIVIDUAL",
            "house": "NATIONAL",
        },
        headers={"Authorization": f"Bearer {token}"},
    )


def test_create_individual_vote(create_individual_vote):
    assert create_individual_vote.status_code == 201


# Handles both consensus and confidential types ("Group" votes)
@pytest.fixture
def create_consensus_vote(bill_fixt, api_client_fixt, superuser_token_api_client_fixt):
    token = superuser_token_api_client_fixt
    return api_client_fixt.post(
        "/api/votes/v1/create",
        data={
            "bill_id": bill_fixt.id,
            "vote_type": "CONFIDENTIAL",
            "vote_summary": {"YES": 100, "NO": 20, "ABSENT": 30},
            "house": "NATIONAL",
        },
        format="json",
        headers={"Authorization": f"Bearer {token}"},
    )


def test_create_consensus_vote(create_consensus_vote):
    assert create_consensus_vote.status_code == 201
    assert create_consensus_vote.data.get("data").get("vote_type") == "CONFIDENTIAL"


def test_vote_filter(api_client_fixt, create_individual_vote):
    response = api_client_fixt.get(
        "/api/votes/v1/filter?items_per_page=10&page=1",
        headers={
            "Authorization": create_individual_vote.request.get("HTTP_AUTHORIZATION"),
        },
    )

    assert response.status_code == 200
    assert len(response.data.get("data")) > 0


def test_vote_fetch(api_client_fixt, create_individual_vote):
    response = api_client_fixt.get(
        f"/api/votes/v1/{create_individual_vote.data.get('data').get('id')}",
        headers={
            "Authorization": create_individual_vote.request.get("HTTP_AUTHORIZATION"),
            "X-AUTHENTICATED-USERNAME": create_individual_vote.request.get(
                "HTTP_X_AUTHENTICATED_USERNAME"
            ),
        },
    )

    assert response.status_code == 200
    assert len(response.data.get("data")) > 0


def test_vote_delete(api_client_fixt, create_consensus_vote):
    response = api_client_fixt.delete(
        f"/api/votes/v1/{create_consensus_vote.data.get('data').get('id')}",
        headers={
            "Authorization": create_consensus_vote.request.get("HTTP_AUTHORIZATION"),
            "X-AUTHENTICATED-USERNAME": create_consensus_vote.request.get(
                "HTTP_X_AUTHENTICATED_USERNAME"
            ),
        },
    )

    assert response.status_code == 204
