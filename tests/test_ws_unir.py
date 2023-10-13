import pytest
import httpx
from db.partidas_session import get_partida
from api.api import app
from fastapi.testclient import TestClient
from pony.orm import db_session
from db.models import Jugador,Partida
from tests.test_newplayer import random_user
from api.ws import manager


async def test_unir_jugador_ws():
    client1 = TestClient(app)
    client2 = TestClient(app)

    response = client2.post(f'jugadores?nombre=WinterIsComing')
    
    
    with client1.websocket_connect("ws://localhost:8000/partidas/2/ws") as websocket:
        assert len(manager.active_connections[2]) == 1

        # mandar un post con otro cliente: 
        client2.post(f'partidas/unir?idPartida=2&idJugador={response.json()["id"]}')

        # Esperar la respuesta del websocket en el cliente1:
        response = websocket.receive_json()

        assert response == {"event": "unir", "data": get_partida(2).model_dump_json()}

async def test_iniciar_partida_ws():
    client1 = TestClient(app)
    client2 = TestClient(app)
    
    partida = 2

    with client1.websocket_connect("ws://localhost:8000/partidas/2/ws") as websocket:
        assert len(manager.active_connections[2]) == 1

        # mandar un post con otro cliente:

        response = client2.put(f'partidas/iniciar?idPartida={partida}')
        assert response.json() == {"detail": "Partida iniciada con exito"}

        # Esperar la respuesta del websocket en el cliente1:
        response = websocket.receive_json()

        assert response == {"event": "iniciar", "data": "null"}


