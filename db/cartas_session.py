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
        crear_template_carta("Aterrador", "Niegate a un ofrecimiento de cambio de carta , mira la carta que te has negado a recibir y roba una carta 'alejate", Tipo_Carta.defensa)
        crear_template_carta("Aqui estoy bien", "cancela una carta 'cambio de lugar' o 'mas vale que corras y roba una carta 'alejate", Tipo_Carta.defensa)
        crear_template_carta("No, gracias", "Niegate a un ofrecimiento de cambio de carta y roba una carta 'alejate", Tipo_Carta.defensa)
        crear_template_carta("Fallaste", "el siguiente jugador despues de ti realiza el intercambio de cartas en tu lugar , no queda infectado si recibe una carta infectado roba una carta 'alejate'" , Tipo_Carta.defensa)
        crear_template_carta("Nada de barbacoas", "cancela una carta 'lanzallamas' que te tenga como objetivo y roba una carta 'alejate", Tipo_Carta.defensa)
        crear_template_carta("Puerta atrancada", "Coloca esta carta entre un jugador adyacente y tu , no se permiten acciones entre este jugador y tu", Tipo_Carta.obstaculo)
        crear_template_carta("Cuarentena", "C", Tipo_Carta.obstaculo)
        crear_template_carta("Revelaciones", "o", Tipo_Carta.panico)
        crear_template_carta("Sal de aqui", "o", Tipo_Carta.panico)
        crear_template_carta("Olvidadizo", "o", Tipo_Carta.panico)
        crear_template_carta("Cuerdas podridas", "o", Tipo_Carta.panico)
        crear_template_carta("Uno, dos", "o", Tipo_Carta.panico)
        crear_template_carta("Tres, cuatro", "o", Tipo_Carta.panico)
        crear_template_carta("Es aqui la fiesta?", "o", Tipo_Carta.panico)
        crear_template_carta("Que quede entre nosotros", "o", Tipo_Carta.panico)
        crear_template_carta("Vuelta y vuelta", "o", Tipo_Carta.panico)
        crear_template_carta("No podemos ser amigos?", "o", Tipo_Carta.panico)
        crear_template_carta("Cita a ciegas", "o", Tipo_Carta.panico)
        crear_template_carta("Ups", "o", Tipo_Carta.panico)
        
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
            carta = select(c for c in partida.cartas if not c.descartada and
                           c.jugador==None and
                           c.template_carta.tipo != Tipo_Carta.panico).random(1)
            
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
            query = select(c for c in partida.cartas if (not c.descartada and c.jugador == None)).random(1)
            if not query:
                rellenar_mazo(partida)
                commit()
                carta = select(c for c in partida.cartas if (not c.descartada and c.jugador == None)).random(1)[0]
            else:
                carta = query[0]

            if carta.template_carta.tipo == Tipo_Carta.panico:

                cartaNombre = carta.template_carta.nombre
                
                match cartaNombre: # agregar las cartas de panico y actuar acorde
                    case _:
                        pass

            else:
                agregar_carta_en_mano(jugador.cartas, carta)

            
@db_session
def get_mano_jugador(idJugador: int):
    with db_session:
        jugador: Jugador = Jugador.get(id=idJugador)
        cartas = jugador.cartas
        list = []
        for carta in cartas:
            list.append(carta.template_carta.nombre)
    return list



def intercambiar_cartas(idCarta1: int, idCarta2: int):
    with db_session:
        carta1 = Carta.get(id=idCarta1)
        carta2 = Carta.get(id=idCarta2)

        jugador1 = carta1.jugador

        carta1.jugador = carta2.jugador
        carta2.jugador = jugador1

def carta_data(idCarta: int):
    # {'id': int, 'descartada': bool, 'template_carta': str, 'jugador': int, 'partida': int}
    with db_session:
        carta = Carta.get(id=idCarta)
    return carta.to_dict(with_collections=True)


@db_session
def descartar_carta(idCarta: int):
    with db_session:
        carta = Carta.get(id=idCarta)
        jugador = carta.jugador
        if not jugador or not carta:
                raise HTTPException(status_code=400,detail="Jugador o carta no encontrados")
        elif carta.template_carta.nombre == "La cosa":
            raise HTTPException(status_code=400,detail="No se puede descartar la carta La cosa")
        elif len(jugador.cartas) == 4:
            raise HTTPException(status_code=400,detail="No se puede descartar con 4 cartas en la mano")
        elif carta.template_carta.nombre == "Infectado" and jugador.Rol == Rol.infectado:
            cartas_infectado = len(select (c for c in jugador.cartas if c.template_carta.nombre== "Infectado"))
            if cartas_infectado > 1:
                jugador.cartas.remove(carta)
                carta.descartada=True
            else:
                raise HTTPException(status_code=400,detail="No se puede descartar la carta Infectado")
        else:
            if carta in jugador.cartas:
                carta.descartada=True
                jugador.cartas.remove(carta)
            else:
                raise HTTPException(status_code=404,detail="La carta no está en la mano del jugador")


def corroborar_infección(jugador1: Jugador, jugador2: Jugador,
                             carta1: Carta, carta2: Carta):
    with db_session:
        if carta1.template_carta.nombre == "Infectado" and jugador2.Rol != Rol.lacosa:
                jugador2.Rol = Rol.infectado
        elif carta2.template_carta.nombre == "Infectado" and jugador1.Rol != Rol.lacosa:
                jugador1.Rol = Rol.infectado

def puede_intercambiar_infectado(jugador1: Jugador, jugador2:Jugador):
    with db_session:
        ret = jugador1.Rol == Rol.lacosa or (jugador1.Rol == Rol.infectado and jugador2.Rol == Rol.lacosa)
    
    return ret
