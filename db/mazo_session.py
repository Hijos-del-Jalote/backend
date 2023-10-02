from pony.orm import *
from db.models import *
from db.cartas_session import *



@db_session
def crear_mazo_4jugadores(partida):
    lanzallamas= TemplateCarta.get(nombre="Lanzallamas")
    cartavacia= TemplateCarta.get(nombre="Carta Vacia")
    crear_carta(TemplateCarta.get(nombre="La cosa"),partida)
    for i in range(2):
        crear_carta(lanzallamas,partida)
    for i in range(31):
        crear_carta(cartavacia ,partida)
    return 0


@db_session
def crear_mazo_5jugadores(partida):
    lanzallamas= TemplateCarta.get(nombre="Lanzallamas")
    cartavacia= TemplateCarta.get(nombre="Carta Vacia")
    crear_carta(TemplateCarta.get(nombre="La cosa"),partida)
    for i in range(2):
        crear_carta(lanzallamas,partida)
    for i in range(31):
        crear_carta(cartavacia ,partida)
    return 0


@db_session
def crear_mazo_6jugadores(partida):
    lanzallamas= TemplateCarta.get(nombre="Lanzallamas")
    cartavacia= TemplateCarta.get(nombre="Carta Vacia")
    crear_carta(TemplateCarta.get(nombre="La cosa"),partida)
    for i in range(3):
        crear_carta(lanzallamas,partida)
    for i in range(31):
        crear_carta(cartavacia ,partida)
    return 0


@db_session
def crear_mazo_7jugadores(partida):
    lanzallamas= TemplateCarta.get(nombre="Lanzallamas")
    cartavacia= TemplateCarta.get(nombre="Carta Vacia")
    crear_carta(TemplateCarta.get(nombre="La cosa"),partida)
    for i in range(3):
        crear_carta(lanzallamas,partida)
    for i in range(55):
        crear_carta(cartavacia ,partida)
    return 0

@db_session
def crear_mazo_8jugadores(partida):
    lanzallamas= TemplateCarta.get(nombre="Lanzallamas")
    cartavacia= TemplateCarta.get(nombre="Carta Vacia")
    crear_carta(TemplateCarta.get(nombre="La cosa"),partida)
    for i in range(4):
        crear_carta(lanzallamas,partida)
    for i in range(59):
        crear_carta(cartavacia ,partida)
    return 0


@db_session
def crear_mazo_9jugadores(partida):
    lanzallamas= TemplateCarta.get(nombre="Lanzallamas")
    cartavacia= TemplateCarta.get(nombre="Carta Vacia")
    crear_carta(TemplateCarta.get(nombre="La cosa"),partida)
    for i in range(4):
        crear_carta(lanzallamas,partida)
    for i in range(63):
        crear_carta(cartavacia ,partida)
    return 0



@db_session
def crear_mazo_10jugadores(partida):
    lanzallamas= TemplateCarta.get(nombre="Lanzallamas")
    cartavacia= TemplateCarta.get(nombre="Carta Vacia")
    crear_carta(TemplateCarta.get(nombre="La cosa"),partida)
    for i in range(4):
        crear_carta(lanzallamas,partida)
    for i in range(63):
        crear_carta(cartavacia ,partida)
    return 0


@db_session
def crear_mazo_11jugadores(partida):
    lanzallamas= TemplateCarta.get(nombre="Lanzallamas")
    cartavacia= TemplateCarta.get(nombre="Carta Vacia")
    crear_carta(TemplateCarta.get(nombre="La cosa"),partida)
    for i in range(5):
        crear_carta(lanzallamas,partida)
    for i in range(79):
        crear_carta(cartavacia ,partida)
    return 0

@db_session
def crear_mazo_12jugadores(partida):
    lanzallamas= TemplateCarta.get(nombre="Lanzallamas")
    cartavacia= TemplateCarta.get(nombre="Carta Vacia")
    crear_carta(TemplateCarta.get(nombre="La cosa"),partida)
    for i in range(5):
        crear_carta(lanzallamas,partida)
    for i in range(79):
        crear_carta(cartavacia ,partida)
    return 0

def crear_mazo(partida):
    num_jugadores = len(partida.jugadores)
    if num_jugadores==4:
        crear_mazo_4jugadores(partida)
    elif num_jugadores==5:
        crear_mazo_5jugadores(partida)
    elif num_jugadores==6:
        crear_mazo_6jugadores(partida)
    elif num_jugadores==7:
        crear_mazo_7jugadores(partida)
    elif num_jugadores==8:
        crear_mazo_8jugadores(partida)
    elif num_jugadores==9:
        crear_mazo_9jugadores(partida)
    elif num_jugadores==10:
        crear_mazo_10jugadores(partida)
    elif num_jugadores==11:
        crear_mazo_11jugadores(partida)
    elif num_jugadores==12:
        crear_mazo_12jugadores(partida)
    return 0
        