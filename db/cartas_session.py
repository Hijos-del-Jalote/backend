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
        crear_template_carta("Carta Vacia", "Esta Carta No Hace Nada",Tipo_Carta.accion)
        crear_template_carta("La cosa", "Te convertiste en la cosa pa",Tipo_Carta.contagio)
        crear_template_carta("Lanzallamas", "matar a un jugador",Tipo_Carta.accion)
        crear_template_carta("Vigila tus espaldas", "Invierte el orden de la partida",Tipo_Carta.accion)
        crear_template_carta("Cambio de lugar", "Cambia de sitio con un jugador adyacente que no este en cuarentena o tras una puerta cerrada", Tipo_Carta.accion)
        crear_template_carta("Mas vale que corras", "Cambia de sitio con cualquier jugador  que no este en cuarentena ignora puertas trancadas", Tipo_Carta.accion)
        crear_template_carta("Seduccion", "Intercambia carta con cualquier jugador que no este en cuarentena , termina tu turno", Tipo_Carta.accion)
        crear_template_carta("Analisis", "Mira la mano de cartas de un jugador adyacente", Tipo_Carta.accion)
        crear_template_carta("Sospecha", "Mira una carta aleatoria de la mano de cartas de un jugador adyacente", Tipo_Carta.accion)
        crear_template_carta("Whisky", "Muestra todas tus cartas a todos los jugadores", Tipo_Carta.accion)
        crear_template_carta("Hacha", "retira una carta 'puerta atrancada' o 'cuarentena'sobre ti o un jugador adyacente", Tipo_Carta.accion)
        crear_template_carta("Determinacion", "roba 3 cartas 'Alejate',elige 1 para quedartela y descarta las demas , luego juega o descarta una carta", Tipo_Carta.accion)
        crear_template_carta("Infectado", "Te convertiste en un infectado",Tipo_Carta.contagio)
    return 0


@db_session
def crear_carta(template,partida):
    with db_session:
        Carta(template_carta=template,partida=partida)
    return 0
