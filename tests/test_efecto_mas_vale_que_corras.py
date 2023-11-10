from fastapi.testclient import TestClient
from fastapi import status
from api.api import app
from api.router.cartas import *
from pony.orm import db_session
from db.models import *

client = TestClient(app)

def populate_db():
    with db_session(optimistic=False):
        l = False
        #Crear template de una carta vigila tus espaldas si no existe
        if not TemplateCarta.exists(nombre="Mas vale que corras"):
            template_carta = TemplateCarta(nombre="Mas vale que corras", descripcion="Esta es una carta de prueba", tipo=Tipo_Carta.accion)
            l = True
        else:
            template_carta = TemplateCarta.get(nombre="Mas vale que corras")
        #Crear un jugador que jugara la carta
        jugador1 = Jugador(nombre="Diego", isHost=True, isAlive=True, blockIzq=False, blockDer=False, Posicion=0)
        #Crear un jugador que recibira el efecto
        jugador2 = Jugador(nombre="Chun", isHost=False, isAlive=True, blockIzq=False, blockDer=False, Posicion=1, cuarentena=True)
        #Crear un jugador que recibira el efecto
        jugador3 = Jugador(nombre="Nico", isHost=False, isAlive=True, blockIzq=False, blockDer=False, Posicion=2)
        #Crear una partida con jugadores
        partida = Partida(nombre="Partida", maxJug=5, minJug=1, sentido=False, iniciada=True, jugadores={jugador1, jugador2, jugador3})
        #Crear carta y asignarsela al jugador1 y partida
        carta = Carta(descartada=False, template_carta=template_carta, partida=partida, jugador=jugador1)
        db.commit()
        partida.turnoActual = jugador1.id
        db.commit()
        return l, template_carta, jugador1, jugador2, jugador3, partida, carta

def test_efecto_mas_vale_que_corras(cleanup_db_after_test):
    with db_session(optimistic=False):
        
        flag, template_carta, jugador1, jugador2, jugador3, partida, carta = populate_db()
        
        jugar_exitoso(carta, jugador1, jugador3)
        
        carta.jugador = jugador1
        db.commit()
                
        jugar_jugador_cuarentena(carta, jugador2)
        
        if flag:
            template_carta.delete()
        jugador1.delete()
        jugador2.delete()
        jugador3.delete()
        partida.delete()
        carta.delete()

def jugar_jugador_cuarentena(carta, jugador2):
    #Jugar carta nuevamente, el jugador 2 esta en cuarentena y no deberia poder jugarse
    response = client.post(f'cartas/jugar?id_carta={carta.id}&id_objetivo={jugador2.id}&test=True')
    assert(response.status_code == 400)

def jugar_exitoso(carta, jugador1, jugador3):
    #Jugar carta
    response = client.post(f'cartas/jugar?id_carta={carta.id}&id_objetivo={jugador3.id}&test=True')
    assert(response.status_code == 200)
    #Pedir info de jugadores.
    response_jugador1 = client.get(f'jugadores/{jugador1.id}')
    response_jugador3 = client.get(f'jugadores/{jugador3.id}')
    #Checkear que se hayan intercambiado las posiciones.
    assert((response_jugador1.json()["posicion"] == 2) & (response_jugador3.json()["posicion"] == 0))
