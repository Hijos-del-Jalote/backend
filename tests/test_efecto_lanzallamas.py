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
                        template_carta = "Lanzallamas",
                        jugador=Jugador[1],
                        partida=Partida[1])
        cartaj2 = Carta(id=1001,
                        template_carta = "Seduccion",
                        jugador=Jugador[2],
                        partida=Partida[1])


@db_session
def test_jugar_carta_falso_objetivo(setup_db_before_test, cleanup_db_after_test):
    dar_cartas()
    Jugador[1].Posicion = 0
    Jugador[2].Posicion = 1
    Partida[1].turnoActual = Jugador[1].id
    db.commit()
    #Jugar carta pasando objetivo inexistente
    response = client.post(f'cartas/jugar?id_carta={1000}&id_objetivo={-1}&test=True')
    assert(response.status_code == 400) & (response.text == '{"detail":"Jugador objetivo No existe o No proporcionado"}')  

@db_session
def test_jugar_carta_no_objetivo(setup_db_before_test, cleanup_db_after_test):
    dar_cartas()
    Jugador[1].Posicion = 0
    Jugador[2].Posicion = 1
    Partida[1].turnoActual = Jugador[1].id
    db.commit()
    #Jugar carta sin pasar objetivo
    response = client.post(f'cartas/jugar?id_carta={1000}')
    assert(response.status_code == 400) & (response.text == '{"detail":"Jugador objetivo No existe o No proporcionado"}')  

@db_session
def test_jugar_carta_exitoso_la_cosa(setup_db_before_test, cleanup_db_after_test):
    dar_cartas()
    Jugador[1].Posicion = 0
    Jugador[2].Posicion = 1
    Jugador[2].Rol = Rol.lacosa
    Partida[1].turnoActual = Jugador[1].id
    Partida[1].cantidadVivos = 4
    db.commit()
    #Jugar carta contra el jugador 2
    response = client.post(f'cartas/jugar?id_carta={1000}&id_objetivo={Jugador[2].id}&test=True')
    response_jugador2 = client.get(f'jugadores/{Jugador[2].id}')
    assert(response.status_code == 200) & (not response_jugador2.json()["isAlive"])
  
@db_session
def test_jugar_carta_exitoso_no_la_cosa(setup_db_before_test, cleanup_db_after_test):
    dar_cartas()
    Jugador[1].Posicion = 0
    Jugador[2].Posicion = 1
    Jugador[3].Rol = Rol.lacosa
    Partida[1].turnoActual = Jugador[1].id
    Partida[1].cantidadVivos = 4
    db.commit()
    #Jugar carta contra el jugador 2
    response = client.post(f'cartas/jugar?id_carta={1000}&id_objetivo={Jugador[2].id}&test=True')
    response_jugador2 = client.get(f'jugadores/{Jugador[2].id}')
    assert(response.status_code == 200) & (not response_jugador2.json()["isAlive"])  
    
