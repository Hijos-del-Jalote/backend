from typing import Optional
from fastapi import APIRouter, HTTPException, status
from pony.orm import *
from db.models import *
import json 
from pydantic import BaseModel
from .schemas import PartidaResponse

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
            partida = db.Partida[idPartida].jugadores.add(db.Jugador[idJugador])
        else:
            raise HTTPException(status_code=400, detail="Non existent id for Jugador or Partida")

class PartidaIn(BaseModel):
    nombrePartida: str

class PartidaOut(BaseModel):
    idPartida: int

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
            partidaResp = PartidaResponse(nombre=partida.nombre,
                                          maxJugadores=partida.maxJug,
                                          minJugadores=partida.minJug,
                                          inciada=partida.iniciada,
                                          turnoActual=partida.turnoActual,
                                          sentido=partida.sentido,
                                          jugadores=[{"id": j.id,
                                                      "nombre": j.nombre} for j in partida.jugadores])
                                          
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Partida no encontrada")
    return partidaResp