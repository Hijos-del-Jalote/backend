from fastapi import APIRouter, HTTPException
from pony.orm import db_session
from db.models import *

cartas_router = APIRouter()

def efecto_lanzallamas(id_objetivo):
    with db_session:
        if (id_objetivo != None) & (Jugador.exists(id=id_objetivo)):
            objetivo = Jugador[id_objetivo]
            objetivo.isAlive = False
            db.commit()
        else:
            raise HTTPException(status_code=400, detail="Jugador objetivo No existe o No proporcionado")
            
            
@cartas_router.post("/jugar", status_code=200)
async def jugar_carta(id_carta:int, id_objetivo:int | None = None):
    with db_session:
        carta = Carta.get(id=id_carta)
        if carta and carta.jugador:
            if carta.partida.turnoActual != carta.jugador.Posicion : raise HTTPException(status_code=400, detail="No es el turno del jugador que tiene esta carta") 
            carta.jugador.cartas.remove(carta)
            carta.descartada=True
            if carta.template_carta.nombre == "Lanzallamas":
                efecto_lanzallamas(id_objetivo)
        else:
            raise HTTPException(status_code=400, detail="No existe el id de la carta ó jugador que la tenga")
