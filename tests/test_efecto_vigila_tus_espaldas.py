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
                        template_carta = "Vigila tus espaldas",
                        jugador=Jugador[1],
                        partida=Partida[1])
        cartaj2 = Carta(id=1001,
                        template_carta = "Vigila tus espaldas",
                        jugador=Jugador[5],
                        partida=Partida[1])



@db_session
def test_jugar_carta_exitoso_sentido1(setup_db_before_test, cleanup_db_after_test):    
    dar_cartas()
    Partida[1].turnoActual = Jugador[1].id
    Partida[1].sentido= False
    db.commit()
    #Jugar carta
    response = client.post(f'cartas/jugar?id_carta={1000}')
    assert(response.status_code == 200)
    #Pedir info de la partida cambiada
    response_partida = client.get(f'partidas/{Partida[1].id}')
    #Checkear que se haya cambiado el sentido de la partida, deberia ser true
    assert(response_partida.json()["sentido"] == True)
    
@db_session
def test_jugar_carta_exitoso_sentido2(setup_db_before_test, cleanup_db_after_test):
    dar_cartas()
    Partida[1].turnoActual = Jugador[1].id
    Partida[1].sentido= False
    db.commit()
    #Jugar carta nuevamente
    response = client.post(f'cartas/jugar?id_carta={1000}')
    assert(response.status_code == 200)
    #Pedir info de la partida cambiada
    response_partida = client.get(f'partidas/{Partida[1].id}')
    #Ahora el sentido deberia ser False 
    assert(response_partida.json()["sentido"] == True)
