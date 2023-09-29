from fastapi import APIRouter
from pony.orm import db_session
from db.models import *

cartas_router = APIRouter()

@cartas_router.post("/jugar", status_code=200)
async def jugar_carta(id_carta:int):
    carta = Carta.get(id=id_carta)
    partida = carta.partida
    with db_session:
        if carta:
            carta.jugador = None
            
