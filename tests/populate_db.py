# Fake users and games for testing
from pony.orm import db_session, count
from db.models import *
from tests.test_newplayer import random_user
from db.cartas_session import crear_templates_cartas
from db.mazo_session import crear_mazo
import random
from db.cartas_session import crear_templates_cartas

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #  
# Si va a usar este código agregue sus propios jugadores y partidas, no toque nada de lo que ya está  #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 


def load_jugadores():
    #(id,nombre,isHost,partida)
    jugadores = [
        (1, f'{random_user()}', True),
        (2, f'{random_user()}', False),
        (3, f'{random_user()}', False),
        (4, f'{random_user()}', False),
        (5, f'{random_user()}', True),
        (6, f'{random_user()}', False),
        (7, f'{random_user()}', False)
    ]
    with db_session:
        if count(Jugador.select()) == 0:
            for id, nombre, isHost in jugadores:
                Jugador(id=id,
                        nombre=nombre,
                        isHost=isHost
                        )

def load_partidas():
    #(id,nombre,maxjug,minjug,iniciada, jugadores)
    partidas = [
        (1, "partida1", 12, 4, True, {Jugador[1],Jugador[2],Jugador[3],Jugador[4]}),
        (2, "partida2", 12, 4, False,{Jugador[5],Jugador[6],Jugador[7]})
    ]
    with db_session:
        if count(Partida.select()) == 0:
            for id, nombre, maxjug, minjug, iniciada, jugadores in partidas:
                Partida(id=id,
                        nombre=nombre,
                        maxJug=maxjug,
                        minJug=minjug,
                        iniciada=iniciada,
                        jugadores=jugadores)


def load_templates():
    with db_session:
        crear_templates_cartas()

def load_cartas():
    with db_session:
        crear_mazo(Partida[1])
                

@db_session
def populate_db():
    with db_session:
        load_jugadores()
        load_partidas()
        load_templates()
        load_cartas()


if __name__ == "__main__":
    populate_db()