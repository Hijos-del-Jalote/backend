from api.api import app
from fastapi.testclient import TestClient
from pony.orm import db_session, commit
from db.models import Jugador,Carta, Partida, Rol
from db.cartas_session import carta_data
from fastapi import WebSocket
from unittest.mock import AsyncMock, patch
import json

def asignar_pos():
    with db_session:
        Jugador[1].Posicion = 1
        Jugador[1].Rol = Rol.lacosa
        commit()
        Jugador[2].Posicion = 2
        Jugador[3].Posicion = 3
        Jugador[4].Posicion = 4
        commit()
        Jugador[1].partida.turnoActual=1

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
        


async def test_intercambiar_aceptado(setup_db_before_test,cleanup_db_after_test):

    client = TestClient(app)

    asignar_pos()
    dar_cartas()
    cartaData = carta_data(1000)

    async def fake_get_from_message_queue(id_partida, id_objetivo):
        # Simular una respuesta que se esperaría
        response_data = {
            "aceptado": True,
            "data": 1001   
        }
        return json.dumps(response_data)

    with client.websocket_connect(f'ws://localhost:8000/partidas/1/ws?idJugador=2') as ws:

        with patch("api.ws.manager.get_from_message_queue", new_callable=AsyncMock) as mock_get_from_message_queue:
            mock_get_from_message_queue.side_effect = fake_get_from_message_queue
            response = client.put(f'/cartas/1000/intercambiar?idObjetivo=2')
        

        

        response_ws = ws.receive_json()
        assert response_ws == {'event': "intercambio_request",
                               'data': cartaData}

        response_ws = ws.receive_json()
        assert response_ws == {'event': "intercambio",
                               'data': {'idJugador1': 1,
                                        'idJugador2': 2}}
        
        response_ws = ws.receive_json()
        assert response_ws == {'event': "intercambio exitoso"}

    with db_session:
        assert Jugador[2].Rol == Rol.infectado
        assert  Carta[1000].jugador == Jugador[2]
        assert Carta[1001].jugador == Jugador[1]
    
    assert response.status_code == 200

def test_intercambiar_rechazado(setup_db_before_test, cleanup_db_after_test):
    client = TestClient(app)

    asignar_pos()
    dar_cartas()
    cartaData = carta_data(1000)

    async def fake_get_from_message_queue(id_partida, id_objetivo):
        # Simular una respuesta que se esperaría
        response_data = {
            "aceptado": False,
            "data": None   
        }
        return json.dumps(response_data)

    with client.websocket_connect(f'ws://localhost:8000/partidas/1/ws?idJugador=2') as ws:

        with patch("api.ws.manager.get_from_message_queue", new_callable=AsyncMock) as mock_get_from_message_queue:
            mock_get_from_message_queue.side_effect = fake_get_from_message_queue
            response = client.put(f'/cartas/1000/intercambiar?idObjetivo=2')
        

        

        response_ws = ws.receive_json()
        assert response_ws == {'event': "intercambio_request",
                               'data': cartaData}

        response_ws = ws.receive_json()
        assert response_ws == {'event': "intercambio",
                               'data': {'idJugador1': 1,
                                        'idJugador2': 2}}
        
        response_ws = ws.receive_json()
        assert response_ws == {'event': "intercambio rechazado"}

    
    
    assert response.status_code == 200

def test_intercambiar_noady(setup_db_before_test, cleanup_db_after_test):
    client = TestClient(app)

    asignar_pos()
    dar_cartas()

    response = client.put(f'/cartas/1000/intercambiar?idObjetivo=3')

    assert response.status_code == 400
    assert response.json() == {'detail': "Sólo puede intercambiar con el siguiente jugador"}

def test_intercambiar_infectadofail_j1(setup_db_before_test, cleanup_db_after_test):
    client = TestClient(app)

    asignar_pos()
    dar_cartas()
    with db_session:
        Jugador[1].Rol = Rol.humano

    response = client.put(f'/cartas/1000/intercambiar?idObjetivo=1')

    assert response.status_code == 400
    assert response.json() == {'detail': "Jugador 1 no puede intercambiar una carta de infectado"}

async def test_intercambiar_infectadofail_j2(setup_db_before_test,cleanup_db_after_test): 
    
    client = TestClient(app)

    asignar_pos()
    dar_cartas()
    with db_session:
        Carta(id=1003,
                        template_carta = "Infectado",
                        jugador=Jugador[2],
                        partida=Partida[1])
        
    cartaData = carta_data(1000)

    with client.websocket_connect(f'ws://localhost:8000/partidas/1/ws?idJugador=2') as ws:

        with patch("api.ws.manager.get_from_message_queue", new_callable=AsyncMock) as mock_get_from_message_queue:
            mock_get_from_message_queue.side_effect = [json.dumps({"aceptado": True, "data": 1003}), json.dumps({"aceptado": False, "data": 1003})]
            response = client.put(f'/cartas/1000/intercambiar?idObjetivo=2')
        
        response_ws = ws.receive_json()
        assert response_ws == {'event': "intercambio_request",
                       'data': cartaData}

        response_ws = ws.receive_json()
        assert response_ws == {'event': "intercambio",
                               'data': {'idJugador1': 1,
                                        'idJugador2': 2}}

        response_ws = ws.receive_json()
        assert response_ws == {'event': "Intercambio erróneo",
                               'data': "No puedes intercambiar una carta de infectado"}

        response_ws = ws.receive_json()
        assert response_ws == {'event': "intercambio rechazado"}

        assert response.status_code == 200

async def test_intercambiar_infectado_a_lacosa(setup_db_before_test, cleanup_db_after_test): 
    
    client = TestClient(app)

    asignar_pos()
    dar_cartas()
    with db_session:
        Jugador[2].Rol = Rol.infectado
        Carta(id=1003,
                        template_carta = "Infectado",
                        jugador=Jugador[2],
                        partida=Partida[1])
        
    cartaData = carta_data(1000)

    with client.websocket_connect(f'ws://localhost:8000/partidas/1/ws?idJugador=2') as ws:

        with patch("api.ws.manager.get_from_message_queue", new_callable=AsyncMock) as mock_get_from_message_queue:
            mock_get_from_message_queue.side_effect = [json.dumps({"aceptado": True, "data": 1003})]
            response = client.put(f'/cartas/1000/intercambiar?idObjetivo=2')
        
        response_ws = ws.receive_json()
        assert response_ws == {'event': "intercambio_request",
                       'data': cartaData}

        response_ws = ws.receive_json()
        assert response_ws == {'event': "intercambio",
                               'data': {'idJugador1': 1,
                                        'idJugador2': 2}}

        response_ws = ws.receive_json()
        assert response_ws == {'event': "intercambio exitoso"}

        assert response.status_code == 200