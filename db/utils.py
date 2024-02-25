from db.models import *
import datetime

def obtener_tiempo_actual():
    ahora = datetime.datetime.now()
    return ahora.strftime('%H:%M')

def msg_data(msg: str, isLog: bool, idJugador:int = None):
    
    with db_session:
        jugador = Jugador.get(id=idJugador)
    nombre = jugador.nombre if jugador else None
    tiempo = obtener_tiempo_actual()
    return {'isLog': isLog,
            'player': nombre,
            'msg': msg,
            'time': tiempo
    }