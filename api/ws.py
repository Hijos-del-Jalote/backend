from fastapi.websockets import *
from typing import List, Dict
from .router.schemas import *
from pony.orm import db_session
from db.models import *

def test_partida(id: int) -> PartidaResponse:
    with db_session:
        partida = Partida.get(id=id)

        jugadores_list = sorted([{"id": j.id,
                                  "nombre": j.nombre,
                                  "posicion": j.Posicion,
                                  "isAlive": j.isAlive} for j in partida.jugadores], key=lambda j: j['id'])
        
        partidaResp = PartidaResponse(nombre=partida.nombre,
                                      maxJugadores=partida.maxJug,
                                      minJugadores=partida.minJug,
                                      iniciada=partida.iniciada,
                                      turnoActual=partida.turnoActual,
                                      sentido=partida.sentido,
                                      jugadores=jugadores_list)

    return partidaResp

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
                dumper: PartidaResponse = test_partida(idPartida)
                await self.broadcast(dumper.model_dump_json(), idPartida)
            case _:
                print("El resto")

manager = ConnectionManager()
    