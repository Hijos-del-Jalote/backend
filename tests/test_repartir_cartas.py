from fastapi.testclient import TestClient
from fastapi import status
from pony.orm import db_session
from api.api import app
from api.router.partidas import *
from db.models import *
from tests.test_newplayer import random_user
from db.mazo_session import *
from db.cartas_session import *

client = TestClient(app)


def test_repartir_cartas(cleanup_db_after_test):
    for i in range (4,12):
        jugadores = []
        for j in range(i):
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
        for i in range(1,i):
            client.post(f"partidas/unir?idPartida={partida.id}&idJugador={jugadores[i].id}")
        # inicio  partida
        response = client.put(f"partidas/iniciar/{partida.id}?idJugador={host.id}")  
        # verifico que haya la cant de cartas correcta
        with db_session:
            partida = Partida.get(id = partida.id)
            for j in partida.jugadores:
                assert len(j.cartas) == 4
           