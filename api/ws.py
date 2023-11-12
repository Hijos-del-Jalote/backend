from fastapi.websockets import *
from typing import List, Dict
from .router.schemas import *
from db.models import *
from db.partidas_session import get_partida, fin_partida_respond, get_jugadores_partida
from db.jugadores_session import get_abandonarlobby_data
from db.cartas_session import carta_data, get_mano_jugador, puede_intercambiar_infectado
import asyncio
import json

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
            resp = None
            while resp == None:
                resp = await self.message_queues[idPartida][idJugador].get()
            return resp



    async def handle_data(self, event: str, idPartida: int, idJugador = -1, winners = [],
                           winning_team = "", idObjetivo = -1, idCarta = -1, msg="",
                             template_carta="", nombreJugador="", nombreObjetivo=""):

        
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
                await self.personal_msg(data,idPartida,idObjetivo)

                # aviso a los clientes que se está llevando a cabo un intercambio
                data2 = build_dict("intercambio", {'idJugador1': idJugador,
                                                   'idJugador2': idObjetivo})
                await self.broadcast(data2, idPartida)
                
                #espero respuesta del jugador objetivo
                while True:
                    response = await self.get_from_message_queue(idPartida, idObjetivo)
                    json_data = json.loads(response)
                    if json_data['aceptado']:
                        jugador = Jugador.get(id=idJugador)
                        jugObj = Jugador.get(id=idObjetivo)
                        jo_carta: Carta = Carta.get(id=json_data['data'])

                        if jo_carta.template_carta.nombre == "Infectado" and not puede_intercambiar_infectado(jugObj,jugador):
                            await self.personal_msg(build_dict("Intercambio erróneo", "No puedes intercambiar una carta de infectado"),
                                                    idPartida,idObjetivo) 
                        else:
                            break
                    else:
                        break
                return json_data
            
            case "fin_de_turno": # si aca devolvemos la partida entera se podria unir en un solo evento con "unir"
                data = build_dict("fin_de_turno", get_partida(idPartida).model_dump_json())
                await self.broadcast(data, idPartida)
            case "jugar carta":
                data = build_dict("jugar_carta", JugarCartaData(idObjetivo=idObjetivo, idCarta=idCarta, idJugador=idJugador, template_carta=template_carta, nombreJugador=nombreJugador, nombreObjetivo=nombreObjetivo).model_dump_json())
                await self.broadcast(data, idPartida)
            case "jugar defensa":
                data = build_dict("jugar_resp", JugarCartaData(idObjetivo=idObjetivo, idCarta=idCarta, idJugador=idJugador, template_carta=template_carta, nombreJugador=nombreJugador, nombreObjetivo=nombreObjetivo).model_dump_json())
                await self.broadcast(data, idPartida)
            case "fin turno jugar":
                data = build_dict("fin_turno_jugar", get_partida(idPartida).model_dump_json())
                await self.broadcast(data, idPartida)
            case "Analisis":
                data = build_dict("Analisis", get_mano_jugador(idObjetivo))
                await self.personal_msg(data,idPartida,idJugador)
            case "Whisky":
                data = build_dict("Whisky", get_mano_jugador(idJugador))
                await self.broadcast(data,idPartida)
            case "sospecha":
                data = build_dict("sospecha", get_mano_jugador(idObjetivo))
                await self.personal_msg(data, idPartida, idJugador)
            case "Aterrador":
                carta = Carta.get(id=idCarta)
                data = build_dict("Aterrador",carta.template_carta.nombre)
                await self.personal_msg(data, idPartida , idObjetivo)
            case _:
                print("El resto")

manager = ConnectionManager()


def build_dict(event: str,data):
    return {"event": event,
            "data": data}
