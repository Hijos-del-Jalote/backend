from fastapi.websockets import *
from typing import List, Dict


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int,List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, idPartida: int):
        await websocket.accept()
        if idPartida in self.active_connections:
            self.active_connections[idPartida].append(websocket)
        else:
            self.active_connections[idPartida] = [websocket]

    def disconnect(self, websocket: WebSocket, idPartida: int):
            self.active_connections[idPartida].remove(websocket)

    async def broadcast(self, idPartida: int, data: str):
        if idPartida in self.active_connections:
            for connection in self.active_connections.get(idPartida):
                await connection.send_json(data)
        else:
            print("no hay partiditas en connections :c")
manager = ConnectionManager()
    