from fastapi import APIRouter, HTTPException
from pony.orm import db_session
from db.models import *

cartas_router = APIRouter()

@cartas_router.post("/jugar", status_code=200)
async def jugar_carta(id_carta:int, objetivo:int | None = None):
    with db_session:
        carta = Carta.get(id=id_carta)
        if carta and carta.jugador:
            if carta.partida.turnoActual != carta.jugador.Posicion : raise HTTPException(status_code=400, detail="No es el turno del jugador que tiene esta carta") 
            carta.jugador.cartas.remove(carta)
            carta.descartada=True
        else:
            raise HTTPException(status_code=400, detail="Non existant id for carta")
            
