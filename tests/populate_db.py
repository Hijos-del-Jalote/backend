# Fake users and games for testing
from pony.orm import db_session, count
from db.models import *
from tests.test_newplayer import random_user
import random

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
        if count(TemplateCarta.select()) == 0:
            carta_vacia = TemplateCarta(nombre="Carta vacía",
                                        descripcion="Esto no hace nada",
                                        tipo=Tipo_Carta.accion)

def load_cartas():
    # (id,descartada, template, partida)
    cartas = []
    for i in range (1,10):
        cartas.append((i,False,"Carta vacía",Partida[1]))

    with db_session:
        if count(Carta.select()) == 0:
            for id, descartada, template, partida in cartas:
                Carta(id=id,
                      descartada=descartada,
                      template_carta=template,
                      partida=partida)
                

def load_cartas_jugadores():
    template_lanzallamas = TemplateCarta(nombre="Lanzallamas",
         descripcion="Esta es una carta de prueba", tipo=Tipo_Carta.accion)
    template_comun = TemplateCarta(nombre="Carta Vacia", descripcion=
         "Esta Carta No Hace Nada", tipo=Tipo_Carta.accion)

    opciones_template = [template_comun, template_lanzallamas]

    with db_session:
        partida = Partida.get(id=1)
        if count(Carta.select()) == 0:
            id = 0
            for jugador in partida.jugadores:
                for i in range(4):
                    template_random = random.choice(opciones_template)
                    carta = Carta(id=id,
                                  descartada=False,
                                  template_carta=template_random,
                                  partida=partida)
                    jugador.cartas.add(carta)
                    id += 1
                


def populate_db():
    load_jugadores()
    load_partidas()
    load_cartas_jugadores()
    load_templates()
    load_cartas()


if __name__ == "__main__":
    populate_db()