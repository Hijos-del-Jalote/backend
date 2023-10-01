from pony.orm import *
from db.models import *
from db.cartas_session import *



@db_session
def crear_mazo_4jugadores(partida):
    lanzallamas= TemplateCarta.get(nombre="Lanzallamas")
    cartavacia= TemplateCarta.get(nombre="Carta Vacia")
    for i in range(2):
        lanza_llamas=crear_carta(lanzallamas,partida)
    for i in range(32):
        carta_vacia=crear_carta(cartavacia ,partida)
    return 0


@db_session
def crear_mazo_5jugadores(partida):
    lanzallamas= TemplateCarta.get(nombre="Lanzallamas")
    cartavacia= TemplateCarta.get(nombre="Carta Vacia")
    for i in range(2):
        carta=crear_carta(lanzallamas,partida)
    for i in range(32):
        carta_vacia=crear_carta(cartavacia ,partida)
    return 0


@db_session
def crear_mazo_6jugadores(partida):
    lanzallamas= TemplateCarta.get(nombre="Lanzallamas")
    cartavacia= TemplateCarta.get(nombre="Carta Vacia")
    for i in range(3):
        carta=crear_carta(lanzallamas,partida)
    for i in range(32):
        carta_vacia=crear_carta(cartavacia ,partida)
    return 0


@db_session
def crear_mazo_7jugadores(partida):
    lanzallamas= TemplateCarta.get(nombre="Lanzallamas")
    cartavacia= TemplateCarta.get(nombre="Carta Vacia")
    for i in range(3):
        carta=crear_carta(lanzallamas,partida)
    for i in range(56):
        carta_vacia=crear_carta(cartavacia ,partida)
    return 0

@db_session
def crear_mazo_8jugadores(partida):
    lanzallamas= TemplateCarta.get(nombre="Lanzallamas")
    cartavacia= TemplateCarta.get(nombre="Carta Vacia")
    for i in range(4):
        carta=crear_carta(lanzallamas,partida)
    for i in range(60):
        carta_vacia=crear_carta(cartavacia ,partida)
    return 0


@db_session
def crear_mazo_9jugadores(partida):
    lanzallamas= TemplateCarta.get(nombre="Lanzallamas")
    cartavacia= TemplateCarta.get(nombre="Carta Vacia")
    for i in range(4):
        carta=crear_carta(lanzallamas,partida)
    for i in range(64):
        carta_vacia=crear_carta(cartavacia ,partida)
    return 0



@db_session
def crear_mazo_10jugadores(partida):
    lanzallamas= TemplateCarta.get(nombre="Lanzallamas")
    cartavacia= TemplateCarta.get(nombre="Carta Vacia")
    for i in range(4):
        carta=crear_carta(lanzallamas,partida)
    for i in range(64):
        carta_vacia=crear_carta(cartavacia ,partida)
    return 0


@db_session
def crear_mazo_11jugadores(partida):
    lanzallamas= TemplateCarta.get(nombre="Lanzallamas")
    cartavacia= TemplateCarta.get(nombre="Carta Vacia")
    for i in range(5):
        carta=crear_carta(lanzallamas,partida)
    for i in range(80):
        carta_vacia=crear_carta(cartavacia ,partida)
    return 0

@db_session
def crear_mazo_12jugadores(partida):
    lanzallamas= TemplateCarta.get(nombre="Lanzallamas")
    cartavacia= TemplateCarta.get(nombre="Carta Vacia")
    for i in range(5):
        carta=crear_carta(lanzallamas,partida)
    for i in range(80):
        carta_vacia=crear_carta(cartavacia ,partida)
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
        