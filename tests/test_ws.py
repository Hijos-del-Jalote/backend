from fastapi.testclient import TestClient
from fastapi import status, WebSocket
from pony.orm import db_session
from api.api import app
from api.router.partidas import *
from api.router.schemas import PartidaResponse
from api.ws import *
import asyncio

import json

async def test_websocket(cleanup_db_after_test):
    client = TestClient(app)
    response = client.post(f'jugadores?nombre=Nachito')
    with client.websocket_connect(f"/partidas/1/ws?idJugador={response.json()['id']}") as websocket:
        while len(manager.active_connections.get(1, {})) != 1:
            await asyncio.sleep(0.1)
        assert len(manager.active_connections[1]) == 1