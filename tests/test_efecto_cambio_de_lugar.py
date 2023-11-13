from fastapi.testclient import TestClient
from fastapi import status
from api.api import app
from api.router.cartas import *
from pony.orm import db_session
from db.models import *
from unittest.mock import patch

client = TestClient(app)

def dar_cartas():
    with db_session:
        cartaj1 = Carta(id=1000,
                        template_carta = "Cambio de lugar",
                        jugador=Jugador[1],
                        partida=Partida[1])
        cartaj2 = Carta(id=1001,
                        template_carta = "Seduccion",
                        jugador=Jugador[2],
                        partida=Partida[1])

@db_session
def test_jugar_objetivo_en_cuarentena(setup_db_before_test, cleanup_db_after_test):
    dar_cartas()
    Jugador[1].Posicion = 0
    Jugador[2].Posicion = 1
    Jugador[2].cuarentena = True
    Partida[1].turnoActual = Jugador[1].id
    Partida[1].cantidadVivos = 4
    db.commit()
    #Jugar carta 
    response = client.post(f'cartas/jugar?id_carta={1000}&id_objetivo={Jugador[2].id}&test=True')
    assert(response.status_code == 400) & (response.text == '{"detail":"Los jugadores no son adyacentes | El jugador objetivo esta en cuarentena | Hay una puerta trancada de por medio"}') 
        
@db_session        
def test_jugar_puerta_trancada(setup_db_before_test, cleanup_db_after_test):
    dar_cartas()
    Jugador[1].Posicion = 0
    Jugador[2].Posicion = 1
    Jugador[2].blockIzq = True
    #Jugador[1].blockDer = True
    Partida[1].turnoActual = Jugador[1].id
    Partida[1].cantidadVivos = 4
    db.commit()
    #Jugar carta nuevamente
    response = client.post(f'cartas/jugar?id_carta={1000}&id_objetivo={Jugador[2].id}&test=True')
    assert(response.status_code == 400) & (response.text == '{"detail":"Los jugadores no son adyacentes | El jugador objetivo esta en cuarentena | Hay una puerta trancada de por medio"}')

@db_session                
def test_jugar_no_adyacente(setup_db_before_test, cleanup_db_after_test):
    dar_cartas()
    Jugador[1].Posicion = 0
    Jugador[3].Posicion = 2
    Partida[1].turnoActual = Jugador[1].id
    Partida[1].cantidadVivos = 4
    db.commit()

    #Jugar carta nuevamente
    response = client.post(f'cartas/jugar?id_carta={1000}&id_objetivo={Jugador[3].id}&test=True')
    assert(response.status_code == 400) & (response.text == '{"detail":"Los jugadores no son adyacentes | El jugador objetivo esta en cuarentena | Hay una puerta trancada de por medio"}')
           
@db_session
def test_jugar_carta_exitoso(setup_db_before_test):
    dar_cartas()
    Jugador[1].Posicion = 1
    Jugador[2].Posicion = 2
    #Jugador[1].blockDer = True
    Partida[1].turnoActual = Jugador[1].id
    Partida[1].cantidadVivos = 4
    db.commit()
    #Jugar carta
    response = client.post(f'cartas/jugar?id_carta={1000}&id_objetivo={Jugador[2].id}&test=True')
    assert(response.status_code == 200)
    #Pedir info de jugadores.
    response_jugador1 = client.get(f'jugadores/{Jugador[1].id}')
    response_jugador2 = client.get(f'jugadores/{Jugador[2].id}')
    #Checkear que se hayan intercambiado las posiciones.
    assert((response_jugador1.json()["posicion"] == 2) & (response_jugador2.json()["posicion"] == 1))
    commit()
    assert(Partida[1].turnoPostIntercambio == Jugador[2].id)

@db_session
def test_turnopostintercambio(cleanup_db_after_test):
    Jugador[3].Posicion = 3
    Jugador[4].Posicion = 4
    Carta[1000].jugador = Jugador[1]
    Carta[1001].jugador = Jugador[3]
    commit()
    with patch("api.ws.manager.get_from_message_queue") as mock:
        mock.return_value = json.dumps({'aceptado': True, 'data': 1000})
        response = client.put(f'/cartas/1000/intercambiar?idObjetivo=3')
    print(response.json())
    assert(response.status_code == 200)
    
    assert (Partida[1].turnoActual == Jugador[2].id)
