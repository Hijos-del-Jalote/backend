from fastapi import HTTPException, status
from pony.orm import db_session, select, count, Set, commit
from db.models import Partida, Jugador, Carta

@db_session
def rellenar_mazo(partida: Partida):
    for c in partida.cartas:
        c.set(descartada=False)

@db_session
def agregar_carta_en_mano(mano: Set, carta: Carta):
    if count(mano)<5:
        mano.add(carta)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail="Mano llena!")

@db_session
def robar_carta(idJugador: int):
    with db_session:
        jugador = Jugador.get(id=idJugador)
        partida = jugador.partida
        if not partida or not partida.iniciada:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="El jugador no está en una partida")
        else:
            carta = select(c for c in partida.cartas if (not c.descartada and c.jugador == None)).first()
            if not carta:
                rellenar_mazo(partida)
                commit()
                carta = select(c for c in partida.cartas if (not c.descartada and c.jugador == None)).first()
            agregar_carta_en_mano(jugador.cartas, carta)