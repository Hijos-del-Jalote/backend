from fastapi.testclient import TestClient
from fastapi import status
from api.api import app

client = TestClient(app)


def test_get_partida_valid():
    response = client.get('partidas/1')
    assert response.status_code == status.HTTP_200_OK

def test_get_partida_invalid():
    response = client.get('partidas/154589')
    assert response.status_code == status.HTTP_404_NOT_FOUND