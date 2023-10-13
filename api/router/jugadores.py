from fastapi import APIRouter, status, HTTPException
from pony.orm import db_session
from db.models import Jugador
from db.cartas_session import robar_carta
from .schemas import PlayerResponse, JugadorResponse

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
                                          cartas = lista_cartas)
                                          
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Jugador no existente")
    return jugadorResponse

@jugadores_router.put(path="/{id}/robar", status_code=status.HTTP_200_OK)
async def carta_robar(id: int):
    with db_session:
        robar_carta(id)
    return {"detail": "Robo exitoso!"}

