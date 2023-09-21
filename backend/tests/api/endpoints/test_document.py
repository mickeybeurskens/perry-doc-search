from perry.api.endpoints.document import *
from tests.conftest import get_mock_secret_key
from tests.api.fixtures import *
from fastapi import status


def get_document_url():
    return "/documents"


@pytest.mark.parametrize(
    "endpoint, method, status_code",
    [
        (get_document_url(), "GET", status.HTTP_401_UNAUTHORIZED),
        (get_document_url(), "POST", status.HTTP_401_UNAUTHORIZED),
        (get_document_url() + "/1", "GET", status.HTTP_401_UNAUTHORIZED),
        (get_document_url() + "/1", "PUT", status.HTTP_401_UNAUTHORIZED),
        (get_document_url() + "/1", "DELETE", status.HTTP_401_UNAUTHORIZED),
    ],
)
def test_endpoints_should_refuse_non_authenticated_users_available(
    test_client, endpoint, method, status_code
):
    response = test_client.request(method, endpoint)
    assert response.status_code == status_code
