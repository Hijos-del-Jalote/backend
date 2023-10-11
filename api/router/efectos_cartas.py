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
            
def cambio_de_lugar(jugador1, jugador2):
    with db_session:
        if jugador1 and jugador2:
            cant = len(jugador1.partida.jugadores)
            #ACA SE ASUME QUE SI SENTIDO=TRUE EL SENTIDO DE LA PARTIDA ES ANTIHORARIO, OSEA (POSICION+1 MOD CANT) CORRESPONDE BLOQUEO DE DERECHA Y (POSICION-1 MOD CANT) CORRESPONDE BLOQUEO DE IZQUIERDA 
            if (not jugador2.cuarentena) and ((jugador1.Posicion+1 % cant == jugador2.Posicion and not jugador1.blockDer) or (jugador1.Posicion-1 % cant == jugador2.Posicion and not jugador1.blockIzq)):
                p1 = jugador1.Posicion
                jugador1.Posicion = jugador2.Posicion
                jugador2.Posicion = p1
                db.commit()
            else:
                raise HTTPException(status_code=400, detail="Los jugadores no son adyacentes | El jugador objetivo esta en cuarentena | Hay una puerta trancada de por medio")
        else:
            raise HTTPException(status_code=400, detail="Jugador proporcionado no existente")

def mas_vale_que_corras(jugador1, jugador2):
    with db_session:
        if jugador1 and jugador2:
            if not jugador2.cuarentena:
                p1 = jugador1.Posicion
                jugador1.Posicion = jugador2.Posicion
                jugador2.Posicion = p1
                db.commit()
            else:
                raise HTTPException(status_code=400, detail="El jugador objetivo esta en cuarentena")
        else:
            raise HTTPException(status_code=400, detail="Jugador proporcionado no existente")
