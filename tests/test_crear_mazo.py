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
        cartas = 34
    elif cant_jugadores == 5:
        cartas = 34
    elif cant_jugadores == 6:
        cartas = 35
    elif cant_jugadores == 7:
        cartas = 59
    elif cant_jugadores == 8:
        cartas = 64
    elif cant_jugadores == 9:
        cartas = 68
    elif cant_jugadores == 10:
        cartas = 68
    elif cant_jugadores == 11:
        cartas = 85
    elif cant_jugadores == 12:
        cartas = 85
    return cartas


def test_crear_mazo():
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
        response = client.put(f"partidas/iniciar?idPartida={partida.id}")
        # verifico que haya la cant de cartas correcta
        with db_session:
            partida = Partida.get(id = partida.id)
            cant_cartas = cant_cartas_por_partida(partida)
            assert len(partida.cartas) == cant_cartas
            templates = list(TemplateCarta.select())
            assert templates[0].nombre == "Lanzallamas" and templates[0].tipo == Tipo_Carta.accion and templates[0].descripcion == "matar a un jugador"
            assert templates[1].nombre == "Carta Vacia" and templates[1].tipo == Tipo_Carta.accion and templates[1].descripcion == "Esta Carta No Hace Nada"
            cartas = list(Carta.select())
            for j in range (len(cartas)):
                assert cartas[j].template_carta == templates[0] or cartas[j].template_carta == templates[1]
                