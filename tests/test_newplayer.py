import pytest
from fastapi.testclient import TestClient
from pony.orm import db_session
from api.api import app
from api.router.jugadores import Jugador
import random
import string


client = TestClient(app)

def random_user() -> str:
    length = 10
    random_string = ''.join(random.choice(string.ascii_letters + string.digits)for _ in range(length))
    return random_string

def test_valid_user():
    username = random_user()
    response = client.post(f'jugadores?nombre={username}')
    assert response.status_code == 201

    with db_session:
        player = Jugador.get(id = response.json()["id"])
        assert player.nombre == username

def test_invalid_user(cleanup_db_after_test):
    response = client.post('jugadores?nombre=')
    assert response.status_code == 400
    
    response = client.post('jugadores?nombre=   ')
    assert response.status_code == 400
