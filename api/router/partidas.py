from fastapi import APIRouter, HTTPException, status
from pony.orm import *
from db.models import *
from db.mazo_session import *
from db.cartas_session import *
from db.partidas_session import *
from .schemas import *
import random
from api.ws import manager, manager_chat
from fastapi.websockets import *
from typing import List
import json


partidas_router = APIRouter()


@partidas_router.get("", status_code=200)
async def listar_partidas():
    p = []
    with db_session:
        partidas = select(pa for pa in db.Partida if pa.iniciada == False)
        for partida in partidas:
            p.append({key: partida.to_dict()[key] for key in partida.to_dict() if key in ["id", "nombre","maxJug", "minJug"]})    
    return p

@partidas_router.post("/unir", status_code=200)
async def unir_jugador(idPartida:int, idJugador:int):
    with db_session:
        jugador = Jugador.get(id=idJugador)
        partida = Partida.get(id=idPartida)
        if partida and jugador:
            if not jugador.partida:
                partida.jugadores.add(jugador)
                jugador.isHost = False
            else:
                raise HTTPException(status_code=400, detail="Jugador already in Partida")
        else:
            raise HTTPException(status_code=400, detail="Non existent id for Jugador or Partida")
    
        jugador = Jugador.get(id=idJugador)
    
    msg = f'{jugador.nombre} se unió al lobby'
    await manager_chat.handle_data("chat_msg", jugador.partida.id, msg=msg, isLog=True)

    await manager.handle_data("unir", idPartida)



@partidas_router.post("",
                     response_model=PartidaOut, 
                     status_code=status.HTTP_201_CREATED)
async def crear_partida(nombrePartida: str, idHost: int) -> PartidaOut:
    with db_session:
        if(len(nombrePartida) == 0 or nombrePartida.isspace()):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Nombre vacio")
        else:
            host = Jugador.get(id=idHost)

            if not host:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="No existe usuario con ese id")
            if host.partida:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Este usuario ya esta en una partida")

            nueva_partida = Partida(nombre = nombrePartida,
                                    maxJug = 12,
                                    minJug = 4,
                                    jugadores = {host})
            host.isHost = True
            host.partida = nueva_partida
            db.commit()
    return PartidaOut(idPartida = nueva_partida.id) # se lo asigna pony solo

@partidas_router.get(path="/{id}", status_code=status.HTTP_200_OK)
async def obtener_partida(id: int) -> PartidaResponse:
    with db_session:
        partida = Partida.get(id=id)

        if partida:
            partidaResp = get_partida(id)
                                          
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Partida no encontrada")
    return partidaResp


@partidas_router.put("/iniciar/{idPartida}/", status_code=status.HTTP_200_OK)
async def iniciar_partida(idPartida:int , idJugador: int ):
    with db_session:
        partida = Partida.get(id=idPartida)
        if not partida: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="No existe partida con ese id")
        jugador= Jugador.get(id=idJugador)
        if not jugador:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="No existe jugador con ese id")
        if jugador.isHost == False:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="El jugador no es el host")
        
        if partida.iniciada:  
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Partida ya iniciada")
        
        if len(partida.jugadores) > partida.maxJug or len(partida.jugadores) < partida.minJug: 
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Partida no respeta limites jugadores")
        
        crear_templates_cartas()
        crear_mazo(partida)
        commit()
        repartir_cartas(partida)
        partida.iniciada = True
        partida.turnoActual = random.choice(tuple(partida.jugadores)).id
        posicion = 0
        partida.cantidadVivos = len(partida.jugadores)
        for jugador in partida.jugadores:
            for carta in jugador.cartas:
                if carta.template_carta.nombre == "La cosa":
                    jugador.Rol = "La cosa"
                    break
                else:
                    jugador.Rol = "Humano"
            jugador.isAlive = True
            jugador.blockDer = False
            jugador.blockIzq = False
            jugador.cuarentena = False
            jugador.Posicion = posicion
            posicion += 1
    await manager.handle_data("iniciar", idPartida)
    return {"detail": "Partida iniciada con exito"}


@partidas_router.get(path="/{id}/estado", response_model=EstadoPartida, status_code=status.HTTP_200_OK)
async def finalizar_partida(id: int) -> EstadoPartida:
    with db_session:
        partida = Partida.get(id=id)
        if not partida: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="No existe partida con ese id")
        
        # ahora a chequear si finalizo
        jugadores = []
        for jugador in partida.jugadores:
            if jugador.isAlive == True:
                jugadores.append(jugador)
                commit()
            if len(jugadores) == 1: # o sea, hay ganadors
                return EstadoPartida(finalizada=True, idGanador=jugadores[0].id)
            else:
                return EstadoPartida(finalizada=False, idGanador=-1)


@partidas_router.get(path="/{id}/chat", status_code=status.HTTP_200_OK)
async def get_chat(id: int):
    with db_session:
        partida = Partida.get(id=id)
        ret = []
        if not partida:
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                 detail="No se encontró esa partida")
        for m in partida.chat:
            ret.append(json.loads(m))
    
    return ret
    

@partidas_router.websocket("/{idPartida}/ws")
async def websocket_endpoint(websocket: WebSocket, idPartida: int, idJugador: int):
    await manager.connect(websocket, idPartida, idJugador)
    
    try:
        while True:
            data = await websocket.receive_text()
            await manager.put_in_message_queue(idPartida,idJugador,data)
    except WebSocketDisconnect:
        await manager.disconnect(idPartida, idJugador)

@partidas_router.websocket("/{idPartida}/ws/chat")
async def websocket_endpoint_chat(websocket: WebSocket, idPartida: int, idJugador: int):
    await manager_chat.connect(websocket, idPartida, idJugador)
    try:
        while True:
            msg = await websocket.receive_text()
            if(msg != ""):
                await manager_chat.handle_data("chat_msg",idPartida,idJugador,msg=msg)
    except WebSocketDisconnect:
        await manager_chat.disconnect(idPartida,idJugador)

async def fin_partida(idPartida: int, idJugador: int): # el jugador que jugó la ultima carta

    with db_session:
        if db.Partida.exists(id=idPartida):  
            winners = get_winners(idPartida, idJugador)
            partida = Partida.get(id=idPartida)

            if len(winners[0]) != 0:
                partida.finalizada = True
                for jugador in  partida.jugadores:
                    jugador.partida = None
                    jugador.cartas.clear()
                db.commit()
                await manager.handle_data(event="finalizar", idPartida=idPartida, 
                                        winners=winners[0], winning_team=winners[1])
            
        else:
            raise HTTPException(status_code=400, detail="Non existent id for Jugador or Partida")

def get_winners(idPartida: int, idJugador: int) -> tuple:
    with db_session:
        partida = Partida.get(id=idPartida)
        jugadores = partida.jugadores
        lacosa = get(j for j in jugadores if j.Rol == Rol.lacosa)
        muertos = select(j for j in jugadores if not j.isAlive)
        humanos = select(j.id for j in jugadores if j.Rol == Rol.humano)
    
    if len(jugadores)-1==len(muertos) and lacosa.isAlive: # todos muertos menos la cosa
        return ([lacosa.id], "cosos")           
    if not lacosa.isAlive: # muere la cosa
        return (sorted(humanos), "humanos")
    else:
        return ([], "no termino")
