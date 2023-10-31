from .models import Jugador, Partida
from pony.orm import db_session
from .partidas_session import get_jugadores_partida

def get_abandonarlobby_data(idJugador: int, idPartida: int):
    with db_session:
        jugador = Jugador.get(id=idJugador)
        isHost = jugador.isHost
        if isHost:
            jugadores = []
        else:
            jugadores = get_jugadores_partida(idPartida)
    
    return {"host": isHost,
            "jugadores": jugadores}

def es_siguiente(jugador1: Jugador, jugador2: Jugador):
    with db_session:
        if jugador1.partida.sentido:
            return ((jugador1.Posicion + 1) % jugador1.partida.cantidadVivos) == jugador2.Posicion
        else:
            return ((jugador1.Posicion - 1) % jugador1.partida.cantidadVivos) == jugador2.Posicion