from fastapi.websockets import *
from typing import List, Dict
from .router.schemas import *
from db.models import *
from db.partidas_session import get_partida, fin_partida_respond, get_jugadores_partida
from db.jugadores_session import get_abandonarlobby_data
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Dict[int,WebSocket]] = {}

    async def connect(self, websocket: WebSocket, idPartida: int, idJugador: int): 
        await websocket.accept()

        if idPartida not in self.active_connections:
            self.active_connections[idPartida] = {}

        self.active_connections[idPartida][idJugador] = websocket


    async def disconnect(self, idPartida: int, idJugador: int):
        if idPartida in self.active_connections and idJugador in self.active_connections[idPartida]:
            del self.active_connections[idPartida][idJugador]


    async def broadcast(self, data: str, idPartida: int):
        if idPartida in self.active_connections:
            for id, websocket in self.active_connections[idPartida].items():
                print(f'broadcasting to {id}')
                await websocket.send_json(data)

    async def await_response(self, idPartida:int, idJugador: int):
        response = None
        if idPartida in self.active_connections:
            for websocket_id, websocket in self.active_connections[idPartida].items():
                if websocket_id == idJugador:
                    response = await websocket.receive_text()
                    break
        return response


    async def handle_data(self, event: str, idPartida: int, idJugador = -1, winners = [], winning_team = "", idObjetivo = -1, idCarta = -1):

        
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
            case "finalizar":
                data = build_dict("finalizar", fin_partida_respond(idPartida, winners, winning_team).model_dump_json())
                await self.broadcast(data, idPartida)
            case "jugar carta":
                data = build_dict("jugar_carta", JugarCartaData(idObjetivo, idCarta, idJugador).model_dump_json())
                await self.broadcast(data, idPartida)
            case "jugar defensa":
                data = build_dict("jugar_resp", JugarCartaData(idObjetivo, idCarta, idJugador).model_dump_json())
                await self.broadcast(data, idPartida)
            case "fin turno jugar":
                data = build_dict("fin_turno_jugar", json.dumps({"Partida" : getPartida(idPartida).model_dump_json(), "Jugadores" : get_jugadores_partida(idPartida).model_dump_json()}, 4))
                await self.broadcast(data, idPartida)
            case _:
                print("El resto")

manager = ConnectionManager()


def build_dict(event: str,data):
    return {"event": event,
            "data": data}
