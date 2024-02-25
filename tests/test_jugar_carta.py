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
                        template_carta = "Infectado",
                        jugador=Jugador[1],
                        partida=Partida[1])
        cartaj2 = Carta(id=1001,
                        template_carta = "Seduccion",
                        jugador=Jugador[2],
                        partida=Partida[1])


   
@db_session
def test_jugar_carta_no_turno(setup_db_before_test, cleanup_db_after_test):
    dar_cartas()
    Partida[1].turnoActual = Jugador[2].id
    commit()
    #Jugar carta, Deberia dar error ya que no es el turno del jugador
    response = client.post(f'cartas/jugar?id_carta={1000}')
    assert((response.status_code == 400) & (response.text == '{"detail":"No es el turno del jugador que tiene esta carta"}'))
    
@db_session    
def test_jugar_carta_correctamente(setup_db_before_test, cleanup_db_after_test):
    dar_cartas()
    Partida[1].turnoActual = Jugador[1].id
    commit()
    #El jugador deberia jugar la carta correctamente
    response = client.post(f'cartas/jugar?id_carta={1000}')
    assert(response.status_code == 200)

@db_session
def test_jugar_carta_sin_dueño(setup_db_before_test, cleanup_db_after_test):    
    dar_cartas()
    Partida[1].turnoActual = Jugador[1].id
    Carta[1000].jugador = None
    commit()    

    response = client.post(f'cartas/jugar?id_carta={1000}')
    assert((response.status_code == 400) & (response.text == '{"detail":"No existe el id de la carta ó jugador que la tenga"}'))

@db_session    
def test_jugar_carta_inexistente(setup_db_before_test, cleanup_db_after_test):
    Partida[1].turnoActual = Jugador[1].id
    commit() 
    #Jugar carta inexistente -> deberia dar error
    response = client.post('cartas/jugar?id_carta=1000000')
    assert((response.status_code == 400) & (response.text == '{"detail":"No existe el id de la carta ó jugador que la tenga"}'))


        
