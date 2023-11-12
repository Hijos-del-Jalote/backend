from fastapi.testclient import TestClient
from fastapi import status
from pony.orm import db_session
from api.api import app
from api.router.partidas import *
from api.router.cartas import *
from db.models import *
from db.cartas_session import *
from api.ws import *
import asyncio
from unittest.mock import AsyncMock, patch

async def test_jugar_entrenosotros_correcto(cleanup_db_after_test):

    client = TestClient(app)
    client2 = TestClient(app)
    crear_templates_cartas()
    crear_datos_partida()
        
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
            response = client.post(f'/cartas/jugar?id_objetivo=2&id_carta=1')
            print (response.json())
        response2 = ws.receive_json()
        response2 = ws.receive_json()   
        assert response2 == {"event": "Que quede entre nosotros", "data": ['Lanzallamas', 'Lanzallamas', 'Lanzallamas', 'Lanzallamas', 'Que quede entre nosotros']}
    assert response.status_code == 200

async def test_jugar_entrenosotros_jugadoresnoadyacentes(cleanup_db_after_test):

    client = TestClient(app)
    client2 = TestClient(app)
    crear_templates_cartas()
    crear_datos_partida()
        
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
            response = client.post(f'/cartas/jugar?id_objetivo=3&id_carta=1')
        assert response.status_code == 400
        assert response.json() == {'detail': "El jugador objetivo deber ser adyacente"}
    





def crear_datos_partida():
    with db_session:
        partida = Partida(nombre="partida", iniciada=True, finalizada=False , maxJug=5, minJug=4, turnoActual=1, cantidadVivos=4, sentido=True)
        db.commit()
        jugador = Jugador(nombre="Jugador", Rol="Humano", isHost=True, isAlive=True, blockIzq=False, blockDer=False, Posicion=1, partida=partida)
        jugador2 = Jugador(nombre="Jugador2", Rol="La cosa", isHost=False, isAlive=True, blockIzq=False, blockDer=False, Posicion=2, partida=partida)
        jugador3 = Jugador(nombre="Jugador3", Rol="Humano", isHost=False, isAlive=True, blockIzq=False, blockDer=False, Posicion=3, partida=partida)
        jugador4 = Jugador(nombre="Jugador4", Rol="Humano", isHost=False, isAlive=True, blockIzq=False, blockDer=False, Posicion=4, partida=partida)
        db.commit()
        partida.turnoActual=Jugador[1].id
        crear_templates_cartas()
        Entre_nosotros = Carta(descartada=False, template_carta="Que quede entre nosotros", partida=partida, jugador=jugador)
        for i in range(4):
            Carta(descartada=False, template_carta="Lanzallamas" , partida=partida, jugador=jugador)
        commit() 