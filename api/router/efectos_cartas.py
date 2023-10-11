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
           
def puerta_trancada(jugador1, jugador2):
    with db_session:
        if jugador1 and jugador2:
            cant = len(jugador1.partida.jugadores)
            #ACA SE ASUME QUE SI SENTIDO=TRUE EL SENTIDO DE LA PARTIDA ES ANTIHORARIO, OSEA (POSICION+1 MOD CANT) CORRESPONDE BLOQUEO DE DERECHA Y (POSICION-1 MOD CANT) CORRESPONDE BLOQUEO DE IZQUIERDA 
            class opciones:
                siguiente = jugador1.Posicion+1 % cant
                anterior = jugador1.Posicion-1 % cant
            match jugador2.Posicion:
            
                case opciones.siguiente:
                    jugador1.blockDer = True
                    jugador2.blockIzq = True
                    db.commit()
                    
                case opciones.anterior:
                    jugador1.blockIzq = True
                    jugador2.blockDer = True
                    db.commit()
                    
                case _ :
                    raise HTTPException(status_code=400, detail="Jugadores no son adyacentes")
                

        else:
            raise HTTPException(status_code=400, detail="Jugador proporcionado no existente")
