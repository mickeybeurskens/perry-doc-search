import pytest
from tests.api.fixtures import test_client
from perry.api.app import AGENTS_URL


@pytest.mark.parametrize(
    "endpoint, method, status_code",
    [
        (AGENTS_URL + "/info", "GET", 401),
    ],
)
def test_endpoint_returns_401_if_not_logged_in(
    test_client, endpoint, method, status_code
):
    response = test_client.get(AGENTS_URL + "/info")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
