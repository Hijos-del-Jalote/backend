from fastapi import HTTPException, status
from pony.orm import db_session, select
from db.models import Partida, Jugador

cantidad_cartas_por_jugador = 4

@db_session
def rellenar_mazo(partida: Partida):
    partida.cartas.set(descartada=False)

def robar_carta(idJugador: int):
    with db_session:
        jugador = Jugador(id=idJugador)
        partida = jugador.partida
        if not partida:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="El jugador no está en una partida")
        else:
            carta = select(c for c in partida.cartas if not c.descartada).first()
            if not carta:
                rellenar_mazo(partida)
            else:
                jugador.cartas.add(carta)
                partida.cartas.remove(carta)
                
@db_session
def repartir_cartas(partida:Partida):
    for jugador in partida.jugadores:
        for i in range(cantidad_cartas_por_jugador):
            carta = select(c for c in partida.cartas if not c.descartada and c.jugador==None).random(1)
            jugador.cartas.add(carta)
