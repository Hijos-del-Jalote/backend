from fastapi.testclient import TestClient
from fastapi import status

from api.api import app
from api.router.partidas import PartidaIn, PartidaOut


client = TestClient(app)


def test_crear_partida():

    response = client.post(f'partidas/?nombrePartida=pruba')

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() != {
        'id': None
        }

    response = client.post(f'partidas/?nombrePartida=')

    assert response.status_code == status.HTTP_400_BAD_REQUEST