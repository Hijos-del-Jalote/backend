from fastapi.testclient import TestClient
from db.models import *
from pony.orm import db_session
from fastapi import HTTPException

def efecto_lanzallamas(id_objetivo):
    with db_session:
        if (id_objetivo != None) & (Jugador.exists(id=id_objetivo)):
            objetivo = Jugador[id_objetivo]
            objetivo.isAlive = False
            objetivo.cartas.clear()
            db.commit()
        else:
            raise HTTPException(status_code=400, detail="Jugador objetivo No existe o No proporcionado")
            
def vigila_tus_espaldas(partida):
    with db_session:
        if partida:
            partida.sentido = not partida.sentido
            db.commit()
        else:
            raise HTTPException(status_code=400, detail="Partida no existente")
            
def efecto_infeccion(id_objetivo, id_jugador):
    with db_session:
        if (id_objetivo != None) & (Jugador.exists(id=id_objetivo)):
            if (Jugador.get(id=id_jugador).Rol == "lacosa"):
                objetivo = Jugador[id_objetivo]
                objetivo.Rol = "infectado"
                db.commit()
            else:
                raise HTTPException(status_code=400, detail="Jugador que juega la carta no es La cosa")
                # por ahora asumimos que alguien que no lo es, no la va a jugar, por eso se mantiene
                # el orden en jugar carta
        else:
            raise HTTPException(status_code=400, detail="Jugador objetivo No existe o No proporcionado")