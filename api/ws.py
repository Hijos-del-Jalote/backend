from fastapi.websockets import *
from typing import List, Dict
from .router.schemas import *
from db.models import *
from db.partidas_session import get_partida
from db.jugadores_session import get_abandonarlobby_data

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, idPartida: int): 
        await websocket.accept()
        
        if idPartida not in self.active_connections:
            self.active_connections[idPartida] = []

        self.active_connections[idPartida].append(websocket)
        

    def disconnect(self, websocket: WebSocket, idPartida: int):
        if idPartida in self.active_connections:
            self.active_connections[idPartida].remove(websocket)

    async def broadcast(self, data: str, idPartida: int):
        if idPartida in self.active_connections:
            for connection in self.active_connections[idPartida]:
                print(f'broadcasting to {connection}')
                await connection.send_json(data)



    async def handle_data(self, event: str, idPartida: int, idJugador = -1):
        
        match event:
            case "unir": # or cualquier otro que requiera este json.
                data = build_dict("unir",get_partida(idPartida).model_dump_json())
                await self.broadcast(data, idPartida)
            case "iniciar":
                data = build_dict("iniciar","null")
                await self.broadcast(data, idPartida)
            case "abandonar lobby":
                data = build_dict("abandonar lobby",get_abandonarlobby_data(idJugador, idPartida))
                await self.broadcast(data,idPartida)
            case _:
                print("El resto")

manager = ConnectionManager()


def build_dict(event: str,data):
    return {"event": event,
            "data": data}