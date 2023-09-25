from fastapi.testclient import TestClient
from fastapi import status

from api.api import app
from api.router.partidas import *


client = TestClient(app)


def test_unir_jugador():

    ids_existentes = {"idPartida" : 1, "idJugador" : 1}

    response = client.post("/partidas/unir", json=ids_existentes)

    assert response.status_code == 200
    
    jugador_no_existente = {"idPartida" : 1, "idJugador" : 100}
    response = client.post("/partidas/", json=ids_no_existentes)

    assert response.status_code == 400

    partida_no_existente = {"idPartida" : 100, "idJugador" : 1}

    assert response.status_code == 400
