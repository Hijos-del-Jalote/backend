from fastapi.testclient import TestClient
from fastapi import status
from api.api import app
from .populate_db import populate_db

client = TestClient(app)

populate_db()


def test_get_partida_valid():
    response = client.get(f'partidas/1')
    assert response.status_code == status.HTTP_200_OK

def test_get_partida_invalid():
    response = client.get(f'partidas/154589')
    assert response.status_code == status.HTTP_404_NOT_FOUND