from api.api import app
from fastapi.testclient import TestClient
from pony.orm import db_session
from db.models import Jugador,Partida
from api.ws import manager
from .conftest import *
from db.partidas_session import get_jugadores_partida
import time

client = TestClient(app)

async def test_abandonar_lobby_nohost(setup_db_before_test):
    client1 = TestClient(app)
    client2 = TestClient(app)

    
    with client1.websocket_connect("ws://localhost:8000/partidas/2/ws") as websocket:
        assert len(manager.active_connections[2]) == 1

        # mandar un post con otro cliente: 
        client2.put("jugadores/6/abandonar_lobby")

        # Esperar la respuesta del websocket en el cliente1:
        response = websocket.receive_json()

        assert response == {'event': 'abandonar lobby',
                            'data': {'host': False,
                                     'jugadores': get_jugadores_partida(2)}}
        with db_session:
            assert Jugador[6].partida == None

def test_abandonar_lobby_nojugador():
    response = client.put("jugadores/666/abandonar_lobby")
    assert response.status_code == 400
    assert response.json() == {'detail': 'El jugador no existe'}

def test_abandonar_lobby_nopartida():
    response = client.put("jugadores/6/abandonar_lobby")
    assert response.status_code == 400
    assert response.json() == {'detail': 'El jugador no se encuentra en una partida'}

async def test_abandonar_lobby_host(cleanup_db_after_test):
    client1 = TestClient(app)
    client2 = TestClient(app)

    
    with client1.websocket_connect("ws://localhost:8000/partidas/2/ws") as websocket:
        assert len(manager.active_connections[2]) == 1

        # mandar un post con otro cliente: 
        client2.put("jugadores/5/abandonar_lobby")

        # Esperar la respuesta del websocket en el cliente1:
        response = websocket.receive_json()

        assert response == {'event': 'abandonar lobby',
                            'data': {'host': True,
                                     'jugadores': []}}
        with db_session:
            assert Jugador[5].partida == None