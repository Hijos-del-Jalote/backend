from fastapi.testclient import TestClient
from db.models import *
from pony.orm import db_session
from fastapi import HTTPException
from api.ws import manager, manager_chat
import asyncio
import json
from db.cartas_session import intercambiar_cartas
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
        raise HTTPException(status_code = 400, detail ="Los jugadores o no existen o no pertenecen a la misma partida")     

def recalcular_posiciones(partida, pos_muerta):
    for jugador in partida.jugadores:
        if jugador.Posicion != None and jugador.Posicion > pos_muerta:
            jugador.Posicion -= 1
            db.commit()

def efecto_lanzallamas(jugador, id_objetivo):
    with db_session:
        if (id_objetivo != None) & (Jugador.exists(id=id_objetivo)):
            if jugador.cuarentena : raise HTTPException(status_code=400, detail="Jugador en cuarentena no puede eliminar otro jugador")
            objetivo = Jugador[id_objetivo]
            #Si hay una puerta trancada en al lado del jugador a eliminar se la debe preservar
            if objetivo.blockDer or objetivo.blockIzq:
                if jugador.partida.cantidadVivos == 3:
                    #Si hay 3 jugadores, al eliminar el objetivo quedaran 2, y la puerta trancada pasa a ser total entre esos 2 jugadores
                    Jugador.get(Posicion=(objetivo.Posicion+1)%objetivo.partida.cantidadVivos, partida=objetivo.partida).blockDer = True
                    Jugador.get(Posicion=(objetivo.Posicion+1)%objetivo.partida.cantidadVivos, partida=objetivo.partida).blockIzq = True
                    Jugador.get(Posicion=(objetivo.Posicion-1)%objetivo.partida.cantidadVivos, partida=objetivo.partida).blockDer = True
                    Jugador.get(Posicion=(objetivo.Posicion-1)%objetivo.partida.cantidadVivos, partida=objetivo.partida).blockIzq = True
                else:
                    #Si son mas de 3 jugadores la puerta trancada queda segun adyacencia comun 
                    Jugador.get(Posicion=(objetivo.Posicion-1)%objetivo.partida.cantidadVivos, partida=objetivo.partida).blockDer = True
                    Jugador.get(Posicion=(objetivo.Posicion+1)%objetivo.partida.cantidadVivos, partida=objetivo.partida).blockIzq = True
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
                jugador1.partida.turnoPostIntercambio = jugador2.id

            else:
                raise HTTPException(status_code=400, detail="Los jugadores no son adyacentes | El jugador objetivo esta en cuarentena | Hay una puerta trancada de por medio")
        else:
            raise HTTPException(status_code=400, detail="Jugador proporcionado no existente")


def mas_vale_que_corras(jugador1, jugador2):
    with db_session:
        if jugador1 and jugador2:
            if not jugador2.cuarentena:
                if jugador1.cuarentena : raise HTTPException(status_code=400, detail="Jugador en cuarentena no puede cambiar de lugar con otro jugador")
                intercambiar_posiciones(jugador1, jugador2)
                jugador1.partida.turnoPostIntercambio = jugador2.id
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

def efecto_cuarentena(jugador, objetivo):
    with db_session:
        if jugador and objetivo:
            if not son_adyacentes(jugador, objetivo)[0]: raise HTTPException(status_code=400, detail="Jugadores no son adyacentes")  
            objetivo.cuarentena = True
            #Seteo en 3 porque el efecto se aplica al jugador adyacente del que jugo la carta.
            #Entonces en el sentido de la ronda una vez le toque al jugador recien ahi se le baja en uno el contador.
            #Lo que tiene hacerlo de esta forma es que el objetivo del lado que el turno siguiente no es suyo la puede llegar a sufrir un poco mas. 
            objetivo.cuarentenaCount = 3
                
        else:
            raise HTTPException(status_code=400, detail="Jugador proporcionado no existente")
            
async def sospecha(idPartida, idObjetivo, idJugador):
    if son_adyacentes(Jugador.get(id=idObjetivo), Jugador.get(id=idJugador))[0]:
        await manager.handle_data("sospecha", idPartida, idObjetivo=idObjetivo, idJugador=idJugador)
        await asyncio.sleep(5)
    else:
        raise HTTPException(status_code=400, detail="El jugador objetivo deber ser adyacente")        
    

def cuerdas_podridas(idPartida):
    partida = Partida.get(id=idPartida)
    if not partida:
        raise HTTPException(status_code=400, detail="Partida no existente")
    else:
        for j in partida.jugadores:
            j.cuarentena = False

def hacha(jugador, objetivo):
    ady = son_adyacentes(jugador, objetivo)
    if (not objetivo) or (not jugador): raise HTTPException(status_code=400, detail="Jugador proporcionado no existente")
    if (jugador!=objetivo) and not ady[0]: raise HTTPException(status_code=400, detail="Los jugadores no son adyacentes")
    
    if (jugador.partida.cantidadVivos == 2) and not (jugador.blockDer or jugador.blockIzq):
        if jugador == objetivo:
            jugador.cuarentena = False
        else:
            objetivo.cuarentena = False
    elif (jugador.partida.cantidadVivos == 2) and (jugador.blockDer or jugador.blockIzq):
        jugador.blockDer = False
        jugador.blockIzq = False
        Jugador.get(Posicion=(jugador.Posicion+1)%jugador.partida.cantidadVivos, partida=jugador.partida).blockDer = False
        Jugador.get(Posicion=(jugador.Posicion+1)%jugador.partida.cantidadVivos, partida=jugador.partida).blockIzq = False
        
    elif (jugador.partida.cantidadVivos >2) and not (jugador.blockDer or jugador.blockIzq):
        if jugador == objetivo:
            jugador.cuarentena = False
        else:
            objetivo.cuarentena = False
    elif (jugador.partida.cantidadVivos >2) and (jugador.blockDer or jugador.blockIzq):
        if jugador == objetivo:
            if jugador.blockDer:
                jugador.blockDer = False
                Jugador.get((jugador.Posicion+1)%jugador.partida.cantidadVivos, partida=jugador.partida).blockIzq = False
            else:
                jugador.blockIzq = False
                Jugador.get((jugador.Posicion-1)%jugador.partida.cantidadVivos, partida=jugador.partida).blockDer = False
        elif ady[1] == 0:
            jugador.blockIzq = False
            objetivo.blockDer = False
        else:
            jugador.blockDer = False
            objetivo.blockIzq = False
    else:
        raise HTTPException(status_code=400, detail="Mal programada la logica en algun lado")


            

async def entre_nosotros(idPartida, idObjetivo, idJugador):
    if son_adyacentes(Jugador.get(id=idObjetivo), Jugador.get(id=idJugador))[0]:
        await manager.handle_data("Que quede entre nosotros", idPartida,idJugador=idJugador ,idObjetivo=idObjetivo)
    else:
        raise HTTPException(status_code=400, detail="El jugador objetivo deber ser adyacente")
        
async def analisis(idPartida, idObjetivo,idJugador,):
    if son_adyacentes(Jugador.get(id=idObjetivo), Jugador.get(id=idJugador))[0]:
        await manager.handle_data("Analisis", idPartida, idObjetivo=idObjetivo , idJugador=idJugador)
    else:
        raise HTTPException(status_code=400, detail="El jugador objetivo deber ser adyacente")


async def cita_a_ciegas(idPartida,idJugador):
    with db_session:
        response = await manager.handle_data("Cita a ciegas", idPartida=idPartida,idJugador=idJugador)
        jugador = Jugador.get(id=idJugador)
        partida = Partida.get(id=idPartida)
        json_data = json.loads(response)
        carta= Carta.get(id=json_data['data'])
        terminado=False
        while not terminado:
            nuevacarta = select(c for c in partida.cartas if (not c.descartada and c.jugador == None)).random(1)[0]
            if nuevacarta.template_carta.tipo=="Panico":
                nuevacarta.descartada=True
            else:
                nuevacarta.jugador=jugador
                terminado=True
        carta.jugador=None
        db.commit()
        await manager.handle_data("fin_de_turno", idPartida=idPartida)

def fallaste_es_aplicable(partida: Partida, jugador1: Jugador, jugador2: Jugador):
    if partida.sentido and (jugador1.blockDer or jugador2.blockIzq):
        return False
    if not partida.sentido and (jugador1.blockIzq or jugador2.blockDer):
        return False
    if jugador1.cuarentena or jugador2.cuarentena:
        return False
    
    return True

async def fallaste(partida: Partida, jugador1: Jugador, jugador2: Jugador, carta: Carta):
    # El siguiente jugador después de ti 
    # (siguiendo el orden de juego) debe intercambiar 
    # las cartas en lugar de hacerlo tú.
    #  Si este jugador recibe una carta “¡Infectado!” 
    # durante el intercambio, no queda Infectado,
    # ¡pero sabrá que ha recibido una carta de La Cosa 
    # durante el intercambio de un jugador Infectado!
    # Si hay “obstáculos” en el camino, como una
    # “Puerta atrancada” o “Cuarentena”, no se produce 
    # ningún intercambio, y el siguiente turno lo jugará
    # el jugador siguiente a aquel que inició el intercambio.
    if fallaste_es_aplicable(partida,jugador1,jugador2):
        with db_session:
            pos = ((jugador2.Posicion+1) % partida.cantidadVivos if partida.sentido 
                   else (jugador2.Posicion-1)%partida.cantidadVivos)
            jugObj: Jugador = Jugador.get(Posicion=pos, partida=partida)

        msg = f'{jugador1.nombre} pasó a intercambiar con {jugObj.nombre}'
        await manager_chat.handle_data("chat_msg", partida.id, msg=msg, isLog=True)
                                       
        response = await manager.handle_data("intercambiar", carta.partida.id, jugador1.id,
                                                     idCarta=carta.id, idObjetivo=jugObj.id)
        
        intercambiar_cartas(carta.id, response['data'])

