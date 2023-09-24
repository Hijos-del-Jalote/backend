from fastapi import APIRouter
from pony.orm import *
from db.models import *
import json 

partidas_router = APIRouter()
 

@partidas_router.post("/demo_insert")
async def demo_insert():
    with db_session:
        db.insert("Partida", nombre = "Partida1", password = "", maxJug = 6,minJug = 5,sentido = True,iniciada = False)


@partidas_router.get("/listar")
async def listar_partidas():
    p = []
    with db_session:
        partidas = select(pa for pa in db.Partida if pa.iniciada == False)
        for partida in partidas:
            p.append(partida.to_dict())    
    return p
