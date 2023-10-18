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

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Dict[int,WebSocket]] = {}
        self.semaphores: Dict[int, Dict[int,asyncio.Semaphore]] = {}
    async def connect(self, websocket: WebSocket, idPartida: int, idJugador: int): 
        await websocket.accept()

        if idPartida not in self.active_connections:
            self.active_connections[idPartida] = {}
            self.semaphores[idPartida] = {}


        self.active_connections[idPartida][idJugador] = websocket
        self.semaphores[idPartida][idJugador] = asyncio.Semaphore(1)
        await self.semaphores[idPartida][idJugador].acquire()
        print(f"SEMA{self.semaphores[idPartida][idJugador]}")


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
        print("ACA??")
        data = await self.active_connections[idPartida][idJugador].receive_text()
        return data
    
    async def personal_msg(self, msg: Dict, idPartida: int, idJugador: int):
        if idPartida in self.active_connections and idJugador in self.active_connections[idPartida]:
            print(f'JUGADORpms: {idJugador}, {self.active_connections[idPartida][idJugador]}')
            await self.active_connections[idPartida][idJugador].send_json(msg)


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
                print("aqui1")

                # aviso a los clientes que se está llevando a cabo un intercambio
                data2 = build_dict("intercambio", {'idJugador1': idJugador,
                                                   'idJugador2': idJugador2})
                await self.broadcast(data2, idPartida)
                print("aqui2")
                
                #espero respuesta del jugador objetivo
                response = await self.await_response(idPartida,idJugador2)
                print("aqui3")
                return response
            
            case "fin_de_turno": # si aca devolvemos la partida entera se podria unir en un solo evento con "unir"
                data = build_dict("fin_de_turno", get_partida(idPartida).model_dump_json())
                await self.broadcast(data, idPartida)
            case _:
                print("El resto")

manager = ConnectionManager()


def build_dict(event: str,data):
    return {"event": event,
            "data": data}