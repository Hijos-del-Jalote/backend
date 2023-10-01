from fastapi.testclient import TestClient
from fastapi import status
from pony.orm import db_session
from api.api import app
from api.router.partidas import PartidaIn, PartidaOut

from db.models import Partida, db, Jugador

from tests.test_newplayer import random_user

client = TestClient(app)

def test_finalizar_partida():
    
    jugadores = []
    for i in range(4):
        username = random_user()
        response = client.post(f'jugadores?nombre={username}')
        with db_session:
            jugadores.append(Jugador.get(id = response.json()["id"]))
    
    partida = random_user()
    host = jugadores[0]

    # creo partida
    response = client.post(f'partidas/?nombrePartida={partida}&idHost={host.id}') 

    with db_session:
        partida = Partida.get(id = response.json()["idPartida"])

    # uno jugadores a partida
    for i in range(1,4):
        client.post(f"partidas/unir?idPartida={partida.id}&idJugador={jugadores[i].id}")
    
    # partida correcta
    response = client.put(f"partidas/iniciar?idPartida={partida.id}")

    with db_session:
        partida = Partida.get(id = partida.id)
        
        # hago una simulacion de juego
        for jugador in partida.jugadores:
            jugador.isAlive = False
            ultimojugador = jugador
        
        ultimojugador.isAlive = True

    # partida finalizada
    response = client.get(f"partidas/{id}/estado?idPartida={partida.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["finalizada"] == True
    assert response.json()["idGanador"] == ultimojugador.id

    # partida no finalizada
    with db_session:
        partida = Partida.get(id = partida.id)
        
        # hago una simulacion de juego
        for jugador in partida.jugadores:
            jugador.isAlive = True

    response = client.get(f"partidas/{id}/estado?idPartida={partida.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["finalizada"] == False

    # partida no existente
    response = client.get(f"partidas/{id}/estado?idPartida=1234")
    assert response.status_code == status.HTTP_404_NOT_FOUND

    