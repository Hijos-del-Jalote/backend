import pytest
from fastapi.testclient import TestClient
from pony.orm import db_session
from .api import app
from .router.jugadores import Jugador

DEFAULTURL = "http://localhost:8000/jugadores"

client = TestClient(app)

def test_valid_user():
    response = client.post(f'{DEFAULTURL}/new?uname=usuario')
    assert response.status_code == 201

    with db_session:
        player = Jugador.get(id = response.json()["id"])
        assert player.nombre == "usuario"

def test_invalid_user():
    response = client.post(f'{DEFAULTURL}/new?uname=')
    assert response.status_code == 400
    
    response = client.post(f'{DEFAULTURL}/new?uname=   ')
    assert response.status_code == 400