from fastapi.testclient import TestClient
from fastapi import status
from api.api import app
from api.router.cartas import *
from pony.orm import db_session
from db.models import *

client = TestClient(app)


def test_efecto_puerta_trancada():
    with db_session(optimistic=False):
        l = False
        #Crear template de una carta si no existe
        if not TemplateCarta.exists(nombre="Puerta Trancada"):
            template_carta = TemplateCarta(nombre="Puerta Trancada", descripcion="Esta es una carta de prueba", tipo=Tipo_Carta.accion)
            l = True
        else:
            template_carta = TemplateCarta.get(nombre="Puerta Trancada")
        #Crear un jugador que jugara la carta
        jugador1 = Jugador(nombre="Diego", isHost=True, isAlive=True, blockIzq=False, blockDer=False, Posicion=0)
        #Crear un jugador que recibira el efecto
        jugador2 = Jugador(nombre="Chun", isHost=False, isAlive=True, blockIzq=False, blockDer=False, Posicion=1)
        #Crear un jugador que recibira el efecto
        jugador3 = Jugador(nombre="Nico", isHost=False, isAlive=True, blockIzq=False, blockDer=False, Posicion=2)
        #Crear una partida con jugadores
        partida = Partida(nombre="Partida", maxJug=5, minJug=1, sentido=False, iniciada=True, turnoActual=0, jugadores={jugador1, jugador2, jugador3})
        #Crear carta y asignarsela al jugador1 y partida
        carta = Carta(descartada=False, template_carta=template_carta, partida=partida, jugador=jugador1)
        db.commit()
        #Jugar carta
        response = client.post(f'cartas/jugar?id_carta={carta.id}&id_objetivo={jugador2.id}')
        assert(response.status_code == 200)
        #Traigo los jugadores.
        response_jugador1 = client.get(f'jugadores/{jugador1.id}')
        response_jugador2 = client.get(f'jugadores/{jugador2.id}')
        #Me fijo que se hayan hecho los bloqueos
        assert((response_jugador1.blockDer == True) & (response_jugador1.blockIzq == False) & (response_jugador2.blockDer == False) & (response_jugador2.blockIzq == True) )
        if l:
            template_carta.delete()
        jugador1.delete()
        jugador2.delete()
        jugador3.delete()
        partida.delete()
        carta.delete()

