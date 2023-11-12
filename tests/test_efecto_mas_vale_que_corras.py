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
                        template_carta = "Mas vale que corras",
                        jugador=Jugador[1],
                        partida=Partida[1])
        cartaj2 = Carta(id=1001,
                        template_carta = "Seduccion",
                        jugador=Jugador[2],
                        partida=Partida[1])

        
@db_session
def test_jugar_jugador_cuarentena(setup_db_before_test, cleanup_db_after_test):
    dar_cartas()
    Jugador[1].Posicion = 0
    Jugador[2].Posicion = 1
    Partida[1].turnoActual = Jugador[1].id
    Jugador[2].cuarentena = True
    db.commit()
    #Jugar carta nuevamente, el jugador 2 esta en cuarentena y no deberia poder jugarse
    response = client.post(f'cartas/jugar?id_carta={1000}&id_objetivo={Jugador[2].id}&test=True')
    assert(response.status_code == 400)

@db_session
def test_jugar_exitoso_adyacente(setup_db_before_test, cleanup_db_after_test):
    dar_cartas()
    Jugador[1].Posicion = 0
    Jugador[2].Posicion = 1
    Partida[1].turnoActual = Jugador[1].id
    db.commit()
    #Jugar carta
    response = client.post(f'cartas/jugar?id_carta={1000}&id_objetivo={Jugador[2].id}&test=True')
    assert(response.status_code == 200)
    #Pedir info de jugadores.
    response_jugador1 = client.get(f'jugadores/{Jugador[1].id}')
    response_jugador2 = client.get(f'jugadores/{Jugador[2].id}')
    #Checkear que se hayan intercambiado las posiciones.
    assert((response_jugador1.json()["posicion"] == 1) & (response_jugador2.json()["posicion"] == 0))
    
@db_session
def test_jugar_exitoso_no_adyacente(setup_db_before_test, cleanup_db_after_test):
    dar_cartas()
    Jugador[1].Posicion = 0
    Jugador[3].Posicion = 2
    Partida[1].turnoActual = Jugador[1].id
    db.commit()
    #Jugar carta
    response = client.post(f'cartas/jugar?id_carta={1000}&id_objetivo={Jugador[3].id}&test=True')
    assert(response.status_code == 200)
    #Pedir info de jugadores.
    response_jugador1 = client.get(f'jugadores/{Jugador[1].id}')
    response_jugador2 = client.get(f'jugadores/{Jugador[3].id}')
    #Checkear que se hayan intercambiado las posiciones.
    assert((response_jugador1.json()["posicion"] == 2) & (response_jugador2.json()["posicion"] == 0))
