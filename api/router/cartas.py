from fastapi import APIRouter, HTTPException, status
from pony.orm import db_session
from db.models import *
from .partidas import fin_partida
from . import efectos_cartas
from api.ws import manager
import json
from db.cartas_session import *
from db.jugadores_session import es_siguiente

cartas_router = APIRouter()

@cartas_router.post("/jugar", status_code=200)
async def jugar_carta(id_carta:int, id_objetivo:int | None = None, test=False):
    with db_session:
        carta = Carta.get(id=id_carta)
        
        if carta and carta.jugador:
            jugador = carta.jugador
            if carta.partida.turnoActual != jugador.id : raise HTTPException(status_code=400, detail="No es el turno del jugador que tiene esta carta") 
            partida = carta.partida
            idJugador = jugador.id
            defendido = False
            if id_objetivo != None and not test:
                objetivo = Jugador[id_objetivo]
                
                if ((efectos_cartas.son_adyacentes(jugador, objetivo)[1] in [0,2]) & (jugador.blockIzq or objetivo.blockDer)) or ((efectos_cartas.son_adyacentes(jugador, objetivo)[1] == 1) & (jugador.blockDer or objetivo.blockIzq)):
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Hay una puerta trancada entre los jugadores")
                    
                await manager.handle_data(event="jugar carta", idPartida=partida.id, idObjetivo=id_objetivo, idCarta=id_carta, idJugador=idJugador, template_carta=carta.template_carta.nombre, nombreJugador=Jugador[idJugador].nombre, nombreObjetivo=Jugador[id_objetivo].nombre)
                
                
                
                response = await manager.get_from_message_queue(partida.id,id_objetivo)
                response = json.loads(response) #hay que parsear el json
                defendido = response['defendido']
                print(f"Llego response: {response}")
                if defendido:
                    #Descarto la carta del jugador que se defendio
                    cartaElim = Carta.get(id=response['idCarta'])
                    Jugador[id_objetivo].cartas.remove(cartaElim)
                    commit()
                    robar_carta(id_objetivo)
                    
                    #Devuelvo datos desde la perspectivo del que se defendio.
                    await manager.handle_data(event="jugar defensa",idPartida=partida.id, idObjetivo=idJugador, idCarta=response['idCarta'], idJugador=id_objetivo, template_carta=Carta[response['idCarta']].template_carta.nombre, nombreJugador=Jugador[id_objetivo].nombre, nombreObjetivo=Jugador[idJugador].nombre)                
                    
                    
            if not defendido:
                match carta.template_carta.nombre: 
                
                    case "Lanzallamas":
                        efectos_cartas.efecto_lanzallamas(id_objetivo)
                        await fin_partida(partida.id, idJugador)
                    case "Vigila tus espaldas":
                        efectos_cartas.vigila_tus_espaldas(partida)
                    case "Cambio de lugar":
                        efectos_cartas.cambio_de_lugar(jugador, Jugador[id_objetivo])
                    case "Mas vale que corras":
                        efectos_cartas.mas_vale_que_corras(jugador, Jugador[id_objetivo])
                    case "Puerta trancada":
                        efectos_cartas.puerta_trancada(jugador, Jugador[id_objetivo])
                    case "Analisis":
                        manager.handle_data("analisis",partida.id,idJugador,idObjetivo=id_objetivo)
                    case "Sospecha":
                        await efectos_cartas.sospecha(partida.id, id_objetivo, idJugador)
                        
            partida.ultimaJugada = carta.template_carta.nombre        
            if(jugador.isAlive):
                jugador.cartas.remove(carta)

            carta.descartada=True
                

            
    
            await manager.handle_data(event="fin turno jugar", idPartida=partida.id)                   
            # por ahora aca porque esto marca el fin del turno, desp lo pondre en intercambiar carta
            

        else:
            raise HTTPException(status_code=400, detail="No existe el id de la carta ó jugador que la tenga")


@cartas_router.put(path="/{idCarta}/intercambiar")
async def intercambiar_cartas_put(idCarta: int, idObjetivo:int):

    with db_session:
        carta: Carta = Carta.get(id=idCarta)
        jugObj: Jugador = Jugador.get(id=idObjetivo)
        jugador = Jugador.get(id=carta.jugador.id)
        partida = jugador.partida
        commit()
        if carta and jugObj:
            if not jugador:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="No puede intercambiar una carta del mazo")
            else:
                # checkear primeras instancias que solo involucran al jugador que inicia el intercambio
                # (esto es así para no avisar al otro jugador de un intercambio a menos que este sea válido)

                if carta.template_carta.nombre == "Infectado" and not puede_intercambiar_infectado(jugador,jugObj): 
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Jugador 1 no puede intercambiar una carta de infectado")

                if (partida.ultimaJugada != "Seduccion") & (not es_siguiente(jugador,jugObj)):
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Sólo puede intercambiar con el siguiente jugador")
                
                if (partida.ultimaJugada == "Seduccion") & jugObj.cuarentena:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="No se puede intercambiar con un jugador en cuarentena")

                if ((efectos_cartas.son_adyacentes(jugador, jugObj)[1] in [0,2]) & (jugador.blockIzq or jugObj.blockDer)) or ((efectos_cartas.son_adyacentes(jugador, jugObj)[1] == 1) & (jugador.blockDer or jugObj.blockIzq)):
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Hay una puerta trancada entre los jugadores")

                response = await manager.handle_data("intercambiar", carta.partida.id, jugador.id,
                                                     idCarta=idCarta, idObjetivo=idObjetivo)
                
                if response['aceptado']:
                    jo_carta: Carta = Carta.get(id=response['data'])    
                    
                    corroborar_infección(jugador,jugObj,carta,jo_carta)
                    
                    intercambiar_cartas(idCarta, response['data'])
                    await manager.broadcast({'event': "intercambio exitoso"}, carta.partida.id)

                else:
                    await manager.broadcast({'event': "intercambio rechazado"}, carta.partida.id)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Carta o jugador no encontrados")

        partida.ultimaJugada = ""
        
        pos_actual = Jugador[partida.turnoActual].Posicion
        if partida.sentido:
            partida.turnoActual = Jugador.get(Posicion=(pos_actual+1)%partida.cantidadVivos, partida=partida).id
        else:
            partida.turnoActual = Jugador.get(Posicion=(pos_actual-1)%partida.cantidadVivos, partida=partida).id   
                     
        commit()         
    await manager.handle_data("fin_de_turno",carta.partida.id)


@cartas_router.put("/descartar_carta/{idCarta}", status_code=200)
def descartar_carta_put(idCarta: int):
    descartar_carta(idCarta)
