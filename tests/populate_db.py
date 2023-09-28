# Fake users and games for testing
from pony.orm import db_session, count
from db.models import Jugador,Partida
from tests.test_newplayer import random_user

def load_jugadores():
    #(id,nombre,isHost,partida)
    jugadores = [
        (1, f'{random_user()}', True),
        (2, f'{random_user()}', False),
        (3, f'{random_user()}', False),
        (4, f'{random_user()}', True),
        (5, f'{random_user()}', False),
        (6, f'{random_user()}', False)
    ]
    with db_session:
        if count(Jugador.select()) == 0:
            for id, nombre, isHost in jugadores:
                Jugador(id=id,
                        nombre=nombre,
                        isHost=isHost
                        )

def load_partidas():
    #(id,nombre,maxjug,minjug,iniciada)
    partidas = [
        (1, "partida1", 12, 4, False, {Jugador[1],Jugador[2],Jugador[3]}),
        (2, "partida2", 12, 4, False,{Jugador[4],Jugador[5],Jugador[6]})
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



@db_session
def populate_db():
    load_jugadores()
    load_partidas()

if __name__ == "__main__":
    populate_db()