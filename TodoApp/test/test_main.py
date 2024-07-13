from fastapi.testclient import TestClient
from starlette import status
from ..main import app

client = TestClient(app)


def test_app_heath():
    response = client.get("/health")
    assert response.status_code == status.HTTP_204_NO_CONTENT
