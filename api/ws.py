from fastapi.websockets import *
from typing import List, Dict
from .router.schemas import *
from db.models import *

from db.partidas_session import get_partida, fin_partida_respond
from db.jugadores_session import get_abandonarlobby_data
from db.cartas_session import carta_data
import time
from websockets import exceptions
import asyncio
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Dict[int, WebSocket]] = {}
        self.message_queues: Dict[int, Dict[int, asyncio.Queue]] = {}

    async def connect(self, websocket: WebSocket, idPartida: int, idJugador: int):
        await websocket.accept()

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
            while True:
                try:
                    data = await asyncio.wait_for(self.message_queues[idPartida][idJugador].get(),timeout=0.5)
                    return data
                except Exception:
                    pass



    async def handle_data(self, event: str, idPartida: int, idJugador = -1, winners = [],
                           winning_team = "", idCarta = 0, idJugador2 = 0):

        
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
            case "intercambiar":
                # mando al jugador objetivo los datos de la carta
                data = build_dict("intercambio_request", carta_data(idCarta))
                await self.personal_msg(data,idPartida,idJugador2)

                # aviso a los clientes que se está llevando a cabo un intercambio
                data2 = build_dict("intercambio", {'idJugador1': idJugador,
                                                   'idJugador2': idJugador2})
                await self.broadcast(data2, idPartida)
                
                #espero respuesta del jugador objetivo
                response = await self.get_from_message_queue(idPartida, idJugador2)
                json_data = json.loads(response)
                return json_data
            
            case "fin_de_turno": # si aca devolvemos la partida entera se podria unir en un solo evento con "unir"
                data = build_dict("fin_de_turno", get_partida(idPartida).model_dump_json())
                await self.broadcast(data, idPartida)
            case _:
                print("El resto")

manager = ConnectionManager()


def build_dict(event: str,data):
    return {"event": event,
            "data": data}