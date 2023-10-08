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
        self.active_connections: List[WebSocket] = [] # esto me guarda todas las conexiones juntas, habría que separarlas por partidas

    async def connect(self, websocket: WebSocket): 
        await websocket.accept()
        
        self.active_connections.append(websocket)
        

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, data: str):
        for connection in self.active_connections:
            print(f'broadcasting to {connection}')
            await connection.send_json(data)

        

    async def handle_data(self, data: str, idPartida: int):
        # acá iría un match case con los posibles casos, por ahora solo esta lo necesario para el lobby
        dumper: PartidaResponse = test_partida(idPartida) 
        await self.broadcast(dumper.model_dump_json())



manager = ConnectionManager()
    