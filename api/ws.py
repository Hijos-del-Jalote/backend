from fastapi.websockets import *
from typing import List, Dict
from .router.partidas import partidas_router


active_connections: Dict[int,List[WebSocket]] = {}

async def connect(websocket: WebSocket, idPartida: int):
    await websocket.accept()
    if idPartida in active_connections:
        active_connections[idPartida].append(websocket)
    else:
        active_connections[idPartida] = [websocket]

def disconnect(websocket: WebSocket, idPartida: int):
        active_connections[idPartida].remove(websocket)



@partidas_router.websocket("/{id}/ws")
async def websocket_endpoint(websocket: WebSocket, id: int):
    await connect(websocket, id)
    