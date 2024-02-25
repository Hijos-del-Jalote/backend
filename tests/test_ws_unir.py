import pytest
import httpx
from db.partidas_session import get_partida
from api.api import app
from fastapi.testclient import TestClient
from pony.orm import db_session
from db.models import Jugador,Partida
from tests.test_newplayer import random_user
from api.ws import manager
from .conftest import *
import asyncio
from unittest.mock import patch
import json
import datetime


async def test_unir_jugador_ws(setup_db_before_test):
    client1 = TestClient(app)

    response = client1.post(f'jugadores?nombre=WinterIsComing')
    response1 = client1.post(f'jugadores?nombre=FireAndBlood')
    
    with client1.websocket_connect(f"ws://localhost:8000/partidas/2/ws?idJugador={response1.json()['id']}") as websocket:
        with client1.websocket_connect(f"ws://localhost:8000/partidas/2/ws/chat?idJugador={response1.json()['id']}") as wschat:

            while len(manager.active_connections.get(2, {})) != 1:
                await asyncio.sleep(0.1)

            assert len(manager.active_connections[2]) == 1

            with patch("db.utils.obtener_tiempo_actual") as mock_time:
                mock_time.return_value = "00:00"
                client1.post(f'partidas/unir?idPartida=2&idJugador={response.json()["id"]}')

            # Esperar la respuesta del websocket en el cliente1:
            response = websocket.receive_json()
            assert response == {"event": "unir", "data": get_partida(2).model_dump_json()}

            logmsg = wschat.receive_json()
            assert logmsg == {'event':"chat_msg",'data':{'isLog':True,'player': None,'msg':'WinterIsComing se unió al lobby','time':"00:00"}}


async def test_iniciar_partida_ws(cleanup_db_after_test):
    client1 = TestClient(app)
    client2 = TestClient(app)

    response = client1.post(f'jugadores?nombre=FireAndBlood')
    
    partida = 2
    
    with client1.websocket_connect(f"ws://localhost:8000/partidas/2/ws?idJugador={response.json()['id']}") as websocket:
        while len(manager.active_connections.get(2, {})) != 1:
            await asyncio.sleep(0.1)
        assert len(manager.active_connections[2]) == 1

        # mandar un post con otro cliente:

        response = client2.put(f"partidas/iniciar/{partida}?idJugador={5}")
        assert response.json() == {"detail": "Partida iniciada con exito"}

        # Esperar la respuesta del websocket en el cliente1:
        response = websocket.receive_json()

        assert response == {"event": "iniciar", "data": "null"}


