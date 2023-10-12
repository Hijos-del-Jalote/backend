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


def cant_cartas_por_partida(partida):
    cant_jugadores = len(partida.jugadores)
    if cant_jugadores == 4:
        cartas = 35
    elif cant_jugadores == 5:
        cartas = 41
    elif cant_jugadores == 6:
        cartas = 54
    elif cant_jugadores == 7:
        cartas = 63
    elif cant_jugadores == 8:
        cartas =69
    elif cant_jugadores == 9:
        cartas = 88
    elif cant_jugadores == 10:
        cartas = 95
    elif cant_jugadores == 11:
        cartas = 108
    elif cant_jugadores == 12:
        cartas = 108
    return cartas

def test_crear_mazo(cleanup_db_after_test):
    for i in range (4,13):
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
        response = client.put(f"partidas/iniciar?idPartida={partida.id}")
        # verifico que haya la cant de cartas correcta
        with db_session:
            partida = Partida.get(id = partida.id)
            cant_cartas = cant_cartas_por_partida(partida)
            assert len(partida.cartas) == cant_cartas
            

