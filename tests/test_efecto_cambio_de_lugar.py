from fastapi.testclient import TestClient
from fastapi import status
from api.api import app
from api.router.cartas import *
from pony.orm import db_session
from db.models import *

client = TestClient(app)


def test_efecto_cambio_de_lugar(cleanup_db_after_test):
    with db_session(optimistic=False):
        l = False
        #Crear template de una carta vigila tus espaldas si no existe
        if not TemplateCarta.exists(nombre="Cambio de lugar"):
            template_carta = TemplateCarta(nombre="Cambio de lugar", descripcion="Esta es una carta de prueba", tipo=Tipo_Carta.accion)
            l = True
        else:
            template_carta = TemplateCarta.get(nombre="Cambio de lugar")
        #Crear un jugador que jugara la carta
        jugador1 = Jugador(nombre="Diego", isHost=True, isAlive=True, blockIzq=False, blockDer=False, Posicion=0)
        #Crear un jugador que recibira el efecto
        jugador2 = Jugador(nombre="Chun", isHost=False, isAlive=True, blockIzq=False, blockDer=False, Posicion=1)
        #Crear un jugador que recibira el efecto
        jugador3 = Jugador(nombre="Nico", isHost=False, isAlive=True, blockIzq=False, blockDer=False, Posicion=2)
        #Crear un jugador que recibira el efecto
        jugador4 = Jugador(nombre="Gonza", isHost=False, isAlive=True, blockIzq=False, blockDer=False, Posicion=3)
        #Crear una partida con jugadores
        partida = Partida(nombre="Partida", maxJug=5, minJug=1, sentido=False, iniciada=True, turnoActual=0, jugadores={jugador1, jugador2, jugador3, jugador4})
        #Crear carta y asignarsela al jugador1 y partida
        carta = Carta(descartada=False, template_carta=template_carta, partida=partida, jugador=jugador1)
        db.commit()
        #Jugar carta
        response = client.post(f'cartas/jugar?id_carta={carta.id}&id_objetivo={jugador2.id}')
        assert(response.status_code == 200)
        #Pedir info de jugadores.
        response_jugador1 = client.get(f'jugadores/{jugador1.id}')
        response_jugador2 = client.get(f'jugadores/{jugador2.id}')
        #Checkear que se hayan intercambiado las posiciones.
        assert((response_jugador1.json()["posicion"] == 1) & (response_jugador2.json()["posicion"] == 0))
        #jugar entre jugadores no adyacentes
        carta.jugador = jugador1
        db.commit()
        #Jugar carta nuevamente
        response = client.post(f'cartas/jugar?id_carta={carta.id}&id_objetivo={jugador3.id}')
        assert(response.status_code == 400)
        #Hacer que haya una puerta trancada de por medio
        jugador2.Posicion = 1
        jugador1.blockDer = True
        carta.jugador = jugador1
        db.commit()
        #Jugar carta nuevamente
        response = client.post(f'cartas/jugar?id_carta={carta.id}&id_objetivo={jugador2.id}')
        assert(response.status_code == 400)
        #Hacer que jugador objetivo este en cuarentena
        jugador2.cuarentena = True
        jugador1.blockDer = False
        carta.jugador = jugador1
        db.commit()
        #Jugar carta nuevamente
        response = client.post(f'cartas/jugar?id_carta={carta.id}&id_objetivo={jugador2.id}')
        assert(response.status_code == 400)
        
        
        if l:
            template_carta.delete()
        jugador1.delete()
        jugador2.delete()
        jugador3.delete()
        jugador4.delete()
        partida.delete()
        carta.delete()

