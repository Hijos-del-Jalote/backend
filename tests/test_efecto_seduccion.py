from fastapi.testclient import TestClient
from fastapi import status
from api.api import app
from api.router.cartas import *
from pony.orm import db_session
from db.models import *

client = TestClient(app)


def test_efecto_mas_vale_que_corras(cleanup_db_after_test):
    with db_session(optimistic=False):
        l = False
        #Crear template de una carta vigila tus espaldas si no existe
        if not TemplateCarta.exists(nombre="Seduccion"):
            template_carta = TemplateCarta(nombre="Seduccion", descripcion="Esta es una carta de prueba", tipo=Tipo_Carta.accion)
            l = True
        else:
            template_carta = TemplateCarta.get(nombre="Mas vale que corras")
        #Crear un jugador que jugara la carta
        jugador1 = Jugador(nombre="Diego", isHost=True, isAlive=True, blockIzq=False, blockDer=False, Posicion=0)
        #Crear un jugador que recibira el efecto
        jugador2 = Jugador(nombre="Chun", isHost=False, isAlive=True, blockIzq=False, blockDer=False, Posicion=1, cuarentena=True)
        #Crear una partida con jugadores
        partida = Partida(nombre="Partida", maxJug=5, minJug=1, sentido=False, iniciada=True, turnoActual=0, jugadores={jugador1, jugador2})
        #Crear cartas y asignarselas al jugador1 y jugador2 y partida
        carta1 = Carta(descartada=False, template_carta=template_carta, partida=partida, jugador=jugador1)
        carta2 = Carta(descartada=False, template_carta=template_carta, partida=partida, jugador=jugador1)
        carta3 = Carta(descartada=False, template_carta=template_carta, partida=partida, jugador=jugador2)
        db.commit()
        #Jugar carta
        response = client.post(f'cartas/jugar?id_carta={carta1.id}&id_base={carta2.id}&id_objetivo={carta3.id}')
        assert(response.status_code == 200)
        #Pedir info de jugadores.
        response_jugador1 = client.get(f'jugadores/{jugador1.id}')
        response_jugador2 = client.get(f'jugadores/{jugador2.id}')
        #Checkear que se hayan intercambiado las cartas.
        assert((carta2 not in response_jugador1.json()["cartas"]) & (carta3 in response_jugador1.json()["cartas"]) & (carta2 in response_jugador2.json()["cartas"]) & (carta3 not in response_jugador2.json()["cartas"]))
        #jugar a jugador en cuarentena
        carta1.jugador = jugador1
        jugador1.cuarentena= True
        db.commit()
        #Jugar carta nuevamente, el jugador 2 esta en cuarentena y no deberia poder jugarse
        response = client.post(f'cartas/jugar?id_carta={carta1.id}&id_base={carta3.id}&id_objetivo={carta2.id}')
        assert(response.status_code == 400)        
        
        if l:
            template_carta.delete()
        jugador1.delete()
        jugador2.delete()
        partida.delete()
        carta1.delete()
        carta2.delete()
        carta3.delete()

