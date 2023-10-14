from fastapi import APIRouter, HTTPException, status
from pony.orm import *
from db.models import *
from db.mazo_session import *
from db.cartas_session import *
from db.partidas_session import *
from .schemas import *
from random import randint
from api.ws import manager
from fastapi.websockets import *
from typing import List


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
        if db.Partida.exists(id=idPartida) & db.Jugador.exists(id=idJugador):
            if not db.Jugador[idJugador].partida:
                partida = db.Partida[idPartida].jugadores.add(db.Jugador[idJugador])
            else:
                raise HTTPException(status_code=400, detail="Jugador already in Partida")
        else:
            raise HTTPException(status_code=400, detail="Non existent id for Jugador or Partida")
    
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

@partidas_router.put("/iniciar", status_code=status.HTTP_200_OK)
async def iniciar_partida(idPartida: int):
    with db_session:
        partida = Partida.get(id=idPartida)
        if not partida: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="No existe partida con ese id")
        
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
        partida.turnoActual = randint(0,len(partida.jugadores)-1)
        posicion = 0
        for jugador in partida.jugadores:
            for carta in jugador.cartas:
                if carta.template_carta.nombre == "La cosa":
                    jugador.Rol = "La cosa"
                    break
                else:
                    jugador.Rol = "Humano"
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
                
    if len(jugadores) == 1: # o sea, hay ganador
        return EstadoPartida(finalizada=True, idGanador=jugadores[0].id)
    else:
        return EstadoPartida(finalizada=False, idGanador=-1)

@partidas_router.websocket("/{idPartida}/ws")
async def websocket_endpoint(websocket: WebSocket, idPartida: int):
    await manager.connect(websocket, idPartida)
    
    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(websocket, idPartida)

async def fin_partida(idPartida: int, idJugador: int): # el jugador que jugó la ultima carta

    with db_session:
        if db.Partida.exists(id=idPartida):  
            winners = get_winners(idPartida, idJugador)
            partida = Partida.get(id=idPartida)

            if len(winners) != 0:
                partida.finalizada = True
                db.commit()
                await manager.handle_data("finalizar", idPartida, winners[0], winners[1])
            
        else:
            raise HTTPException(status_code=400, detail="Non existent id for Jugador or Partida")

def get_winners(idPartida: int, idJugador: int) -> tuple:
    with db_session:
        jugadores = Partida.get(id=idPartida).jugadores
        humanos = []
        cosos = []
        isLacosaAlive = True
        cosaunicoganador = True
        for jugador in jugadores:
            if jugador.Rol == "Humano":
                humanos.append(jugador.id)
            if jugador.Rol == "La cosa" and not jugador.isAlive:
                isLacosaAlive = False
            # ultimo humano sigue contando como humano, asi que no está en cosos:
            if (jugador.Rol == "La cosa" or jugador.Rol == "Infectado") and (jugador.id != idJugador):
                cosos.append(jugador.id)
            if not jugador.isAlive:
                cosaunicoganador = False
            if jugador.Rol == "La cosa":
                idLacosa = jugador.id

    if len(humanos) == 0 and isLacosaAlive: # gana la cosa y su team
        if len(cosos) == len(jugadores) and cosaunicoganador: # si para todos isAlive y todos infectados
            return ([idLacosa], "cosos")
        else:
            return (sorted(cosos), "cosos")
        
    else:
        if not isLacosaAlive: # ganan los humanos
            return (sorted(humanos), "humanos")
        else:
            return ([], "no termino")
