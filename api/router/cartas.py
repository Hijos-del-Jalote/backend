from fastapi import APIRouter, HTTPException, status
from pony.orm import db_session
from db.models import *
from .partidas import fin_partida
from . import efectos_cartas
from api.ws import manager, manager_chat
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
            ultimaRobada = Carta.get(id=partida.ultimaRobada)
            commit()

            if  ultimaRobada and ultimaRobada.template_carta.tipo == Tipo_Carta.panico and carta != ultimaRobada:
                raise HTTPException(status_code=400, detail="Debes jugar la carta de pánico levantada")
            

            defendido = False
            if id_objetivo != None and not test:
                objetivo = Jugador[id_objetivo]
                
                if ((efectos_cartas.son_adyacentes(jugador, objetivo)[1] in [0,2]) & (jugador.blockIzq or objetivo.blockDer)) or ((efectos_cartas.son_adyacentes(jugador, objetivo)[1] == 1) & (jugador.blockDer or objetivo.blockIzq)):
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Hay una puerta trancada entre los jugadores")
                    
                await manager.handle_data(event="jugar carta", idPartida=partida.id, idObjetivo=id_objetivo, idCarta=id_carta, idJugador=idJugador, template_carta=carta.template_carta.nombre, nombreJugador=Jugador[idJugador].nombre, nombreObjetivo=Jugador[id_objetivo].nombre)
                
                msg = f'{jugador.nombre} jugó {carta.template_carta.nombre} contra {objetivo.nombre}'
                await manager_chat.handle_data("chat_msg", partida.id, msg=msg, isLog=True)
                
                
                response = await manager.get_from_message_queue(partida.id,id_objetivo)
                response = json.loads(response) #hay que parsear el json
                defendido = response['defendido']
                print(f"Llego response: {response}")
                if defendido:
                    #Descarto la carta del jugador que se defendio
                    cartaElim = Carta.get(id=response['idCarta'])

                    msg = f'{objetivo.nombre} se defendió con {cartaElim.template_carta.nombre}'
                    await manager_chat.handle_data("chat_msg", partida.id, msg=msg, isLog=True)

                    objetivo.cartas.remove(cartaElim)
                    commit()
                    robar_carta(id_objetivo)
                    
                    #Devuelvo datos desde la perspectivo del que se defendio.
                    await manager.handle_data(event="jugar defensa",idPartida=partida.id, idObjetivo=idJugador, idCarta=response['idCarta'], idJugador=id_objetivo, template_carta=Carta[response['idCarta']].template_carta.nombre, nombreJugador=Jugador[id_objetivo].nombre, nombreObjetivo=Jugador[idJugador].nombre)                
                else:
                    msg = f'{objetivo.nombre} no se defendió'
                    await manager_chat.handle_data("chat_msg", partida.id, msg=msg, isLog=True)
            else:
                msg = f'{jugador.nombre} jugó {carta.template_carta.nombre}'
                await manager_chat.handle_data("chat_msg", partida.id, msg=msg, isLog=True)
                    
            if not defendido:
                match carta.template_carta.nombre: 
                
                    case "Lanzallamas":
                        with db_session:
                            objetivo = Jugador.get(id=id_objetivo)
                        efectos_cartas.efecto_lanzallamas(jugador, id_objetivo)
                        msg = f'{objetivo.nombre} ha sido eliminado'
                        await manager_chat.handle_data("chat_msg", partida.id, msg=msg, isLog=True)
                        await fin_partida(partida.id, idJugador)
                    case "Vigila tus espaldas":
                        efectos_cartas.vigila_tus_espaldas(partida)
                    case "Cambio de lugar":
                        efectos_cartas.cambio_de_lugar(jugador, Jugador[id_objetivo])
                    case "Mas vale que corras":
                        efectos_cartas.mas_vale_que_corras(jugador, Jugador[id_objetivo])
                    case "Puerta atrancada":
                        efectos_cartas.puerta_trancada(jugador, Jugador[id_objetivo])
                    case "Hacha":
                        efectos_cartas.hacha(jugador, Jugador[id_objetivo])

                    case "Cuarentena":
                        efectos_cartas.efecto_cuarentena(jugador, Jugador[id_objetivo])
                    case "Analisis":
                        await efectos_cartas.analisis(partida.id, id_objetivo, idJugador)
                    case "Whisky":
                        await manager.handle_data("Whisky",partida.id,idJugador)   
                    case "Sospecha":
                        await efectos_cartas.sospecha(partida.id, id_objetivo, idJugador)
                    case "Cuerdas podridas":
                        efectos_cartas.cuerdas_podridas(partida.id)
                    case "Ups":
                        await manager.handle_data("Ups",partida.id,idJugador)
                    case "Que quede entre nosotros":
                        await efectos_cartas.entre_nosotros(partida.id, id_objetivo, idJugador)

                        


            partida.ultimaJugada = carta.template_carta.nombre        
            if(jugador.isAlive):
                jugador.cartas.remove(carta)

            carta.descartada=True
                
            partida.ultimaRobada=None
            
    
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
                if carta.template_carta.nombre == "La cosa":
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail="No se puede intercambiar la carta La Cosa")
                    
                if (partida.ultimaJugada != "Seduccion") & (not es_siguiente(jugador,jugObj)):
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Sólo puede intercambiar con el siguiente jugador")
                
                if (partida.ultimaJugada == "Seduccion") & jugObj.cuarentena:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="No se puede intercambiar con un jugador en cuarentena")

                if ((efectos_cartas.son_adyacentes(jugador, jugObj)[1] in [0,2]) & (jugador.blockIzq or jugObj.blockDer)) or ((efectos_cartas.son_adyacentes(jugador, jugObj)[1] == 1) & (jugador.blockDer or jugObj.blockIzq)):
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Hay una puerta trancada entre los jugadores")


                msg = f'{jugador.nombre} quiere intercambiar una carta con {jugObj.nombre}'
                await manager_chat.handle_data("chat_msg", partida.id, msg=msg, isLog=True)

                response = await manager.handle_data("intercambiar", carta.partida.id, jugador.id,
                                                     idCarta=idCarta, idObjetivo=idObjetivo)
                
                if response['aceptado']:
                    
                    msg = f'{jugObj.nombre} aceptó el intercambio'
                    await manager_chat.handle_data("chat_msg", partida.id, msg=msg, isLog=True)

                    jo_carta: Carta = Carta.get(id=response['data'])    
                    
                    corroborar_infección(jugador,jugObj,carta,jo_carta)
                    
                    intercambiar_cartas(idCarta, response['data'])
                    await manager.broadcast({'event': "intercambio exitoso"}, carta.partida.id)

                else:
                    jo_carta: Carta = Carta.get(id=response['data']) 
                    
                    if jo_carta.template_carta.nombre == "Aterrador":
                        await manager.handle_data("Aterrador",partida.id,idObjetivo=idObjetivo ,idCarta=idCarta)
                        

                    msg = f'{jugObj.nombre} jugó {jo_carta.template_carta.nombre} y rechazó el intercambio'
                    await manager_chat.handle_data("chat_msg", partida.id, msg=msg, isLog=True)
                    
                    await manager.broadcast({'event': "intercambio rechazado"}, carta.partida.id)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Carta o jugador no encontrados")

        partida.ultimaJugada = ""
        
        if not partida.turnoPostIntercambio:
            pos_actual = Jugador[partida.turnoActual].Posicion
            if partida.sentido:
                siguiente = Jugador.get(Posicion=(pos_actual+1)%partida.cantidadVivos, partida=partida)
            else:
                siguiente = Jugador.get(Posicion=(pos_actual-1)%partida.cantidadVivos, partida=partida)
            partida.turnoActual = siguiente.id
            checkeo_cuarentena(siguiente)
        else:
            partida.turnoActual = partida.turnoPostIntercambio
            partida.turnoPostIntercambio = None

        
                     
        commit()         
    await manager.handle_data("fin_de_turno",carta.partida.id)


@cartas_router.put("/descartar_carta/{idCarta}", status_code=200)
async def descartar_carta_put(idCarta: int):
    with db_session:
        carta = Carta.get(id=idCarta)
        jugador = carta.jugador
        partida = jugador.partida

    descartar_carta(idCarta)

    msg = f'{jugador.nombre} descartó una carta'
    await manager_chat.handle_data("chat_msg", partida.id, msg=msg, isLog=True)

@db_session   
def checkeo_cuarentena(jugador):
    if jugador.cuarentena:
        if jugador.cuarentenaCounter > 0:
            jugador.cuarentenaCounter -= 1
            if jugador.cuarentenaCounter == 0:
                jugador.cuarentena = False
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Error de flujo del programa; se bajo el contador a 0 pero el jugador sigue en cuarentena")  
