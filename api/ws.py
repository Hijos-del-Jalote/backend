from fastapi.websockets import *
from typing import List, Dict
from .router.schemas import *
from db.models import *
from db.partidas_session import get_partida, fin_partida_respond, get_jugadores_partida
from db.jugadores_session import get_abandonarlobby_data
import json
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Dict[int, WebSocket]] = {}
        self.message_queues: Dict[int, Dict[int, asyncio.Queue]] = {}

    async def connect(self, websocket: WebSocket, idPartida: int, idJugador: int):
        await websocket.accept()
        print("user connected")
        if idPartida not in self.active_connections:
            self.active_connections[idPartida] = {}
            self.message_queues[idPartida] = {}

        self.active_connections[idPartida][idJugador] = websocket
        self.message_queues[idPartida][idJugador] = asyncio.Queue()

    async def disconnect(self, idPartida: int, idJugador: int):
        if idPartida in self.active_connections and idJugador in self.active_connections[idPartida]:
            del self.active_connections[idPartida][idJugador]
            del self.message_queues[idPartida][idJugador]

    async def broadcast(self, data: str, idPartida: int):
        if idPartida in self.active_connections:
            for id, websocket in self.active_connections[idPartida].items():
                print(f'broadcasting to {id}')
                await websocket.send_json(data)

    
    async def await_response(self, idPartida: int, idJugador: int):
        #NO USAR ESTA FUNCION, usar get_from_message_queue
        data = await self.active_connections[idPartida][idJugador].receive_text()
        return data
    
    async def personal_msg(self, msg: Dict, idPartida: int, idJugador: int):
        if idPartida in self.active_connections and idJugador in self.active_connections[idPartida]:
            await self.active_connections[idPartida][idJugador].send_json(msg)

    # Método para poner datos en la cola
    async def put_in_message_queue(self, idPartida: int, idJugador: int, data: str):
        if idPartida in self.message_queues and idJugador in self.message_queues[idPartida]:
            await self.message_queues[idPartida][idJugador].put(data)

    # Método para obtener datos de la cola
    async def get_from_message_queue(self, idPartida: int, idJugador: int):
        if idPartida in self.message_queues and idJugador in self.message_queues[idPartida]:
            # while True:
            #     try:
            #         data = await asyncio.wait_for(self.message_queues[idPartida][idJugador].get(),timeout=0.5)
            #         return data
            #     except Exception:
            #         pass

            # esto de abajo asi tal cual anda en simulación a mano, pero se tilda en el test (quizás por el multi threading) 
            return await self.message_queues[idPartida][idJugador].get()



    async def handle_data(self, event: str, idPartida: int, idJugador = -1, winners = [], winning_team = "", idObjetivo = -1, idCarta = -1, msg=""):

        
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
                data = build_dict("jugar_carta", JugarCartaData(idObjetivo=idObjetivo, idCarta=idCarta, idJugador=idJugador).model_dump_json())
                await self.broadcast(data, idPartida)
            case "jugar defensa":
                data = build_dict("jugar_resp", JugarCartaData(idObjetivo=idObjetivo, idCarta=idCarta, idJugador=idJugador).model_dump_json())
                await self.broadcast(data, idPartida)
            case "defensa erronea":
                data = build_dict("defensa_erronea", msg)
                await self.personal_msg(data, idPartida, idJugador)
            case "fin turno jugar":
                data = build_dict("fin_turno_jugar", get_partida(idPartida).model_dump_json())
                await self.broadcast(data, idPartida)
                print("se envio el turno jugar")

            case _:
                print("El resto")

manager = ConnectionManager()


def build_dict(event: str,data):
    return {"event": event,
            "data": data}
