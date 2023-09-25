from fastapi.testclient import TestClient
from fastapi import status
from pony.orm import db_session
from api.api import app
from api.router.partidas import PartidaIn, PartidaOut

from db.models import Partida, db, Jugador

from tests.test_newplayer import random_user

client = TestClient(app)


def test_crear_partida():
    # parte parecida a test_newplayer pero necesito el idHost
    username = random_user()
    response = client.post(f'jugadores?nombre={username}')
    assert response.status_code == 201

    with db_session:
        host = Jugador.get(id = response.json()["id"])
        assert host.nombre == username
    # hasta aca

    response = client.post(f'partidas/?nombrePartida=pruba&idHost={host.id}')

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() != {
        'id': None
        }

    response = client.post(f'partidas/?nombrePartida=&idHost={host.id}')

    assert response.status_code == status.HTTP_400_BAD_REQUEST