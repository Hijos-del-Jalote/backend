from typing import Optional
from fastapi import APIRouter, HTTPException, status
from pony.orm import db_session
from db.models import Partida, db
from pydantic import BaseModel

partidas_router = APIRouter()

class PartidaIn(BaseModel):
    nombrePartida: str

class PartidaOut(BaseModel):
    idPartida: int

@partidas_router.post("",
                     response_model=PartidaOut, 
                     status_code=status.HTTP_201_CREATED)
async def crear_partida(partida: PartidaIn) -> PartidaOut:
    with db_session:

        if(len(partida.nombrePartida) == 0):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Nombre vacio")
        else:
            nueva_partida = Partida(nombre = partida.nombrePartida,
                                    maxJug = 12,
                                    minJug = 4)
            db.commit()
        return PartidaOut(idPartida = nueva_partida.id) # se lo asigna pony solo
        

 