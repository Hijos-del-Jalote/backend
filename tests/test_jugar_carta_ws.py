import pytest
from api.api import app
from pony.orm import db_session
from db.models import *
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import json
from api.router.schemas import JugarCartaData
from db.partidas_session import get_partida

def dar_cartas(nomcarta1: str, nomcarta2: str):
    with db_session:
        jugador1 = Jugador.get(id=1)
        jugador2 = Jugador.get(id=2)
        jugador3 = Jugador.get(id=3)
        jugador4 = Jugador.get(id=4)

        carta1: Carta = Carta(template_carta=nomcarta1, jugador=jugador1, partida=jugador1.partida)
        carta2: Carta = Carta(template_carta=nomcarta2, jugador=jugador2, partida=jugador2.partida)
        commit()
        jugador1.Posicion = 1
        jugador1.partida.turnoActual = 1
        jugador1.partida.cantidadVivos = 4
        commit()
        jugador2.Posicion = 2
        jugador3.Posicion = 3
        jugador4.Posucion = 4
        commit()
        jugador1.Rol = Rol.lacosa
        jugador2.Rol = Rol.humano
        jugador3.Rol = Rol.humano
        jugador4.Rol = Rol.humano

    return {"idpartida": jugador1.partida.id,
            "idc1": carta1.id,
            "idc2": carta2.id,
            "idj1": jugador1.id,
            "idj2": jugador2.id,
            "idj3": jugador3.id,
            "idj4": jugador4.id,
            "nomj1": jugador1.nombre,
            "nomj2": jugador2.nombre}


async def test_jugar_carta_defendido(setup_db_before_test, cleanup_db_after_test):

    client = TestClient(app)

    ids = dar_cartas("Lanzallamas", "Nada de barbacoas")
    

    async def fake_get_from_message_queue(id_partida, id_objetivo):
        # Simular una respuesta que se esperaría
        response_data = {
            "defendido": True,
            "idCarta": ids['idc2']  
        }
        return json.dumps(response_data)
    
    with client.websocket_connect(f'ws://localhost:8000/partidas/1/ws?idJugador=2') as ws:

        with patch("api.ws.manager.get_from_message_queue", new_callable=AsyncMock) as mock_get_from_message_queue:
            mock_get_from_message_queue.side_effect = fake_get_from_message_queue

            response = client.post(f'cartas/jugar?id_carta={ids["idc1"]}&id_objetivo=2')
        
        responsews = ws.receive_json()
        assert responsews == {'event': "jugar_carta",
                            'data':JugarCartaData(idObjetivo=ids['idj2'],
                                                  idCarta=ids['idc1'],
                                                  idJugador=ids['idj1'],
                                                  template_carta="Lanzallamas",
                                                  nombreJugador=ids['nomj1'],
                                                  nombreObjetivo=ids['nomj2']).model_dump_json()}
        
        responsews = ws.receive_json()
        assert responsews == {'event': "jugar_resp",
                            'data':JugarCartaData(idObjetivo=ids['idj1'],
                                                  idCarta=ids['idc2'],
                                                  idJugador=ids['idj2'],
                                                  template_carta="Nada de barbacoas",
                                                  nombreJugador=ids['nomj2'],
                                                  nombreObjetivo=ids['nomj1']).model_dump_json()}

        responsews = ws.receive_json()
        assert responsews == {'event': "fin_turno_jugar",
                              'data': get_partida(ids['idpartida']).model_dump_json()}


    assert response.status_code == 200

    with db_session:
        assert len(Jugador[1].cartas) == 0
        assert len(Jugador[2].cartas) == 1


async def test_jugar_carta_no_defendido(setup_db_before_test, cleanup_db_after_test):

    client = TestClient(app)
    
    ids = dar_cartas("Lanzallamas", "Cuarentena")
    

    async def fake_get_from_message_queue(id_partida, id_objetivo):
        # Simular una respuesta que se esperaría
        response_data = {
            "defendido": False,
            "idCarta": None  
        }
        return json.dumps(response_data)
    
    with client.websocket_connect(f'ws://localhost:8000/partidas/1/ws?idJugador=2') as ws:

        with patch("api.ws.manager.get_from_message_queue", new_callable=AsyncMock) as mock_get_from_message_queue:
            mock_get_from_message_queue.side_effect = fake_get_from_message_queue

            response = client.post(f'cartas/jugar?id_carta={ids["idc1"]}&id_objetivo=2')
        
        responsews = ws.receive_json()
        assert responsews == {'event': "jugar_carta",
                            'data':JugarCartaData(idObjetivo=ids['idj2'],
                                                  idCarta=ids['idc1'],
                                                  idJugador=ids['idj1'],
                                                  template_carta="Lanzallamas",
                                                  nombreJugador=ids['nomj1'],
                                                  nombreObjetivo=ids['nomj2']).model_dump_json()}

        responsews = ws.receive_json()
        assert responsews == {'event': "fin_turno_jugar",
                              'data': get_partida(ids['idpartida']).model_dump_json()}
        
        assert response.status_code == 200

        with db_session:
            assert Jugador[2].isAlive == False
            assert Jugador[1].partida.id == ids['idpartida']

def test_jugar_lacosa_muere(setup_db_before_test, cleanup_db_after_test):
    client = TestClient(app)
    ids = dar_cartas("Cuarentena", "Lanzallamas")

    with db_session:
        partida = Jugador[ids['idj1']].partida
        partida.turnoActual= ids['idj2']
    
    async def fake_get_from_message_queue(id_partida, id_objetivo):
        # Simular una respuesta que se esperaría
        response_data = {
            "defendido": False,
            "idCarta": None  
        }
        return json.dumps(response_data)

    with client.websocket_connect(f'ws://localhost:8000/partidas/{ids["idpartida"]}/ws?idJugador=3') as ws:

        with patch("api.ws.manager.get_from_message_queue", new_callable=AsyncMock) as mock_get_from_message_queue:
            mock_get_from_message_queue.side_effect = fake_get_from_message_queue

            response = client.post(f'cartas/jugar?id_carta={ids["idc2"]}&id_objetivo={ids["idj1"]}')

            responsews = ws.receive_json()
            assert responsews == {'event': "jugar_carta",
                                'data':JugarCartaData(idObjetivo=ids['idj1'],
                                                      idCarta=ids['idc2'],
                                                      idJugador=ids['idj2'],
                                                      template_carta="Lanzallamas",
                                                      nombreJugador=ids['nomj2'],
                                                      nombreObjetivo=ids['nomj1']).model_dump_json()}
            
            responsews = ws.receive_json()
            assert responsews == {'event': "finalizar",
                                  'data': '{"isHumanoTeamWinner":true,"winners":[2,3,4]}'}

            responsews = ws.receive_json()
            assert responsews == {'event': "fin_turno_jugar",
                                  'data': get_partida(ids['idpartida']).model_dump_json()}

            assert response.status_code == 200
        
        with db_session:
            assert Partida[ids['idpartida']].finalizada
            assert len(Partida[ids['idpartida']].jugadores) == 0
            for i in range(1,4):
                assert len(Jugador[ids[f"idj{i}"]].cartas) == 0 


def test_jugar_lacosa_procede_a_masacrar_a_todos(setup_db_before_test, cleanup_db_after_test):
    client = TestClient(app)
    ids = dar_cartas("Lanzallamas", "Cuarentena")

    with db_session:
        for i in range(3,5):
            Jugador[ids[f'idj{i}']].isAlive = False
    async def fake_get_from_message_queue(id_partida, id_objetivo):
        # Simular una respuesta que se esperaría
        response_data = {
            "defendido": False,
            "idCarta": None  
        }
        return json.dumps(response_data)

    with client.websocket_connect(f'ws://localhost:8000/partidas/{ids["idpartida"]}/ws?idJugador=1') as ws:

        with patch("api.ws.manager.get_from_message_queue", new_callable=AsyncMock) as mock_get_from_message_queue:
            mock_get_from_message_queue.side_effect = fake_get_from_message_queue

            response = client.post(f'cartas/jugar?id_carta={ids["idc1"]}&id_objetivo={ids["idj2"]}')

            responsews = ws.receive_json()
            assert responsews == {'event': "jugar_carta",
                                'data':JugarCartaData(idObjetivo=ids['idj2'],
                                                      idCarta=ids['idc1'],
                                                      idJugador=ids['idj1'],
                                                      template_carta="Lanzallamas",
                                                      nombreJugador=ids['nomj1'],
                                                      nombreObjetivo=ids['nomj2']).model_dump_json()}
            
            responsews = ws.receive_json()
            assert responsews == {'event': "finalizar",
                                  'data': '{"isHumanoTeamWinner":false,"winners":[1]}'}

            responsews = ws.receive_json()
            assert responsews == {'event': "fin_turno_jugar",
                                  'data': get_partida(ids['idpartida']).model_dump_json()}

            assert response.status_code == 200
        
        with db_session:
            assert Partida[ids['idpartida']].finalizada
            assert len(Partida[ids['idpartida']].jugadores) == 0
            for i in range(1,4):
                assert len(Jugador[ids[f"idj{i}"]].cartas) == 0 


def test_jugar_carta_noturno(setup_db_before_test, cleanup_db_after_test):

    client = TestClient(app)
    
    ids = dar_cartas("Lanzallamas", "Cuarentena")
    
    response = client.post(f'cartas/jugar?id_carta={ids["idc2"]}&id_objetivo=1')
    assert response.status_code == 400
    assert response.json() == {'detail': "No es el turno del jugador que tiene esta carta"}

def test_jugar_carta_nocarta(setup_db_before_test, cleanup_db_after_test):

    client = TestClient(app)
    
    ids = dar_cartas("Lanzallamas", "Cuarentena")
    
    response = client.post(f'cartas/jugar?id_carta=42069&id_objetivo=1')
    assert response.status_code == 400
    assert response.json() == {'detail': "No existe el id de la carta ó jugador que la tenga"}
