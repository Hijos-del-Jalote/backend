from fastapi.websockets import *
from typing import List, Dict
from .router.schemas import *
from db.models import *
from db.partidas_session import get_partida

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


    async def handle_data(self, data: str, idPartida: int):
        
        match data:
            case "unir": # or cualquier otro que requiera este json.
                dumper: PartidaResponse = get_partida(idPartida)
                await self.broadcast(dumper.model_dump_json(), idPartida)
            case "finalizar":
                dumper: FinPartidaResponse = fin_partida_respond(idPartida)
                await self.broadcast(dumper.model_dump_json(), idPartida)
            case _:
                print("El resto")

manager = ConnectionManager()
