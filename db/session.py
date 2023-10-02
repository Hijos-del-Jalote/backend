from fastapi import HTTPException, status
from pony.orm import db_session, select
from db.models import Partida, Jugador
import random

cantidad_cartas_por_jugador = 4

@db_session
def repartir_cartas(partida:Partida):
    la_cosa=select(c for c in partida.cartas if c.template_carta.nombre=="La cosa").random(1)
    jugadores_lista = list(partida.jugadores)
    jugador_aleatorio = random.choice(jugadores_lista)
    jugador_aleatorio.cartas.add(la_cosa)
    for jugador in partida.jugadores:
        for i in range(cantidad_cartas_por_jugador):
            carta = select(c for c in partida.cartas if not c.descartada and c.jugador==None).random(1)
            if len(jugador.cartas)<4:
                 jugador.cartas.add(carta)

