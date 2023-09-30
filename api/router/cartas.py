from fastapi import APIRouter, HTTPException
from pony.orm import db_session
from db.models import *

cartas_router = APIRouter()

def efecto_lanzallamas(objetivo:Jugador):
    with db_session:
        objetivo.isAlive = False

@cartas_router.post("/jugar", status_code=200)
async def jugar_carta(id_carta:int, objetivo:Jugador=None):
    carta = Carta.get(id=id_carta)
    partida = carta.partida
    jugador = carta.jugador
    with db_session:
        if carta & jugador:
            jugador.cartas.remove(carta)
            
            if carta.template_carta.nombre == "Lanzallamas":
                try:
                    efecto_lanzallamas(objetivo)      
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"Failed Efecto Lanzallamas: {e}")
        else:
            raise HTTPException(status_code=400, detail="Non existant id for carta or jugador")
            
