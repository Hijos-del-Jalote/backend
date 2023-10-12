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
            jugador.Rol = "humano"
            jugador.Posicion = posicion
            posicion += 1


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
            data = await websocket.receive_text()
            print(f'data::::::::::::::::{data}')
            await manager.handle_data(data,idPartida)
            pass

    except WebSocketDisconnect:
        manager.disconnect(websocket, idPartida)

async def fin_partida(idPartida: int):
    with db_session:
        if db.Partida.exists(id=idPartida):
            try:
                await manager.handle_data("finalizar", idPartida)
            except Exception:
                return
        else:
            raise HTTPException(status_code=400, detail="Non existent id for Jugador or Partida")
        
