from fastapi import APIRouter, HTTPException, status
from pony.orm import db_session
from db.models import *
from .partidas import fin_partida
from . import efectos_cartas
from ..ws import manager
import json
from db.cartas_session import intercambiar_cartas

cartas_router = APIRouter()

@cartas_router.post("/jugar", status_code=200)
async def jugar_carta(id_carta:int, id_objetivo:int | None = None):
    with db_session:
        carta = Carta.get(id=id_carta)
        if carta and carta.jugador:
            if carta.partida.turnoActual != carta.jugador.Posicion : raise HTTPException(status_code=400, detail="No es el turno del jugador que tiene esta carta") 

            partida = carta.partida
            idJugador = carta.jugador.id
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
            
            # por ahora aca porque esto marca el fin del turno, desp lo pondre en intercambiar carta
            
            await fin_partida(partida.id, idJugador)

        else:
            raise HTTPException(status_code=400, detail="No existe el id de la carta ó jugador que la tenga")


@cartas_router.put(path="/{idCarta}/intercambiar")
async def intercambiar_cartas_put(idCarta: int, idObjetivo:int):

    with db_session:
        carta: Carta = Carta.get(id=idCarta)
        jugObj: Jugador = Jugador.get(id=idObjetivo)
        jugador = Jugador.get(id=carta.jugador.id)

        if carta and jugObj:
            if not jugador:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="No puede intercambiar una carta del mazo")
            else:
                response = await manager.handle_data("intercambiar", carta.partida.id, jugador.id,
                                                     idCarta=idCarta, idJugador2=idObjetivo)
                
                if response['aceptado']:
                    jo_carta: Carta = Carta.get(id=response['data'])
                    
                    if carta.template_carta.nombre == "Infectado":
                        jugObj.Rol = Rol.infectado

                    if jo_carta.template_carta == "Infectado":
                        jugador.Rol = Rol.infectado

                    intercambiar_cartas(idCarta, response['data'])
                    await manager.broadcast({'event': "intercambio exitoso"}, carta.partida.id)

                else:
                    await manager.broadcast({'event': "intercambio rechazado"}, carta.partida.id)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Carta o jugador no encontrados")
        
    await manager.handle_data("fin_de_turno",carta.partida.id)