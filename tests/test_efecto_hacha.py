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
                        template_carta = "Hacha",
                        jugador=Jugador[1],
                        partida=Partida[1])
        cartaj2 = Carta(id=1001,
                        template_carta = "Seduccion",
                        jugador=Jugador[2],
                        partida=Partida[1])


#Hay mas de 2 jugadores con puerta trancada de por medio: jugar contra uno mismo y contra el otro. Deberia desaparecer puerta trancada
#Hay mas de 2 jugadores alguno con cuarentena: jugar contra uno mismo y contra el otro. Deberia desaparecer cuarentena
       
@db_session
def test_2_jugadores_puerta_atrancada_contra_otro(setup_db_before_test, cleanup_db_after_test):
    dar_cartas()
    Jugador[1].Posicion = 0
    Jugador[1].blockDer = True
    Jugador[1].blockIzq = True
    Jugador[2].Posicion = 1
    Jugador[2].blockDer = True
    Jugador[2].blockIzq = True
    Partida[1].cantidadVivos = 2
    Partida[1].turnoActual = Jugador[1].id
    Jugador[3].partida=None
    Jugador[4].partida=None
    
    db.commit()
    response = client.post(f'cartas/jugar?id_carta={1000}&id_objetivo={Jugador[2].id}&test=True')
    response_jugador1 = client.get(f'jugadores/{Jugador[1].id}')
    response_jugador2 = client.get(f'jugadores/{Jugador[2].id}')    
    assert(response.status_code == 200) & (response_jugador1.json()["blockIzq"] == False) & (response_jugador1.json()["blockDer"] == False) & (response_jugador2.json()["blockIzq"] == False) & (response_jugador2.json()["blockDer"] == False)
    
@db_session
def test_2_jugadores_puerta_atrancada_mismo(setup_db_before_test, cleanup_db_after_test):
    dar_cartas()
    Jugador[1].Posicion = 0
    Jugador[1].blockDer = True
    Jugador[1].blockIzq = True
    Jugador[2].Posicion = 1
    Jugador[2].blockDer = True
    Jugador[2].blockIzq = True
    Partida[1].cantidadVivos = 2
    Partida[1].turnoActual = Jugador[1].id
    Jugador[3].partida=None
    Jugador[4].partida=None
    
    db.commit()
    response = client.post(f'cartas/jugar?id_carta={1000}&id_objetivo={Jugador[1].id}&test=True')
    response_jugador1 = client.get(f'jugadores/{Jugador[1].id}')
    response_jugador2 = client.get(f'jugadores/{Jugador[2].id}')    
    assert(response.status_code == 200) & (response_jugador1.json()["blockIzq"] == False) & (response_jugador1.json()["blockDer"] == False) & (response_jugador2.json()["blockIzq"] == False) & (response_jugador2.json()["blockDer"] == False)
    
@db_session
def test_2_jugadores_cuarentena_contra_otro(setup_db_before_test, cleanup_db_after_test):
    dar_cartas()
    Jugador[1].Posicion = 0
    Jugador[1].cuarentena = True 
    Jugador[2].cuarentena = True 
    Jugador[2].Posicion = 1
    Partida[1].cantidadVivos = 2
    Partida[1].turnoActual = Jugador[1].id
    Jugador[3].partida=None
    Jugador[4].partida=None
    
    db.commit()
    response = client.post(f'cartas/jugar?id_carta={1000}&id_objetivo={Jugador[2].id}&test=True')
    response_jugador1 = client.get(f'jugadores/{Jugador[1].id}')
    response_jugador2 = client.get(f'jugadores/{Jugador[2].id}')    
    assert(response.status_code == 200) & (response_jugador2.json()["cuarentena"] == False) & (response_jugador1.json()["cuarentena"] == True)
    
@db_session
def test_2_jugadores_cuarentena_mismo(setup_db_before_test, cleanup_db_after_test):
    dar_cartas()
    Jugador[1].Posicion = 0
    Jugador[1].cuarentena = True 
    Jugador[2].cuarentena = True 
    Jugador[2].Posicion = 1
    Partida[1].cantidadVivos = 2
    Partida[1].turnoActual = Jugador[1].id
    Jugador[3].partida=None
    Jugador[4].partida=None
    
    db.commit()
    response = client.post(f'cartas/jugar?id_carta={1000}&id_objetivo={Jugador[1].id}&test=True')
    response_jugador1 = client.get(f'jugadores/{Jugador[1].id}')
    response_jugador2 = client.get(f'jugadores/{Jugador[2].id}')    
    assert(response.status_code == 200) & (response_jugador1.json()["cuarentena"] == False) & (response_jugador2.json()["cuarentena"] == True)   
    
@db_session
def test_4_jugadores_puerta_atrancada_contra_otro_der(setup_db_before_test, cleanup_db_after_test):
    dar_cartas()
    Jugador[1].Posicion = 0
    Jugador[1].cuarentena = True 
    Jugador[1].blockDer = True
    
    Jugador[2].cuarentena = True 
    Jugador[2].Posicion = 1
    Jugador[2].blockIzq = True
    Partida[1].cantidadVivos = 4
    Partida[1].turnoActual = Jugador[1].id
    
    db.commit()
    response = client.post(f'cartas/jugar?id_carta={1000}&id_objetivo={Jugador[2].id}&test=True')
    response_jugador1 = client.get(f'jugadores/{Jugador[1].id}')
    response_jugador2 = client.get(f'jugadores/{Jugador[2].id}')    
    assert(response.status_code == 200) & (response_jugador1.json()["cuarentena"] == True) & (response_jugador2.json()["cuarentena"] == True) & (response_jugador1.json()["blockDer"] == False) & (response_jugador2.json()["blockIzq"] == False)

@db_session
def test_4_jugadores_puerta_atrancada_contra_otro_izq(setup_db_before_test, cleanup_db_after_test):
    dar_cartas()
    Jugador[1].Posicion = 0
    Jugador[1].cuarentena = True 
    Jugador[1].blockIzq = True
    
    Jugador[4].cuarentena = True 
    Jugador[4].Posicion = 3
    Jugador[4].blockDer = True
    Partida[1].cantidadVivos = 4
    Partida[1].turnoActual = Jugador[1].id
    
    db.commit()
    response = client.post(f'cartas/jugar?id_carta={1000}&id_objetivo={Jugador[4].id}&test=True')
    response_jugador1 = client.get(f'jugadores/{Jugador[1].id}')
    response_jugador4 = client.get(f'jugadores/{Jugador[4].id}')    
    assert(response.status_code == 200) & (response_jugador1.json()["cuarentena"] == True) & (response_jugador4.json()["cuarentena"] == True) & (response_jugador1.json()["blockIzq"] == False) & (response_jugador4.json()["blockDer"] == False)

@db_session
def test_4_jugadores_cuarentena_contra_otro(setup_db_before_test, cleanup_db_after_test):
    dar_cartas()
    Jugador[1].Posicion = 0
    Jugador[1].cuarentena = True 
    Jugador[2].cuarentena = True 
    Jugador[2].Posicion = 1
    Partida[1].cantidadVivos = 4
    Partida[1].turnoActual = Jugador[1].id
    
    db.commit()
    response = client.post(f'cartas/jugar?id_carta={1000}&id_objetivo={Jugador[2].id}&test=True')
    response_jugador1 = client.get(f'jugadores/{Jugador[1].id}')
    response_jugador2 = client.get(f'jugadores/{Jugador[2].id}')    
    assert(response.status_code == 200) & (response_jugador1.json()["cuarentena"] == True) & (response_jugador2.json()["cuarentena"] == False)
    
@db_session
def test_4_jugadores_cuarentena_mismo(setup_db_before_test, cleanup_db_after_test):
    dar_cartas()
    Jugador[1].Posicion = 0
    Jugador[1].cuarentena = True 
    Jugador[2].cuarentena = True 
    Jugador[2].Posicion = 1
    Partida[1].cantidadVivos = 4
    Partida[1].turnoActual = Jugador[1].id
    
    db.commit()
    response = client.post(f'cartas/jugar?id_carta={1000}&id_objetivo={Jugador[1].id}&test=True')
    response_jugador1 = client.get(f'jugadores/{Jugador[1].id}')
    response_jugador2 = client.get(f'jugadores/{Jugador[2].id}')    
    assert(response.status_code == 200) & (response_jugador1.json()["cuarentena"] == False) & (response_jugador2.json()["cuarentena"] == True)
    
@db_session
def test_no_adyacentes(setup_db_before_test, cleanup_db_after_test):
    dar_cartas()
    Jugador[1].Posicion = 0
    Jugador[1].cuarentena = True 
    Jugador[2].cuarentena = True 
    Jugador[2].Posicion = 2
    Partida[1].cantidadVivos = 4
    Partida[1].turnoActual = Jugador[1].id
    
    db.commit()
    response = client.post(f'cartas/jugar?id_carta={1000}&id_objetivo={Jugador[2].id}&test=True')
    response_jugador1 = client.get(f'jugadores/{Jugador[1].id}')
    response_jugador2 = client.get(f'jugadores/{Jugador[2].id}')    
    assert(response.status_code == 400) & (response.text == '{"detail":"Los jugadores no son adyacentes"}') 
