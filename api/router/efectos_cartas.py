from fastapi.testclient import TestClient
from db.models import *
from pony.orm import db_session
from fastapi import HTTPException

#Esta funcion es para saber si jugador2 es adyacente a jugador1 y de que lado.
#El valor de retorno es una tupla (adyacente, lado)
#adyacente es bool indicando si es o no adyacente. Si no lo es entonces lado es None, sino:
#lado es un int que puede ser: 0 si es adyacente por izquierda, 1 si es adyacente por derecha, y 2 si es adyacente por ambos lados, osea que son los unicos 2 jugadores vivos.
@db_session
def son_adyacentes(jugador1, jugador2):
    if jugador1 and jugador2 and jugador1.partida == jugador2.partida:
        partida = jugador1.partida
        cant = partida.cantidadVivos
        #No se encontro
        if (jugador1.Posicion != ((jugador2.Posicion-1) % cant)) and (jugador1.Posicion != ((jugador2.Posicion+1) % cant)):
            return (False, None)
        #Se encontro por la izquierda
        elif (jugador1.Posicion != ((jugador2.Posicion-1) % cant)) and (jugador1.Posicion == ((jugador2.Posicion+1) % cant)):
            return (True, 0)
        #Se encontro por la derecha
        elif (jugador1.Posicion == ((jugador2.Posicion-1) % cant)) and (jugador1.Posicion != ((jugador2.Posicion+1) % cant)):
            return (True, 1)
        #Se encontro por ambos lados
        else:
            return (True, 2)
             
    else:
        raise Exception("Los jugadores o no existen o no pertenecen a la misma partida")     

def recalcular_posiciones(partida, pos_muerta):
    for jugador in partida.jugadores:
        if jugador.Posicion != None and jugador.Posicion > pos_muerta:
            jugador.Posicion -= 1
            db.commit()

def efecto_lanzallamas(id_objetivo):
    with db_session:
        if (id_objetivo != None) & (Jugador.exists(id=id_objetivo)):
            objetivo = Jugador[id_objetivo]
            recalcular_posiciones(objetivo.partida, objetivo.Posicion)
            objetivo.isAlive = False
            objetivo.Posicion = None
            objetivo.partida.cantidadVivos -= 1
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
            #Checkeo que jugador2 sea adyacente a jugador1 y decido si es adyacente por izquiera o por derecha para saber de que lado poner el bloqueo.
            adyacentes = son_adyacentes(jugador1, jugador2)
            print(adyacentes)
            if not adyacentes[0]:
                raise HTTPException(status_code=400, detail="Jugadores no son adyacentes") 
            elif adyacentes[1] == 0:
                jugador1.blockIzq = True
                jugador2.blockDer = True
            elif adyacentes[1] == 1:
                jugador1.blockDer = True
                jugador2.blockIzq = True
            else:
                jugador1.blockIzq = True
                jugador1.blockDer = True
                jugador2.blockIzq = True
                jugador2.blockDer = True
                                    
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
            cant = jugador1.partida.cantidadVivos
            ady = son_adyacentes(jugador1, jugador2)
            #ACA SE ASUME QUE SI SENTIDO=TRUE EL SENTIDO DE LA PARTIDA ES ANTIHORARIO, OSEA (POSICION+1 MOD CANT) CORRESPONDE BLOQUEO DE DERECHA Y (POSICION-1 MOD CANT) CORRESPONDE BLOQUEO DE IZQUIERDA 

            if ady[0] and (not jugador2.cuarentena) and ((ady[1]==1 and (not jugador1.blockDer) and (not jugador2.blockIzq)) or (ady[1]==0 and (not jugador1.blockIzq) and (not jugador1.blockDer)) or (ady[1]==2 and (not jugador1.blockIzq) and (not jugador1.blockDer))):
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


