from fastapi.testclient import TestClient
from fastapi import status

from api.api import app
from api.router.partidas import *


client = TestClient(app)


def test_unir_jugador():

    existen_response = client.post("partidas/unir?idPartida=1&idJugador=1")

    assert existen_response.status_code == 200
    
    no_jugador_response = client.post("partidas/unir?idPartida=1&idJugador=100")

    assert no_jugador_response.status_code == 400

    no_partida_response = client.post("partidas/unir?idPartida=100&idJugador=1")

    assert no_partida_response.status_code == 400