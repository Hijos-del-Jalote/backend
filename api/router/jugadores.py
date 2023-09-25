from fastapi import APIRouter
from pony.orm import db_session
from db.models import *

jugadores_router = APIRouter() 

@jugadores_router.post("/demo_insert")
async def demo_insert():
    with db_session:
        db.insert("Jugador", nombre = "JUgador1", isHost = False, isAlive =True,blockIzq = False,blockDer = False)

    
