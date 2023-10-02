from pony.orm import  *
from db.models import *

cantidad_cartas_por_jugador = 4

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
    return 0


@db_session
def crear_carta(template,partida):
    with db_session:
        Carta(template_carta=template,partida=partida)
    return 0
