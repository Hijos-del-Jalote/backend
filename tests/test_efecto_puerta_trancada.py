from fastapi.testclient import TestClient
from fastapi import status
from api.api import app
from api.router.cartas import *
from pony.orm import db_session
from db.models import *

client = TestClient(app)

def dar_cartas():
    with db_session:
        cartaj1 = Carta(id=1000,
                        template_carta = "Puerta atrancada",
                        jugador=Jugador[1],
                        partida=Partida[1])
        cartaj2 = Carta(id=1001,
                        template_carta = "Seduccion",
                        jugador=Jugador[2],
                        partida=Partida[1])


@db_session
def test_jugar_carta_exito_3_jugadores(setup_db_before_test, cleanup_db_after_test):
    dar_cartas()
    Jugador[1].Posicion = 0
    Jugador[2].Posicion = 1
    Jugador[3].Posicion = 2
    Partida[1].turnoActual = Jugador[1].id
    Partida[1].cantidadVivos = 3
    Jugador[4].partida = None
    db.commit()
    #Jugar carta
    response = client.post(f'cartas/jugar?id_carta={1000}&id_objetivo={Jugador[3].id}&test=True') 
    assert(response.status_code == 200)
    #Traigo los jugadores.
    response_jugador1 = client.get(f'jugadores/{Jugador[1].id}')
    response_jugador2 = client.get(f'jugadores/{Jugador[2].id}')
    response_jugador3 = client.get(f'jugadores/{Jugador[3].id}')
    #Me fijo que se hayan hecho los bloqueos
    assert((response_jugador1.json()["blockDer"]  == False) & (response_jugador1.json()["blockIzq"]  == True) & (response_jugador2.json()["blockDer"]  == False) & (response_jugador2.json()["blockIzq"]  == False) & (response_jugador3.json()["blockDer"]  == True) & (response_jugador3.json()["blockIzq"]  == False))


@db_session
def test_jugar_carta_exito_2_jugadores(setup_db_before_test, cleanup_db_after_test):
    dar_cartas()
    Jugador[1].Posicion = 0
    Jugador[2].Posicion = 1
    Partida[1].turnoActual = Jugador[1].id
    Partida[1].cantidadVivos = 2
    Jugador[4].partida = None
    db.commit()
    #Jugar carta
    response = client.post(f'cartas/jugar?id_carta={1000}&id_objetivo={Jugador[2].id}&test=True')
    assert(response.status_code == 200)
    #Traigo los jugadores.
    response_jugador1 = client.get(f'jugadores/{Jugador[1].id}')
    response_jugador2 = client.get(f'jugadores/{Jugador[2].id}')
    #Me fijo que se hayan hecho los bloqueos
    assert((response_jugador1.json()["blockDer"]  == True) & (response_jugador1.json()["blockIzq"]  == True) & (response_jugador2.json()["blockDer"]  == True) & (response_jugador2.json()["blockIzq"]  == True))
