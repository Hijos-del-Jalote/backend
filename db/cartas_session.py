from pony.orm import  *
from db.models import *


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
