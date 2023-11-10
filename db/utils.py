from db.models import *
import datetime

def msg_data(msg: str, idJugador:int, isLog: bool):
    
    with db_session:
        jugador = Jugador.get(id=idJugador)
    nombre = jugador.nombre if jugador else None
    ahora = datetime.datetime.now()
    tiempo = ahora.strftime('%H:%M')
    return {'isLog': isLog,
            'player': nombre,
            'msg': msg,
            'time': tiempo
    }