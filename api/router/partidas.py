from typing import Optional
from fastapi import APIRouter, HTTPException, status
from pony.orm import db_session
from db.models import Partida, db
from pydantic import BaseModel
from .schemas import PartidaResponse

partidas_router = APIRouter()

class PartidaIn(BaseModel):
    nombrePartida: str

class PartidaOut(BaseModel):
    idPartida: int

@partidas_router.post("",
                     response_model=PartidaOut, 
                     status_code=status.HTTP_201_CREATED)
async def crear_partida(nombrePartida: str) -> PartidaOut:
    with db_session:
        if(len(nombrePartida) == 0 or nombrePartida.isspace()):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Nombre vacio")
        else:
            nueva_partida = Partida(nombre = nombrePartida,
                                    maxJug = 12,
                                    minJug = 4)
            db.commit()
    return PartidaOut(idPartida = nueva_partida.id) # se lo asigna pony solo


@partidas_router.get(path="/{id}", status_code=status.HTTP_200_OK)
async def obtener_partida(id: int):
    with db_session:
        partida = Partida.get(id=id)

        if partida:
            partidaResp = PartidaResponse(nombre=partida.nombre,
                                          maxJugadores=partida.maxJug,
                                          minJugadores=partida.minJug,
                                          inciada=partida.iniciada,
                                          turnoActual=partida.turnoActual,
                                          sentido=partida.sentido)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Partida no encontrada")
    return partidaResp