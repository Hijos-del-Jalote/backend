from fastapi.testclient import TestClient
from fastapi import status, WebSocket
from pony.orm import db_session
from api.api import app
from api.router.partidas import *
from api.router.schemas import PartidaResponse
from api.ws import *


import json

def test_websocket():
    client = TestClient(app)
    
    with client.websocket_connect("/partidas/1/ws") as websocket:
        assert len(manager.active_connections[1]) == 1
#         dumper: PartidaResponse = test_partida(1)
#         manager.broadcast(dumper.model_dump_json(), idPartida=1)
#      # [-1] se refiere al ultimo elemento del array.
#         assert websocket.messages[-1]["text"] == dumper.model_jump_json()

# # def test_connect_disconnect():
#     manager = ConnectionManager()
#     client = TestClient(app)
#     with client.websocket_connect("/1/ws") as websocket:
#         data = websocket.receive_json()
#         assert data == data


# @pytest.mark.asyncio
# async def test_broadcast():
#     manager = ConnectionManager()

#     j1 = WebSocket()
#     j2 = WebSocket()

#     await manager.connect(j1, idPartida=1)
#     await manager.connect(j2, idPartida=1)

#     dumper: PartidaResponse = test_partida(idPartida)
#     await manager.broadcast(dumper.model_dump_json(), idPartida=1)
#     # [-1] se refiere al ultimo elemento del array.
#     assert j1.messages[-1]["text"] == dumper.model_jump_json()
#     assert j2.messages[-1]["text"] == dumper.model_jump_json()

#     # pip install pytest-asyncio