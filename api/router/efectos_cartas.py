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
            partida = jugador1.partida
            cant = len(partida.jugadores)
            #ACA SE ASUME QUE SI SENTIDO=TRUE EL SENTIDO DE LA PARTIDA ES ANTIHORARIO, OSEA (POSICION+1 MOD CANT) CORRESPONDE BLOQUEO DE DERECHA Y (POSICION-1 MOD CANT) CORRESPONDE BLOQUEO DE IZQUIERDA 
            
            #Checkeo que jugador2 sea adyacente a jugador1 y decido si es adyacente por izquiera o por derecha para saber de que lado poner el bloqueo.
            #La idea es recorrer las posiciones anteriores y siguentes a la posicion de jugador1 hasta que encuentre el primer jugador vivo.
            #Una vez que encuentro el primer jugador vivo (izq o der) me fijo si es jugador2.
            #Si lo es, entonces aplico bloqueos.
            #Si no, pongo una de las flags en False para saber que por ese lado no puede ser adyacente.
             
            #flags para saber si la busqueda de izq o derecha es valida (si encontramos un jugador vivo pero que no es jugador2 entonces se vuelve no valid)
            der_valido, izq_valido = True, True
            #flag para saber si encontramos.
            encontrado = False
            for i in range(1, len(partida.jugadores)):
                
                pos_sig = (partida.turnoActual+i) % cant
                jug_sig = Jugador.get(Posicion=pos_sig, partida=partida)
                
                pos_ant = (partida.turnoActual-i) % cant
                jug_ant = Jugador.get(Posicion=pos_ant, partida=partida)
                
                if jug_sig.isAlive and der_valido:
                    if jug_sig.Posicion != jugador2.Posicion:
                        der_valido = False
                    else:
                        jugador1.blockDer = True
                        jugador2.blockIzq = True         
                        db.commit()
                        encontrado = True
                if jug_ant.isAlive and izq_valido:
                    if jug_ant.Posicion != jugador2.Posicion:
                        izq_valido = False
                    else:
                        jugador1.blockIzq = True
                        jugador2.blockDer = True
                        db.commit()
                        encontrado = True
                        
                if (not encontrado) and (not der_valido) and (not izq_valido):
                    raise HTTPException(status_code=400, detail="Jugadores no son adyacentes")                
        else:
            raise HTTPException(status_code=400, detail="Jugador proporcionado no existente")

def intercambiar_posiciones(jugador1, jugador2):
    with db_session:
        p1 = jugador1.Posicion
        d1 = jugador1.blockDer
        i1 = jugador1.blockIzq
        
        jugador1.Posicion = jugador2.Posicion
        jugador1.blockDer = jugador2.blockDer
        jugador1.blockIzq = jugador2.blockIzq
        
        jugador2.Posicion = p1
        jugador2.blockDer = d1
        jugador2.blockIzq = i1
        
        db.commit()

def cambio_de_lugar(jugador1, jugador2):
    with db_session:
        if jugador1 and jugador2:
            cant = len(jugador1.partida.jugadores)
            #ACA SE ASUME QUE SI SENTIDO=TRUE EL SENTIDO DE LA PARTIDA ES ANTIHORARIO, OSEA (POSICION+1 MOD CANT) CORRESPONDE BLOQUEO DE DERECHA Y (POSICION-1 MOD CANT) CORRESPONDE BLOQUEO DE IZQUIERDA 
            if (not jugador2.cuarentena) and ((jugador1.Posicion+1 % cant == jugador2.Posicion and not jugador1.blockDer) or (jugador1.Posicion-1 % cant == jugador2.Posicion and not jugador1.blockIzq)):
                intercambiar_posiciones(jugador1, jugador2)
            else:
                raise HTTPException(status_code=400, detail="Los jugadores no son adyacentes | El jugador objetivo esta en cuarentena | Hay una puerta trancada de por medio")
        else:
            raise HTTPException(status_code=400, detail="Jugador proporcionado no existente")


def mas_vale_que_corras(jugador1, jugador2):
    with db_session:
        if jugador1 and jugador2:
            if not jugador2.cuarentena:
                intercambiar_posiciones(jugador1, jugador2)
            else:
                raise HTTPException(status_code=400, detail="El jugador objetivo esta en cuarentena")
        else:
            raise HTTPException(status_code=400, detail="Jugador proporcionado no existente")

def efecto_infeccion(id_objetivo, id_jugador):
    with db_session:
        if (id_objetivo != None) & (Jugador.exists(id=id_objetivo)):
            if (Jugador.get(id=id_jugador).Rol == "La cosa"): # queda checkeo aca por ahora, desp va en intercambio
                objetivo = Jugador[id_objetivo]
                objetivo.Rol = "Infectado"
                db.commit()
            else:
                raise HTTPException(status_code=400, detail="Jugador que juega la carta no es La cosa")
                # por ahora asumimos que alguien que no lo es, no la va a jugar, por eso se mantiene
                # el orden en jugar carta
        else:
            raise HTTPException(status_code=400, detail="Jugador objetivo No existe o No proporcionado")


