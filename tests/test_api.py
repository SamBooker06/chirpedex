from fastapi.testclient import TestClient
from chirpedex.api.server import _app as app

client = TestClient(app)

def test_get_version():
    response = client.get("/version")

    assert response.status_code == 200