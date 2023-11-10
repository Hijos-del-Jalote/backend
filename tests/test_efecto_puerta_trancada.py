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
        #Crear template de una carta si no existe
        if not TemplateCarta.exists(nombre="Puerta trancada"):
            template_carta = TemplateCarta(nombre="Puerta trancada", descripcion="Esta es una carta de prueba", tipo=Tipo_Carta.accion)
            l = True
        else:
            template_carta = TemplateCarta.get(nombre="Puerta trancada")
        #Crear un jugador que jugara la carta
        jugador1 = Jugador(nombre="Diego", isHost=True, isAlive=True, blockIzq=False, blockDer=False, Posicion=0)
        #Crear un jugador que recibira el efecto
        jugador2 = Jugador(nombre="Chun", isHost=False, isAlive=True, blockIzq=False, blockDer=False, Posicion=1)
        #Crear una partida con jugadores
        partida = Partida(nombre="Partida", maxJug=5, minJug=1, sentido=False, iniciada=True, cantidadVivos=2, jugadores={jugador1, jugador2})
        #Crear carta y asignarsela al jugador1 y partida
        carta = Carta(descartada=False, template_carta=template_carta, partida=partida, jugador=jugador1)
        db.commit()
        partida.turnoActual=jugador1.id
        db.commit()
        return jugador1, jugador2, partida, carta, l, template_carta


def test_efecto_puerta_trancada(cleanup_db_after_test):
    with db_session(optimistic=False):
        
        
        jugador1, jugador2, partida, carta, flag, template_carta = populate_db()
        
        jugar_carta_exito_2_jugadores(carta, jugador1, jugador2)
        
        #Pruebo con 1 jugador más
        jugador3 = Jugador(nombre="Nico", isHost=False, isAlive=True, blockIzq=False, blockDer=False, Posicion=2, partida = partida)
        carta.jugador = jugador1
        #reseteo blockeos
        jugador1.blockDer = False
        jugador1.blockIzq = False
        jugador2.blockDer = False
        jugador2.blockIzq = False
        partida.turnoActual=jugador1.id
        partida.cantidadVivos = 3
        db.commit() 
        
        jugar_carta_exito_3_jugadores(carta, jugador1, jugador2, jugador3)
        
 
        if flag:
            template_carta.delete()
        jugador1.delete()
        jugador2.delete()
        jugador3.delete()
        partida.delete()
        carta.delete()

def jugar_carta_exito_3_jugadores(carta, jugador1, jugador2, jugador3):
        #Jugar carta
        response = client.post(f'cartas/jugar?id_carta={carta.id}&id_objetivo={jugador3.id}&test=True') 
        assert(response.status_code == 200)
        #Traigo los jugadores.
        response_jugador1 = client.get(f'jugadores/{jugador1.id}')
        response_jugador2 = client.get(f'jugadores/{jugador2.id}')
        response_jugador3 = client.get(f'jugadores/{jugador3.id}')
        #Me fijo que se hayan hecho los bloqueos
        assert((response_jugador1.json()["blockDer"]  == False) & (response_jugador1.json()["blockIzq"]  == True) & (response_jugador2.json()["blockDer"]  == False) & (response_jugador2.json()["blockIzq"]  == False) & (response_jugador3.json()["blockDer"]  == True) & (response_jugador3.json()["blockIzq"]  == False))

def jugar_carta_exito_2_jugadores(carta, jugador1, jugador2):
    #Jugar carta
    response = client.post(f'cartas/jugar?id_carta={carta.id}&id_objetivo={jugador2.id}&test=True')
    assert(response.status_code == 200)
    #Traigo los jugadores.
    response_jugador1 = client.get(f'jugadores/{jugador1.id}')
    response_jugador2 = client.get(f'jugadores/{jugador2.id}')
    #Me fijo que se hayan hecho los bloqueos
    assert((response_jugador1.json()["blockDer"]  == True) & (response_jugador1.json()["blockIzq"]  == True) & (response_jugador2.json()["blockDer"]  == True) & (response_jugador2.json()["blockIzq"]  == True))
