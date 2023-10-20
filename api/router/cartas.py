from fastapi import APIRouter, HTTPException
from pony.orm import db_session
from db.models import *
from .partidas import fin_partida
from . import efectos_cartas
from api.ws import manager
import json


cartas_router = APIRouter()

@cartas_router.post("/jugar", status_code=200)
async def jugar_carta(id_carta:int, id_objetivo:int | None = None):
    with db_session:
        carta = Carta.get(id=id_carta)
        if carta and carta.jugador:
            if carta.partida.turnoActual != carta.jugador.Posicion : raise HTTPException(status_code=400, detail="No es el turno del jugador que tiene esta carta") 

            partida = carta.partida
            idJugador = carta.jugador.id
            
            defendido = False
            if id_objetivo != None:
                await manager.handle_data(event="jugar carta", idPartida=partida.id, idObjetivo=id_objetivo, idCarta=id_carta, idJugador=idJugador)
                response = await manager.get_from_message_queue(partida.id,id_objetivo)
                response = json.loads(response) #hay que parsear el json
                defendido = response['defendido']
                if defendido: 
                    #Descarto la carta del jugador que se defendio
                    Jugador[id_objetivo].cartas.remove(response['idCarta'])
                    #Devuelvo datos desde la perspectivo del que se defendio, preguntar.
                    await manager.handle_data(event="jugar defensa", idObjetivo=idJugador, idCarta=response['idCarta'], idJugador=id_objetivo)                   
                    
            if not defendido:
                match carta.template_carta.nombre: 
                
                    case "Lanzallamas":
                        efectos_cartas.efecto_lanzallamas(id_objetivo)
                    case "Vigila tus espaldas":
                        efectos_cartas.vigila_tus_espaldas(partida)
                    case "Cambio de lugar":
                        efectos_cartas.cambio_de_lugar(carta.jugador, Jugador[id_objetivo])
                    case "Mas vale que corras":
                        efectos_cartas.mas_vale_que_corras(carta.jugador, Jugador[id_objetivo])
                    case "Puerta trancada":
                        efectos_cartas.puerta_trancada(carta.jugador, Jugador[id_objetivo])

                
                    
            carta.jugador.cartas.remove(carta)
            carta.descartada=True
                

            if partida.sentido:
                for i in range(1, len(partida.jugadores)):
                    pos = (partida.turnoActual+i) % len(partida.jugadores)
                    if Jugador.get(Posicion=pos, partida=partida).isAlive:
                        partida.turnoActual = pos
                        break
            else:
                for i in range(1, len(partida.jugadores)):
                    pos = (partida.turnoActual-i) % len(partida.jugadores)
                    if Jugador.get(Posicion=pos, partida=partida).isAlive:
                        partida.turnoActual = pos
                        break
    
            await manager.handle_data(event="fin_turno_jugar", idPartida=partida.id)                   
            # por ahora aca porque esto marca el fin del turno, desp lo pondre en intercambiar carta
            
            await fin_partida(partida.id, idJugador)

        else:
            raise HTTPException(status_code=400, detail="No existe el id de la carta ó jugador que la tenga")

