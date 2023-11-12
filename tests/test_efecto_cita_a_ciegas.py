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
        Jugador[1].Rol = Rol.infectado
        commit()
        Jugador[2].Posicion = 2
        Jugador[3].Posicion = 3
        Jugador[4].Posicion = 4
        commit()
        Jugador[1].partida.turnoActual=Jugador[1].id
        Jugador[1].partida.cantidadVivos = 4

def dar_cartas():
    with db_session:
        cartaj1 = Carta(id=1000,
                        template_carta = "Cita a ciegas",
                        jugador=Jugador[1],
                        partida=Partida[1])

        cartaj2 = Carta(id=1001,
                        template_carta = "Seduccion",
                        jugador=Jugador[1],
                        partida=Partida[1])
        carta3 = Carta(id=1002,
                        template_carta = "Lanzallamas",
                        jugador= None,
                        partida=Partida[1])
                        


async def test_cita_a_ciegas_exitosa(setup_db_before_test,cleanup_db_after_test):

    client = TestClient(app)

    asignar_pos()
    dar_cartas()


    async def fake_get_from_message_queue(id_partida, id_jugador):
        # Simular una respuesta que se esperaría
        response_data = {
            "data": 1001
        }
        return json.dumps(response_data)
    

    with client.websocket_connect(f'ws://localhost:8000/partidas/1/ws?idJugador=1') as ws:

        with patch("api.ws.manager.get_from_message_queue", new_callable=AsyncMock) as mock_get_from_message_queue:
            mock_get_from_message_queue.side_effect = fake_get_from_message_queue
            response = client.post(f'/cartas/jugar?id_carta=1000')
            assert response.status_code == 200
    with db_session:
        carta = Carta.get(id=1000)
        carta2 = Carta.get(id=1001)
        carta3 = Carta.get(id=1002)
        assert carta.jugador == None
        assert carta.descartada == True
        assert carta2.jugador == None
        assert carta2.descartada == False
        assert carta3.jugador == Jugador[1]
        assert carta3.descartada == False
        
