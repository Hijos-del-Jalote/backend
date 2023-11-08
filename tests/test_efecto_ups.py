from fastapi.testclient import TestClient
from fastapi import status
from pony.orm import db_session
from api.api import app
from api.router.partidas import *
from api.router.cartas import *
from db.models import *
from api.ws import *
import asyncio


async def test_jugar_Ups(cleanup_db_after_test):
    client = TestClient(app)
    crear_datos_partida()
    with client.websocket_connect(f"ws://localhost:8000/partidas/1/ws?idJugador=1") as websocket:
        while len(manager.active_connections.get(1, {})) != 1:
            await asyncio.sleep(0.1)
        assert len(manager.active_connections[1]) == 1
        response = client.post(f'cartas/jugar?id_carta=1') 
        print(response.json())
        assert response.status_code == 200
        response2 = websocket.receive_json()
        assert response2 == {"event": "Ups", "data": ['Lanzallamas', 'Lanzallamas', 'Lanzallamas', 'Lanzallamas', 'Ups']}


def crear_datos_partida():
    with db_session:
        crear_templates_cartas()
        partida = Partida(nombre="partida", iniciada=True, finalizada=False , maxJug=5, minJug=4, turnoActual=1)
        db.commit()
        jugador = Jugador(nombre="Jugador", Rol="Humano", isHost=True, isAlive=True, blockIzq=False, blockDer=False, Posicion=0)
        db.commit()
        Carta(descartada=False, template_carta="Ups", partida=partida, jugador=jugador)
        for i in range(4):
            Carta(descartada=False, template_carta="Lanzallamas" , partida=partida, jugador=jugador)
        db.commit()