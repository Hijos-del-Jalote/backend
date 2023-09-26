from fastapi import APIRouter, status, HTTPException
from pony.orm import db_session
from db.models import Jugador, Rol, db
from .schemas import PlayerResponse

jugadores_router = APIRouter()

@jugadores_router.get("/list")
async def traer(id:int):
    with db_session:
        return db.Jugador[id].to_dict()

@jugadores_router.post(path="", status_code=status.HTTP_201_CREATED)
async def new_player(nombre: str) -> PlayerResponse:
    with db_session:
        if (nombre.isspace() or len(nombre) == 0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty username")
        else:
            user = Jugador(nombre = nombre)
    return PlayerResponse(id=user.id)
