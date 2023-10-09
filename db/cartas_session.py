from fastapi import HTTPException, status
from pony.orm import  *
from db.models import *
import random

@db_session
def crear_template_carta( nombre ,descripcion , tipo):
    with db_session:
       TemplateCarta(nombre=nombre, descripcion=descripcion, tipo=tipo)
    return 0

@db_session
def crear_templates_cartas(): 
    if TemplateCarta.select().count() == 0:
        crear_template_carta("Lanzallamas", "matar a un jugador",Tipo_Carta.accion)
        crear_template_carta("Carta Vacia", "Esta Carta No Hace Nada",Tipo_Carta.accion)
        crear_template_carta("La cosa", "Te convertiste en la cosa pa",Tipo_Carta.contagio)
    return 0


@db_session
def crear_carta(template,partida):
    with db_session:
        Carta(template_carta=template,partida=partida)
    return 0

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
            carta = select(c for c in partida.cartas if (not c.descartada and c.jugador == None)).random(1)
            if not carta:
                rellenar_mazo(partida)
                commit()
                carta = select(c for c in partida.cartas if (not c.descartada and c.jugador == None)).random(1)
            agregar_carta_en_mano(jugador.cartas, carta)

