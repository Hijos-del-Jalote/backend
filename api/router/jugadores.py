from fastapi import APIRouter, status, HTTPException
from pony.orm import db_session
from db.models import Jugador, Rol
from api.router.schemas import PlayerResponse

jugadores_router = APIRouter()

@jugadores_router.post(path="/new", status_code=status.HTTP_201_CREATED)
async def new_player(uname: str) -> PlayerResponse:
    with db_session:
        if (uname.isspace() or len(uname) == 0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty username")
        else:
            user = Jugador(nombre = uname)
    return PlayerResponse(id=user.id)