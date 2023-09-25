from fastapi import APIRouter
from pony.orm import *
from db.models import *
import json 
from pydantic import BaseModel

partidas_router = APIRouter()
 

@partidas_router.post("/demo_insert")
async def demo_insert():
    with db_session:
        db.insert("Partida", nombre = "Partida1", password = "", maxJug = 6,minJug = 5,sentido = True,iniciada = False)


@partidas_router.get("", status_code=200)
async def listar_partidas():
    p = []
    with db_session:
        partidas = select(pa for pa in db.Partida if pa.iniciada == False)
        for partida in partidas:
            p.append({key: partida.to_dict()[key] for key in partida.to_dict() if key in ["id", "nombre","maxJug", "minJug"]})    
    return p

@partidas_router.post("/unir", status_code=200)
async def unir_jugador(idPartida:int, idJugador:int):
    with db_session:
        if db.Partida.exists(id=idPartida) & db.Jugador.exists(id=idJugador):
            jugador = db.Jugador[idJugador]
            jugador.partida = idPartida
        else:
            raise HTTPException(status_code=400, detail="Non existent id for Jugador or Partida")
