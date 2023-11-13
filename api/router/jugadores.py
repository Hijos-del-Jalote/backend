from fastapi import APIRouter, status, HTTPException
from pony.orm import db_session, commit
from db.models import Jugador, Partida
from db.cartas_session import robar_carta
from .schemas import PlayerResponse, JugadorResponse
from ..ws import manager, manager_chat


jugadores_router = APIRouter()

@jugadores_router.post(path="", status_code=status.HTTP_201_CREATED)
async def new_player(nombre: str) -> PlayerResponse:
    with db_session:
        if (nombre.isspace() or len(nombre) == 0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty username")
        else:
            user = Jugador(nombre = nombre)
        commit() # si no le hago esto se rompe cuando uso el intercambiar y al mismo tiempo agrego un jugador (ni idea por que)
    return PlayerResponse(id=user.id)


@jugadores_router.get("/{id}", status_code=status.HTTP_200_OK)
async def obtener_jugador(id: int) -> JugadorResponse:
    with db_session:
        jugador = Jugador.get(id=id)

        if jugador:
            lista_cartas = sorted([{
                "id": carta.id,
                "nombre": carta.template_carta.nombre,
                "descripcion": carta.template_carta.descripcion,
                "tipo": carta.template_carta.tipo
            } for carta in jugador.cartas], key=lambda c: c['id'])
                
            jugadorResponse = JugadorResponse(nombre = jugador.nombre,
                                          isHost = jugador.isHost,
                                          posicion = jugador.Posicion,
                                          isAlive = jugador.isAlive,
                                          rol = jugador.Rol,
                                          blockIzq = jugador.blockIzq,
                                          blockDer = jugador.blockDer,
                                          cuarentena = jugador.cuarentena,
                                          cuarentenaCount = jugador.cuarentenaCount,
                                          cartas = lista_cartas)
                                          
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Jugador no existente")
    return jugadorResponse

@jugadores_router.put(path="/{id}/robar", status_code=status.HTTP_200_OK)
async def carta_robar(id: int):
    with db_session:
        jugador = Jugador.get(id=id)
        robar_carta(id)
    
    msg = f'{jugador.nombre} robó una carta'
    await manager_chat.handle_data("chat_msg", jugador.partida.id, msg=msg, isLog=True)

    return {"detail": "Robo exitoso!"}

@jugadores_router.put(path="/{id}/abandonar_lobby", status_code=status.HTTP_200_OK)
async def abandonar_lobby(id: int):
    with db_session:
        jugador: Jugador = Jugador.get(id=id)
        
        if not jugador:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="El jugador no existe")
        if not jugador.partida:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="El jugador no se encuentra en una partida")
        if jugador.partida.iniciada:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="No puede abandonar el lobby de una partida iniciada")
        else: 
            isHost = jugador.isHost
            partida = jugador.partida
            partida.jugadores.remove(jugador)
            commit()
            
            msg = f'{jugador.nombre} abandonó el lobby'
            await manager_chat.handle_data("chat_msg", partida.id, msg=msg, isLog=True)

            await manager.handle_data("abandonar lobby",partida.id, jugador.id)
            
            if isHost:
               partida.delete()
               jugador.isHost = False
    

    return {"detail": "Partida abandonada con éxito"}

@jugadores_router.put("/{idJugador}/lacosafinaliza", status_code=status.HTTP_200_OK)
async def la_cosa_finaliza_la_partida(idJugador: int):
    with db_session:
        jugador = Jugador.get(id=idJugador)
        if not jugador:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="No existe jugador con ese id")
        partida = Partida.get(id=jugador.partida.id)
        humanos = []
        infectados = []
        if jugador.Rol != "La cosa":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="El jugador no es la cosa")
        if not partida: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="No existe partida con ese id")
        
        if partida.iniciada == False:  
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Partida no iniciada")
        
        if partida.finalizada == True: 
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Partida ya finalizada")
        ganalacosa=True
        for jugador in partida.jugadores:
            if jugador.Rol == "Humano" and jugador.isAlive == True:
                ganalacosa=False
                humanos.append(jugador.id)
            elif jugador.Rol == "Infectado" and partida.ultimo_infectado == jugador.id:
                humanos.append(jugador.id)
            else:
                infectados.append(jugador.id)
        if ganalacosa == True:
            partida.finalizada = True
            for jugador in partida.jugadores:
                jugador.partida = None
                jugador.cartas.clear()
            commit()
            await manager.handle_data(event="finalizar", idPartida=partida.id, 
                                        winners=infectados, winning_team="cosos")
        else:
            partida.finalizada = True
            for jugador in partida.jugadores:
                jugador.partida = None
                jugador.cartas.clear()
            commit()
            await manager.handle_data(event="finalizar", idPartida=partida.id, 
                                        winners=humanos, winning_team="humanos")
        
