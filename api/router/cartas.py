from fastapi import APIRouter
from pony.orm import db_session
from db.models import *

cantidad_cartas_por_jugador = 4

@db_session
def crear_template_carta( nombre ,descripcion , tipo):
    with db_session:
        carta = TemplateCarta(nombre=nombre, descripcion=descripcion, tipo=tipo)
    return carta
   
    
@db_session
def crear_templates_cartas(): 
    if TemplateCarta.select().count() == 0:
        lanzallamas_template = crear_template_carta("Lanzallamas", "matar a un jugador", Tipo_Carta.accion)
        cartavacia_template = crear_template_carta("Carta Vacia", "Esta Carta No Hace Nada", Tipo_Carta.accion)
    return 0



@db_session
def crear_carta(template,partida):
    with db_session:
        carta=Carta(template_carta=template,partida=partida)
    return carta

"""@db_session
def repartir_cartas(partida):
    for j in partida.jugadores:
        for i in range cantidad_cartas_por_jugador:
            robar_carta(partida.cartas , j)
    return 0 
"""


cartas_router = APIRouter()
